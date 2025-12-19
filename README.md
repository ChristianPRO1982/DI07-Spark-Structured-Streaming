# Analyse de flux de données en temps réel avec Spark Structured Streaming

## Veille KAFKA + SPARK STREAMING

[Veille (doc MD sur GitHub)](https://github.com/ChristianPRO1982/DI07-Spark-Structured-Streaming/blob/main/01-veille-kafka-spark.md)

## préparation de l'environnement

```bash

```

## lancer docker compose
```bash
docker-compose up -d
```
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## pour faire fonctionner KAFKA/SILVER (2.2)

### terminal #1
> Préparer les droits + dossiers (host)
```bash
mkdir -p data/checkpoints/silver_sensor_data_kafka data/delta/silver
chmod -R a+rwX data
```

> lancer un job dans un premier terminal
```bash
docker exec -it spark /opt/spark/bin/spark-submit \
  --master spark://localhost:7077 \
  --packages io.delta:delta-spark_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  --conf "spark.jars.ivy=/tmp/ivy2" \
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" \
  /opt/spark/work-dir/jobs/silver_from_kafka_streaming.py
```
**Note :** on voit les jobs avancer dans l'interface de Spark il ne faut pas qu'il soit au statut "completed"

### terminal #2
> lancer des messages fictifs dans un deuxième terminal :
```bash
docker exec -it kafka kafka-console-producer \
  --bootstrap-server kafka:9092 \
  --topic iot_sensor
```
```json
docker exec -it kafka kafka-console-producer \
{"sensor_id":"S-701","temperature":22.5,"humidity":39.9,"event_time":"2025-12-19 10:00:00"}
{"sensor_id":"S-702","temperature":30.8,"humidity":29.1,"event_time":"2025-12-19 10:00:02"}
```