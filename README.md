# TP5 – Orchestration, transformation et supervision du Lakehouse

## Objectif

Ce TP consiste à automatiser, transformer et superviser un pipeline de données Lakehouse, en assurant la qualité des données et le suivi des traitements.

## Technologies utilisées

- **Docker Compose** : déploiement des services
- **Apache Spark** : traitement des données Bronze et Silver
- **MinIO et Apache Iceberg** : stockage et gestion des tables
- **Trino** : interrogation des données
- **dbt** : transformation des données vers la couche Gold
- **Apache Airflow** : orchestration et automatisation du pipeline
- **Apache Superset** : visualisation des indicateurs métier
- **Grafana, Loki et Alloy** : supervision, centralisation des logs et alertes
- **PostgreSQL et MySQL** : gestion des métadonnées

## Démarrage

Depuis le dossier TP5 :

```bash
docker compose up -d
docker compose ps
```

## Interfaces

| Service | URL |
|---|---|
| Airflow | http://localhost:8082 |
| Superset | http://localhost:8088 |
| Grafana | http://localhost:3000 |
| Trino | http://localhost:8080 |
| MinIO | http://localhost:9001 |
| Spark Master | http://localhost:8090 |
| Grafana Alloy | http://localhost:12345 |

## Fonctionnalités

- Automatisation du pipeline Bronze → Silver → Gold
- Contrôle de la qualité des données
- Gestion des exécutions historiques (Backfill)
- Publication et export des données
- Tableaux de bord métier et opérationnels
- Centralisation des journaux et déclenchement des alertes

## Environnement

TP réalisé sur macOS avec Docker Desktop. Le parallélisme d'Airflow et la mémoire JVM de Trino ont été adaptés aux ressources disponibles.

## Arrêt des services

```bash
docker compose stop
```

Les volumes sont conservés afin de garantir la persistance des données.
