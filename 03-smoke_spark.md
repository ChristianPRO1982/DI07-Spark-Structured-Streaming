# smoke

## état du projet
```bash
tree -I 'chris|jeux_de_donnees'
.
├── 01-commands_run_emitter.md
├── 02-smoke_spark.md
├── data
│   ├── checkpoints
│   └── delta
│       ├── bronze
│       ├── gold
│       └── silver
├── docker-compose version avec spark worker.yml
├── docker-compose.yml
├── jobs
│   └── delta_smoke_test.py
├── main.py
├── pyproject.toml
├── README.md
├── scripts
│   ├── iot_init_reset.py
│   └── iot_run_emitter.py
└── uv.lock

9 directories, 11 files
```

## bash
```bash
sudo chown -R $USER:$USER data
chmod -R u+rwX data

chmod -R a+rwX data
mkdir -p data/checkpoints/silver_sensor_data_kafka
chmod -R a+rwX data/checkpoints

chmod +x scripts/iot_reset_all.sh
./scripts/iot_reset_all.sh

docker compose up -d kafka kafka-ui
docker exec -it kafka kafka-topics --bootstrap-server kafka:9092 \
  --create --if-not-exists --topic iot_sensor --partitions 3 --replication-factor 1
docker exec -it kafka kafka-topics --bootstrap-server kafka:9092 --list

```

| Usage                   | Lecture Bronze |
| ----------------------- | -------------- |
| Pipeline temps réel     | ✅ stream       |
| Reprocessing / backfill | ✅ batch        |
| Debug / audit           | ✅ batch        |
| Contrôles qualité       | ✅ batch        |
| Exploration             | ✅ batch        |

Étape unique — Relancer un worker Spark (indispensable)
```
docker exec -d spark /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \
  spark://localhost:7077 \
  --cores 2 \
  --memory 2g \
  --webui-port 8082

```