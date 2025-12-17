from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T


@dataclass(frozen=True)
class DeltaPaths:
    base_path: str


def build_spark(app_name: str) -> SparkSession:
    """Create a SparkSession configured for Delta Lake."""
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )


def build_sample_df(spark: SparkSession):
    """Create a small deterministic DataFrame for a Delta write/read smoke test."""
    rows: List[Tuple[str, float, float, str]] = [
        ("S-001", 21.5, 45.2, "2025-12-17 09:00:00"),
        ("S-002", 27.1, 38.7, "2025-12-17 09:00:02"),
        ("S-001", 22.0, 44.9, "2025-12-17 09:00:05"),
    ]

    df = spark.createDataFrame(rows, ["sensor_id", "temperature", "humidity", "event_time"])

    return (
        df.withColumn("event_time", F.to_timestamp("event_time", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("day", F.to_date("event_time"))
    )


def write_delta(df, output_path: str) -> None:
    """Write a DataFrame as a Delta table."""
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .save(output_path)
    )


def read_delta(spark: SparkSession, input_path: str):
    """Read a Delta table as a DataFrame."""
    return spark.read.format("delta").load(input_path)


def main() -> None:
    spark = build_spark("DI07-Delta-Smoke-Test")

    paths = DeltaPaths(base_path="/opt/spark/work-dir/data/delta/bronze/delta_smoke_test")
    df = build_sample_df(spark)

    write_delta(df, paths.base_path)
    out_df = read_delta(spark, paths.base_path)

    out_df.orderBy("event_time").show(truncate=False)
    print(f"OK: delta table written + read at: {paths.base_path}")

    spark.stop()


if __name__ == "__main__":
    main()
