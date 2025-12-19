# KAFKA + SPARK

## commands

### 0) lancer un worker (si pas auto)
```
docker exec -d spark /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \
  spark://localhost:7077 \
  --cores 2 \
  --memory 2g \
  --webui-port 8082
```

### 1) Lance le job debug console (1 seul terminal)
```
docker exec -it spark /opt/spark/bin/spark-submit \
  --master spark://localhost:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  --conf "spark.jars.ivy=/tmp/ivy2" \
  /opt/spark/work-dir/jobs/kafka_debug_console.py

```

### 2) Envoie 1 message dans Kafka (autre terminal)
```
docker exec -it kafka kafka-console-producer \
  --bootstrap-server kafka:9092 \
  --topic iot_sensor
```

Puis colle :
```
{"sensor_id":"S-999","temperature":25.0,"humidity":40.0,"event_time":"2025-12-17 16:45:00"}

```