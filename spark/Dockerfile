
FROM apache/spark:3.5.9-python3

ARG MAVEN=https://repo1.maven.org/maven2

ADD --chown=spark:spark ${MAVEN}/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar /opt/spark/jars/

ADD --chown=spark:spark ${MAVEN}/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar /opt/spark/jars/

ADD --chown=spark:spark ${MAVEN}/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar /opt/spark/jars/

WORKDIR /opt/tp3
