# Commands run emitter

## Commands

### init

```bash
uv run python scripts/iot_init_reset.py \                                                                                                           
  --source-dir "./jeux_de_donnees/sensor_data" \
  --init-dir "./jeux_de_donnees/init" \      
  --landing-dir "./jeux_de_donnees/landing" \
  --pattern "sensor_data_*.json"
```

### run

```bash
uv run python scripts/iot_run_emitter.py \                                                                                                          
  --init-dir "./jeux_de_donnees/init" \
  --landing-dir "./jeux_de_donnees/landing" \
  --batch-min 1 \
  --batch-max 1 \
  --min-delay-s 1 \
  --max-delay-s 3
```

## Explications

Ces deux scripts permettent de simuler un flux de données IoT basé sur des fichiers, afin de reproduire le comportement d’un système de streaming sans message broker, comme première étape avant Kafka.

L’idée générale est de séparer clairement les rôles des dossiers :

* `sensor_data/` : **source immuable**, versionnée dans Git, contenant l’ensemble du dataset de référence
* `init/` : **zone de stock temporaire**, représentant les données encore non consommées
* `landing/` : **zone d’ingestion streaming**, surveillée par Spark Structured Streaming

### Script `iot_init_reset.py` — RESET du flux

Ce script permet de remettre le système dans un état initial propre, avant de relancer une simulation.

Fonctionnement :
* vide les dossiers `init/` et `landing/` (sans supprimer les `.gitkeep`)
* recopie tous les fichiers JSON depuis `sensor_data/` vers `init/`
* garantit que chaque run de streaming démarre depuis le même état

Objectif pédagogique :
* simuler un **redémarrage complet de pipeline**
* éviter toute ambiguïté liée à des fichiers résiduels ou à des anciens runs
* maîtriser explicitement l’état d’entrée du streaming

Ce script est **à lancer une seule fois avant un run**, ou chaque fois qu’on souhaite réinitialiser l’expérience.

### Script `iot_run_emitter.py` — Simulation du flux IoT

Ce script simule l’arrivée de données au fil du temps, comme le ferait un système IoT réel.

Fonctionnement :
* déplace progressivement des fichiers depuis `init/` vers `landing/`
* introduit des délais aléatoires entre chaque arrivée
* permet de déplacer un ou plusieurs fichiers par itération
* s’arrête automatiquement lorsque `init/` est vide

Dans la configuration fournie :
* un fichier est déplacé à la fois (`batch-min = batch-max = 1`)
* les délais sont compris entre 1 et 3 secondes
* le flux est volontairement lent et observable

Objectif pédagogique :
* reproduire le principe de **micro-batches**
* permettre à Spark Structured Streaming de détecter les nouveaux fichiers
* comprendre le rôle du checkpoint et de la notion de “fichier déjà traité”

### Pourquoi ce pattern est important

Cette approche permet de :
* comprendre le streaming **sans Kafka** avant d’introduire un message broker
* visualiser concrètement la différence entre **stock** et **flux**
* maîtriser l’ordre, le rythme et la reproductibilité des données
* préparer naturellement la transition vers Kafka (topics ≈ landing, offsets ≈ état traité)
