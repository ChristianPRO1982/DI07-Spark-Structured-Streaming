# Analyse de flux de données en temps réel avec Spark Structured Streaming

# Apache Kafka / Apache Spark

## Définitions

### on-premise

* `on-premise = où ça tourne`
* `on-premise ≠ cloud`

> 👉 on-premise = où ça tourne, et qui gère l’infrastructure (hardware, réseau, sécurité, déploiement).

### Apache Kafka

* `Kafka = log d’événements + découplage + relecture`
* `Kafka ≠ queue / trigger`
> une couche de streaming qui collecte/stocke/rejoue des événements, et permet à Spark (ou d’autres) de consommer en continu, de façon scalable et fiable

### Apache Spark

* `Spark = moteur distribué batch + streaming`
> Pandas-like API + SQL + exécution distribuée + streaming + tolérance aux pannes

*l’API n’est qu’une façade d’un moteur distribué.*

## A retenir

> Spark Structured Streaming fournit une API temps réel basée sur un modèle micro-batch, garantissant cohérence et tolérance aux pannes.

> Kafka organise les données par topics découpés en partitions, dans lesquelles les messages sont identifiés par des offsets, tandis que Spark consomme ces offsets via un consumer group en assurant la reprise grâce aux checkpoints.

## Quel problème Kafka résout que Spark seul ne résout pas bien ?

> Kafka apporte une couche de découplage et de persistance des flux qui permet à Spark de traiter des données en continu de manière fiable, scalable et tolérante aux pannes, en absorbant les pics de charge et en permettant la reprise du traitement à partir d’un offset précis.

> **Kafka garantit la disponibilité des événements, Spark garantit la cohérence du traitement.**

### développement

> Kafka permet de collecter et stocker des données brutes sous forme d’événements, sans transformation métier, en assurant leur persistance via des offsets.

⚠️ *Techniquement, Kafka peut faire un minimum de transformation (Kafka Streams, SMT).*

> Il découple les producteurs (capteurs IoT) des consommateurs (Spark), ce qui permet à Spark de consommer les données à son propre rythme, d’absorber des pics de charge, et de reprendre le traitement à partir d’un offset précis en cas d’erreur ou de redémarrage.

**En substance :**
* Kafka absorbe le flux brut
* Spark traite quand il peut, à son rythme
* Et surtout : on peut reprendre

**Exemples :**
* pics IoT → buffer Kafka (`anti-indigestion` 👍)
* bug applicatif → reprise à offset N (`ça, c’est du vécu`)

**Concepts :**
* Kafka ne fait pas de transformation métier, mais il fait bien :
  * de la distribution (partitions),
  * de la réplication (tolérance aux pannes).
  * `→ Ce n’est pas Spark, mais ce n’est pas “juste du stockage”.`
* Spark ne “*cible*” pas manuellement les offsets en pratique :
  * il les gère automatiquement via les consumer groups + checkpoints,
  * mais ton raisonnement reste correct conceptuellement.

# Workflow

**capteurs → Kafka → Spark**

# Vocabulaire clé (Kafka / Spark Streaming)
## Endpoint
> 👉 Un endpoint est un point d’accès réseau à un service.

Dans le contexte du brief :
* Kafka : host:port d’un broker (localhost:9092)
* Spark : endpoint Kafka pour lire/écrire des messages
* API : URL exposée par un service

> 👉 **À retenir :**
Un endpoint ne fait rien tout seul : c’est l’adresse où un service est joignable.

## Partition (Kafka)
> 👉 Une partition est une sous-partie ordonnée d’un topic Kafka.
* Un topic est découpé en N partitions
* Chaque partition est :
  * ordonnée (ordre garanti dans la partition),
  * append-only (on ajoute à la fin),
  * indépendante des autres partitions

**Pourquoi les partitions existent :**
* parallélisme (plusieurs consumers en même temps),
* montée en charge,
* répartition des données.

> 👉 **Règle clé :**
L’ordre n’est garanti que dans une partition, jamais entre partitions.

