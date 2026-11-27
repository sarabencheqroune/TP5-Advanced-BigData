"""Exposer autrement : un fichier livré au partenaire, dès que Gold est publié."""
from datetime import datetime

from airflow.sdk import Asset, dag, task

gold_trajets = Asset("s3://lakehouse/gold/trajets_jour")


@dag(
    dag_id="export_trajets",
    schedule=[gold_trajets],               # planifié par la donnée, pas par l'heure
    start_date=datetime(2025, 12, 1),
    catchup=False,
    default_args={"owner": "data-eng", "retries": 1},
    tags=["tp5", "exposition"],
)
def export_trajets():

    @task
    def exporter_csv():
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        from airflow.providers.trino.hooks.trino import TrinoHook
        trino = TrinoHook()
        jour = trino.get_first("SELECT max(jour) FROM lake.gold.trajets_jour")[0]
        lignes = trino.get_records(f"""
            SELECT jour, region, ville, type_route, nb_trajets, km, litres
            FROM lake.gold.trajets_jour WHERE jour = DATE '{jour}' ORDER BY 2, 3, 4""")
        csv = "jour;region;ville;type_route;nb_trajets;km;litres\n" + "".join(
            ";".join(str(v) for v in l) + "\n" for l in lignes)
        cle = f"exports/trajets_jour/{jour}.csv"
        S3Hook(aws_conn_id="minio_default").load_string(
            csv, key=cle, bucket_name="lakehouse", replace=True)   # idempotent
        print(f"{len(lignes)} lignes livrées dans s3://lakehouse/{cle}")
        return cle                                                # XCom : un chemin

    exporter_csv()


export_trajets()
