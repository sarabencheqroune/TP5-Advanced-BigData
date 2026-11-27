FROM apache/airflow:3.3.2

COPY --from=tp3-spark:3.5.9 /opt/java/openjdk /opt/java/openjdk
COPY --from=tp3-spark:3.5.9 --chown=airflow:root /opt/spark /opt/spark

ENV JAVA_HOME=/opt/java/openjdk \
    SPARK_HOME=/opt/spark \
    PATH="/opt/java/openjdk/bin:/opt/spark/bin:${PATH}:/opt/airflow/dbt-venv/bin"

RUN pip install --no-cache-dir "apache-airflow==3.3.2" \
    apache-airflow-providers-apache-spark==6.3.5 \
    apache-airflow-providers-trino==7.0.0 \
    astronomer-cosmos==1.16.0 keyring

RUN python -m venv /opt/airflow/dbt-venv \
 && /opt/airflow/dbt-venv/bin/pip install --no-cache-dir \
    dbt-core==1.12.7 dbt-trino==1.12.0 keyring
