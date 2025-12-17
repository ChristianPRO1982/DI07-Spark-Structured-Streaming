from __future__ import annotations

from pyspark.sql import SparkSession


def build_spark(app_name: str) -> SparkSession:
    """Create a SparkSession configured for Delta Lake."""
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )


def main() -> None:
    spark = build_spark("DI07-Read-Bronze-Batch")

    bronze_path = "/opt/spark/work-dir/data/delta/bronze/sensor_data"
    df = spark.read.format("delta").load(bronze_path)

    df.printSchema()
    df.orderBy("event_time").show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