## Offset (Kafka)

> 👉 Un offset est un index numérique qui identifie la position d’un message dans une partition.

**Ce qu’est un offset :**
* un entier croissant (0, 1, 2, 3, …)
* unique par partition
* attribué automatiquement par Kafka
* lié à un message précis

**Ce qu’il n’est pas :**
* ❌ pas un timestamp
* ❌ pas global au topic
* ❌ pas une clé métier

**Organisation réelle :**
```
Topic
 ├─ Partition 0 : offset 0 → 1 → 2 → 3
 ├─ Partition 1 : offset 0 → 1 → 2
 └─ Partition 2 : offset 0 → 1
```

Chaque partition **a sa propre suite d’offsets**.

**Taille d’un offset :**
* conceptuellement : un nombre (int64)
* physiquement : stocké avec le message dans le log Kafka
* ce n’est pas le message, juste son index

## Consumer Group

> 👉 Un consumer group est un groupe logique de consommateurs qui se partagent les partitions d’un topic.

* 1 partition → 1 consumer max dans un group
* permet :
  * scalabilité,
  * tolérance aux pannes,
  * reprise automatique

Spark Structured Streaming **= un consumer group Kafka**.

## Commit d’offset

> 👉 Committer un offset = dire “j’ai traité jusqu’ici”.

* Kafka stocke les offsets consommés
* Spark décide quand committer :
  * après écriture réussie (Delta, sink, etc.)
  * via checkpoint

> 👉 Si Spark plante avant commit → les messages sont relus.

## Endpoint Kafka vs Topic

Petit piège classique :

* Endpoint = où se connecter (localhost:9092)
* Topic = quoi lire/écrire (iot_sensor_data)

## Mini-schéma mental (à garder en tête)
```
Capteur
  ↓
Kafka endpoint (broker)
  ↓
Topic
  ↓
Partitions
  ↓
Offsets
  ↓
Spark (consumer group + checkpoint)
```

# Concurrence

## 🔄 Outils de streaming / traitement de flux
> (Concurrents de Spark Structured Streaming)

| Outil                                 | Type                  | Points forts                      | Différence clé avec Spark |
| ------------------------------------- | --------------------- | --------------------------------- | ------------------------- |
| **Apache Spark Structured Streaming** | Micro-batch streaming | Robuste, SQL, batch + streaming   | Latence > Flink           |
| **Apache Flink**                      | Streaming natif       | Vrai streaming, event-time avancé | Plus complexe à opérer    |
| **Apache Beam**                       | SDK unifié            | Portabilité multi-engines         | Pas un moteur             |
| **Kafka Streams**                     | Lib Java              | Léger, intégré Kafka              | Pas distribué seul        |
| **ksqlDB**                            | Streaming SQL         | SQL temps réel                    | Cas d’usage limités       |
| **Apache Storm**                      | Streaming bas niveau  | Très faible latence               | Ancien, verbeux           |
| **Serverless streaming**              | Event-driven          | Scalabilité auto                  | Dépendance cloud          |

## 📨 Message brokers / Pub-Sub
> (Concurrents de Kafka)

| Outil                | Type              | Points forts                 | Différence clé avec Kafka    |
| -------------------- | ----------------- | ---------------------------- | ---------------------------- |
| **Apache Kafka**     | Log distribué     | Replay, débit massif         | Complexité infra             |
| **Apache Pulsar**    | Pub-Sub distribué | Multi-tenant, storage séparé | Moins répandu                |
| **RabbitMQ**         | Message Queue     | Routing avancé               | Pas conçu pour replay massif |
| **AWS Kinesis**      | Streaming managé  | Intégré AWS                  | Cloud only                   |
| **Google Pub/Sub**   | Pub-Sub managé    | Scalabilité auto             | Pas d’on-prem                |
| **Azure Event Hubs** | Event streaming   | Équivalent Kafka Azure       | Azure only                   |
| **Redis Streams**    | Streams mémoire   | Faible latence               | Rétention limitée            |

