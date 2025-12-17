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

## donner les droits pour `data/`
```bash
sudo chown -R $USER:$USER data
chmod -R u+rwX data
```