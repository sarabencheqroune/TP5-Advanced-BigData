"""Chaîne quotidienne des trajets : bronze, Silver (Spark), contrôle, Gold (dbt)."""
from datetime import datetime, timedelta
from airflow.sdk import Asset, dag, task
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from cosmos import (DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig,
                    RenderConfig)

DBT = "/opt/airflow/dbt/trajets_gold"
silver_trajets = Asset("s3://lakehouse/silver/trajets")
gold_trajets = Asset("s3://lakehouse/gold/trajets_jour")


def alerter(context):
    """Appelée quand le run échoue : une ligne dans le journal des alertes."""
    ti = context["task_instance"]
    with open("/opt/airflow/logs/alertes.log", "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M} ALERTE {ti.dag_id} : tâche "
                f"{ti.task_id} en échec pour la journée {context['ds']}\n")


@dag(
    dag_id="trajets_quotidien",
    schedule="@daily",                  # chaque nuit à minuit (UTC), pour la veille
    start_date=datetime(2025, 12, 1),
    catchup=False,
    max_active_runs=1,                        # deux runs écriraient les mêmes tables
    default_args={"owner": "data-eng", "retries": 1,
                  "retry_delay": timedelta(seconds=30),
                  "execution_timeout": timedelta(minutes=20)},
    on_failure_callback=alerter,
    tags=["tp5", "trajets"],
)
def trajets_quotidien():

    # 1. Attendre que le bronze du mois soit déposé dans MinIO, sans occuper de worker
    attendre_bronze = S3KeySensor(
        task_id="attendre_bronze",
        aws_conn_id="minio_default",
        bucket_name="bronze",
        bucket_key="trajets/mois={{ ds[:7] }}/*.parquet",
        wildcard_match=True,
        deferrable=True,
        poke_interval=30,
        timeout=120,
    )

    # 2. Le job Spark du TP5, sur le cluster du TP4, pour la journée du run
    silver = SparkSubmitOperator(
        task_id="silver_trajets",
        conn_id="spark_default",
        application="/opt/airflow/jobs/tp4-spark-1.0.jar",
        java_class="ma.uir.tp4.SilverTrajets",
        application_args=["{{ ds }}"],
        name="silver_trajets_{{ ds }}",
        total_executor_cores=2,
        executor_memory="1g",
        outlets=[silver_trajets],
    )

    # 3. Un contrôle qui bloque : trop de rejets, et Gold n'est pas recalculé
    @task
    def controle_qualite(ds=None):
        from airflow.providers.trino.hooks.trino import TrinoHook
        from airflow.sdk import Variable
        seuil = float(Variable.get("seuil_rejet", default="0.05"))
        valides, rejets = TrinoHook().get_first(f"""
            SELECT
              (SELECT count(*) FROM lake.silver.trajets WHERE jour = DATE '{ds}'),
              (SELECT count(*) FROM lake.silver.trajets_rejets WHERE jour = DATE '{ds}')
        """)
        taux = rejets / (valides + rejets)
        print(f"{ds} : {valides} valides, {rejets} rejets, taux {taux:.2%}")
        if taux > seuil:
            raise ValueError(f"taux de rejet {taux:.2%} au-dessus du seuil {seuil:.0%}")
        return rejets                          # XCom : un entier, pas des données

    # 4. Gold : le projet dbt, une tâche Airflow par modèle, seed, snapshot et test
    gold = DbtTaskGroup(
        group_id="dbt_gold",
        project_config=ProjectConfig(DBT),
        profile_config=ProfileConfig(profile_name="trajets_gold", target_name="prod",
                                     profiles_yml_filepath=f"{DBT}/profiles.yml"),
        execution_config=ExecutionConfig(
            dbt_executable_path="/opt/airflow/dbt-venv/bin/dbt"),
        # un test qui lit deux modèles (réconciliation) attend les deux
        render_config=RenderConfig(should_detach_multiple_parents_tests=True),
        operator_args={"vars": {"jour": "{{ ds }}"}},
        default_args={"retries": 0},
    )

    @task(outlets=[gold_trajets])
    def publier(ds=None):
        print(f"Gold publié pour {ds}")

    attendre_bronze >> silver >> controle_qualite() >> gold >> publier()


trajets_quotidien()