## 📦 Ingestion / orchestration / pipelines
> (Complément au streaming)

| Outil              | Rôle                  | Usage principal  |
| ------------------ | --------------------- | ---------------- |
| **Apache NiFi**    | Ingestion visuelle    | Routage de flux  |
| **Apache Airflow** | Orchestration batch   | ETL planifiés    |
| **Prefect**        | Orchestration moderne | Pipelines Python |
| **Dagster**        | Data orchestration    | Data-centric     |
| **dbt**            | Transformation SQL    | ELT analytique   |

## 📊 Analytique temps réel / stockage
> (Consommateurs de flux)

| Outil             | Type               | Usage                |
| ----------------- | ------------------ | -------------------- |
| **ClickHouse**    | OLAP               | Analytique rapide    |
| **Apache Druid**  | OLAP temps réel    | Dashboards           |
| **Apache Pinot**  | OLAP streaming     | Requêtes low-latency |
| **Elasticsearch** | Search + analytics | Logs & métriques     |
| **Materialize**   | Streaming SQL      | Vues temps réel      |


## 🧠 Aide mémoire

| Besoin                  | Outils typiques     |
| ----------------------- | ------------------- |
| *Message broker*        | Kafka, Pulsar       |
| *Streaming compute*     | Spark, Flink        |
| *Streaming SQL*         | ksqlDB, Materialize |
| *Orchestration*         | Airflow, Prefect    |
| *Analytique temps réel* | ClickHouse, Druid   |

```
               +--------------------+
               | Streaming compute  |
               | (traitement)       |
               | Spark / Flink /    |
               | Kafka Streams      |
               +---------+----------+
                         |
            +------------+---------------+
            |       Message brokers      |
            | Kafka / Pulsar / RabbitMQ  |
            | Kinesis / PubSub / Redis   |
            +------------+---------------+
                         |
         +---------------+--------------------+
         |  Stockage / Analytique temps réel  |
         | ClickHouse / Druid / Elasticsearch |
         +------------------------------------+

```


nouveau vocabulaire à mettre dans la fiche :
* Kafka produit (producer) / consomme (consumer)
* Kafka écrit dans le log d’un topic (append)
* Le consumer lit / relit des messages (read / replay)






Vocabulaire Kafka — minimum vital
Producer

👉 Un producer est une application qui envoie des messages à Kafka.

ex : capteur IoT, simulateur, application backend

rôle : écrire des événements dans un topic

👉 Kafka produit = des producers écrivent dans Kafka

Consumer

👉 Un consumer est une application qui lit des messages depuis Kafka.

ex : Spark Structured Streaming

rôle : lire les événements d’un topic

👉 Kafka consomme = des consumers lisent depuis Kafka

Topic

👉 Un topic est un canal logique de messages dans Kafka.

comparable à un flux nommé

ex : iot_sensor_data

👉 Un topic contient des partitions, pas des messages directement.

Log (Kafka log)

👉 Le log Kafka est une structure de stockage append-only.

les messages sont ajoutés à la fin

jamais modifiés ni supprimés immédiatement

organisés par partitions

👉 Quand tu dis :

Kafka écrit dans le log d’un topic

tu dis en réalité :

Kafka ajoute des messages à la fin du log de chaque partition du topic.

Append

👉 Append = ajouter à la fin.

Dans Kafka :

on ne fait que append

pas de update

pas de delete immédiat

C’est ce qui rend Kafka :

simple,

performant,

rejouable.

Read

👉 Read = lire des messages à partir d’un offset donné.

un consumer lit séquentiellement

respecte l’ordre de la partition

peut s’arrêter / reprendre

Replay

👉 Replay = relire des messages déjà lus.

Possible parce que :

Kafka conserve les messages

les offsets sont stockés séparément

le consumer peut repartir d’un offset plus ancien

👉 Très utile pour :

debug,

reprocessing,

nouveaux consommateurs.