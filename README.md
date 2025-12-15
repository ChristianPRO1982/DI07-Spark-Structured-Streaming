# Analyse de flux de données en temps réel avec Spark Structured Streaming

# Veille

## Définitions

### on-premise

* `on-premise = où ça tourne`
* `on-promise ≠ cloud`

> 👉 on-premise = où ça tourne, et qui gère l’infrastructure (hardware, réseau, sécurité, déploiement).

### Apache Spark

* `Spark = moteur distribué batch + streaming`
>Pandas-like API + SQL + exécution distribuée + streaming + tolérance aux pannes

*l’API n’est qu’une façade d’un moteur distribué.*

### Apache Kafka

* `Kafka = log d’événements + découplage + relecture`
* `Kafka ≠ queue / trigger`
> une couche de streaming qui collecte/stocke/rejoue des événements, et permet à Spark (ou d’autres) de consommer en continu, de façon scalable et fiable

## Quel problème Kafka résout que Spark seul ne résout pas bien ?

> Kafka apporte une couche de découplage et de persistance des flux qui permet à Spark de traiter des données en continu de manière fiable, scalable et tolérante aux pannes, en absorbant les pics de charge et en permettant la reprise du traitement à partir d’un offset précis.

> **Kafka garantit la disponibilité des événements, Spark garantit la cohérence du traitement.**

### développement

> Kafka permet de collecter et stocker des données brutes sous forme d’événements, sans transformation métier, en assurant leur persistance via des offsets.

> Il découple les producteurs (capteurs IoT) des consommateurs (Spark), ce qui permet à Spark de consommer les données à son propre rythme, d’absorber des pics de charge, et de reprendre le traitement à partir d’un offset précis en cas d’erreur ou de redémarrage.

**En substance :**
* Kafka absorbe le flux brut
* Spark traite quand il peut, à son rythme
* Et surtout : on peut reprendre

**Exemples :**
* pics IoT → buffer Kafka (`anti-indigestion` 👍)
* bug applicatif → reprise à offset N (`ça, c’est du vécu`, *et le jury adore*)

**Concepts :**
* Kafka ne fait pas de transformation métier, mais il fait bien :
  * de la distribution (partitions),
  * de la réplication (tolérance aux pannes).
  * `→ Ce n’est pas Spark, mais ce n’est pas “juste du stockage”.`
* Spark ne “*cible*” pas manuellement les offsets en pratique :
  * il les gère automatiquement via les consumer groups + checkpoints,
  * mais ton raisonnement reste correct conceptuellement.

## Workflow

**capteurs → Kafka → Spark**