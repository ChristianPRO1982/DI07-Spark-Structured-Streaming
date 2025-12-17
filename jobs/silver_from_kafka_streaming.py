from __future__ import annotations

from dataclasses import dataclass

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T


@dataclass(frozen=True)
class PipelinePaths:
    silver_path: str
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


def read_kafka_stream(spark: SparkSession):
    """Read Kafka topic as a streaming source."""
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "iot_sensor")
        .option("startingOffsets", "earliest")
        .load()
    )


def parse_and_transform(kafka_df):
    """Parse Kafka value as JSON and apply basic Silver transformations."""
    json_df = kafka_df.selectExpr("CAST(value AS STRING) AS json_str")

    parsed = json_df.select(F.from_json(F.col("json_str"), get_schema()).alias("data")).select("data.*")

    return (
        parsed.withColumn("event_time", F.to_timestamp("event_time", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("ingest_time", F.current_timestamp())
        .withColumn("day", F.to_date("event_time"))
        .filter(F.col("sensor_id").isNotNull())
        .filter(F.col("event_time").isNotNull())
    )


def write_silver(df, silver_path: str, checkpoint_path: str):
    """Write the streaming DataFrame to Delta Silver with checkpointing."""
    return (
        df.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", checkpoint_path)
        .start(silver_path)
    )


def main() -> None:
    spark = build_spark("DI07-Silver-From-Kafka-Streaming")

    paths = PipelinePaths(
        silver_path="/opt/spark/work-dir/data/delta/silver/sensor_data",
        checkpoint_path="/opt/spark/work-dir/data/checkpoints/silver_sensor_data_kafka",
    )

    kafka_df = read_kafka_stream(spark)
    silver_df = parse_and_transform(kafka_df)

    query = write_silver(silver_df, paths.silver_path, paths.checkpoint_path)
    query.awaitTermination()


if __name__ == "__main__":
    main()
