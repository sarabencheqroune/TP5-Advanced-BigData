
FROM apache/spark:3.5.9-python3 AS sdk

USER root

RUN java -jar /opt/spark/jars/ivy-2.5.3.jar \
    -dependency software.amazon.awssdk s3-transfer-manager 2.24.6 -confs default \
    -retrieve "/sdk/[artifact]-[revision].[ext]"

FROM apache/hive:standalone-metastore-4.2.1

COPY --from=sdk /sdk/ /opt/hive/lib/

RUN cp /opt/hadoop/share/hadoop/tools/lib/hadoop-aws-3.4.1.jar /opt/hive/lib/

COPY mysql-connector-j-8.4.0.jar /opt/hive/lib/
