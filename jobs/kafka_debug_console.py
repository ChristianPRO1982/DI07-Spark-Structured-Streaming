from __future__ import annotations

from pyspark.sql import SparkSession


def build_spark(app_name: str) -> SparkSession:
    """Create a SparkSession for reading Kafka in streaming mode."""
    return SparkSession.builder.appName(app_name).getOrCreate()


def main() -> None:
    spark = build_spark("DI07-Kafka-Debug-Console")

    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "iot_sensor")
        .option("startingOffsets", "earliest")
        .load()
    )

    out = df.selectExpr(
        "topic",
        "partition",
        "offset",
        "CAST(key AS STRING) AS key_str",
        "CAST(value AS STRING) AS value_str",
        "timestamp",
    )

    query = (
        out.writeStream.format("console")
        .outputMode("append")
        .option("truncate", "false")
        .option("checkpointLocation", "/opt/spark/work-dir/data/checkpoints/kafka_debug_console")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
