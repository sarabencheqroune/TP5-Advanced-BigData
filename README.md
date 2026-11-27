# TP5 : produit de données « Trajets quotidiens »

Chaîne quotidienne du lakehouse : **Airflow** orchestre Spark (Silver) et dbt (Gold), **Trino** lit et écrit les tables Iceberg (MinIO), **Superset** expose Gold, **Alloy + Loki + Grafana** surveillent l'exploitation.
Auteure : Sara Bencheqroune (119922), groupe Tp B, Advanced BigData, UIR.

## Consommateurs

| Qui | Ce qu'ils utilisent |
|---|---|
| Direction des opérations | Tableau de bord Superset « Trajets : suivi quotidien » |
| Responsables de région | Le même tableau, filtré par sécurité par ligne (ex. `resp_fes` : Fès-Meknès seulement) |
| Partenaire externe | CSV de la dernière journée, livré par le DAG `export_trajets` (`s3://lakehouse/exports/trajets_jour/AAAA-MM-JJ.csv`) |
| Équipe data | Supervision Superset (durée et échecs des runs) et tableau d'exploitation Grafana (journaux, alerte) |

## Définition des indicateurs

Table Gold `trajets_jour`, au grain **(jour, ville, type de route)**, avec contrat de schéma dbt.

| Indicateur | Définition |
|---|---|
| `nb_trajets` | Nombre de trajets du jour |
| `nb_voitures` | Nombre de voitures distinctes |
| `km` | Distance totale parcourue (km) |
| `litres` | Carburant consommé (L) |
| `conso_l100` | Consommation réelle : `SUM(litres) * 100 / SUM(km)` (pas la moyenne des `conso_l100`, qui pèserait pareil un jour de 10 et un jour de 10 000 trajets) |

Table `conso_modeles` : consommation réelle contre annoncée par modèle (`ecart_pct`). Définitions détaillées dans la documentation dbt.

## Fraîcheur promise

- Gold est recalculée **chaque nuit** par le DAG `trajets_quotidien` (données de la veille).
- Au-delà de **26 h** sans `publier` réussi, la nuit est considérée comme manquée (panneau « Fraîcheur de Gold » rouge dans Grafana).
- Source Silver : avertissement après 6 h, erreur après 24 h (`dbt source freshness`).

## Garde-fous qualité

- **Contrôle bloquant** : si le taux de rejet Silver dépasse la variable Airflow `seuil_rejet`, Gold n'est pas construite.
- **Tests dbt** : clés uniques, non nulls, relations (villes, voitures), valeurs acceptées, grain unique, test unitaire du calcul d'écart.
- **Réconciliation carburant** (sévérité `warn`) : litres des trajets contre factures du fournisseur, signalée au-delà de 1 % d'écart.
- Un `dbt build` en échec saute les modèles en aval : le tableau garde la dernière version valide.

## Propriétaire

- **Métier** : direction des opérations. **Exploitation** : équipe data.
- Le seuil de réconciliation reste à valider avec la comptabilité avant passage en `error`.

## Démarrage et interfaces

Depuis le dossier TP5 :

```
docker compose up -d
docker compose ps
docker compose stop      # arrêt ; les volumes sont conservés
```

| Service | URL |
|---|---|
| Airflow | http://localhost:8082 |
| Superset | http://localhost:8088 |
| Grafana | http://localhost:3000 |
| Trino | http://localhost:8080 |
| MinIO | http://localhost:9001 |
| Spark Master | http://localhost:8090 |
| Grafana Alloy | http://localhost:12345 |

## Structure du dépôt

| Dossier | Contenu |
|---|---|
| `docker-compose.yml`, `airflow/`, `superset/` | Plateforme et deux Dockerfile |
| `trino/` | Catalogue `lake` (Iceberg) |
| `dags/` | `trajets_quotidien`, `export_trajets` |
| `dbt/trajets_gold/` | Sources, staging, marts, seeds, tests, snapshot, exposure |
| `superset/tableaux/` | Tableaux de bord exportés |
| `alloy/`, `grafana/` | Collecte des journaux, tableau d'exploitation exporté, alerte |

## Environnement et limites

- Réalisé sur macOS avec Docker Desktop ; le parallélisme d'Airflow et la mémoire JVM de Trino ont été adaptés aux ressources disponibles.
- L'écart de réconciliation du 2 décembre (3,47 %) reste à expliquer.
- La RLS de Superset ne protège pas les accès directs à Trino : en production, la règle serait aussi posée dans le moteur ou le catalogue.
