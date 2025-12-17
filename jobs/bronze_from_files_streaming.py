from __future__ import annotations

from dataclasses import dataclass

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T


@dataclass(frozen=True)
class PipelinePaths:
    landing_path: str
    bronze_path: str
    checkpoint_path: str


def build_spark(app_name: str) -> SparkSession:
    """Create a SparkSession configured for Delta Lake."""
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )


def get_schema() -> T.StructType:
    """Return the expected JSON schema for IoT events."""
    return T.StructType(
        [
            T.StructField("sensor_id", T.StringType(), True),
            T.StructField("temperature", T.DoubleType(), True),
            T.StructField("humidity", T.DoubleType(), True),
            T.StructField("event_time", T.StringType(), True),
        ]
    )


def read_stream(spark: SparkSession, landing_path: str):
    """Read JSON files as a streaming source."""
    return (
        spark.readStream.format("json")
        .schema(get_schema())
        .option("maxFilesPerTrigger", 1)
        .load(landing_path)
    )


def transform(df):
    """Apply minimal Bronze transformations: parsing, filtering, and derived columns."""
    return (
        df.withColumn("event_time", F.to_timestamp("event_time", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("ingest_time", F.current_timestamp())
        .withColumn("day", F.to_date("event_time"))
        .filter(F.col("sensor_id").isNotNull())
        .filter(F.col("event_time").isNotNull())
    )


def write_bronze(df, bronze_path: str, checkpoint_path: str):
    """Write the streaming DataFrame to Delta Bronze with checkpointing."""
    return (
        df.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint_path)
        .start(bronze_path)
    )


def main() -> None:
    spark = build_spark("DI07-Bronze-From-Files-Streaming")

    paths = PipelinePaths(
        landing_path="/opt/spark/work-dir/data/landing",
        bronze_path="/opt/spark/work-dir/data/delta/bronze/sensor_data",
        checkpoint_path="/opt/spark/work-dir/data/checkpoints/bronze_sensor_data",
    )

    raw_df = read_stream(spark, paths.landing_path)
    bronze_df = transform(raw_df)

    query = write_bronze(bronze_df, paths.bronze_path, paths.checkpoint_path)
    query.awaitTermination()


if __name__ == "__main__":
    main()
