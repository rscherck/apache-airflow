FROM apache/airflow:latest
USER root
# INSTALL TOOLS

RUN apt-get update \
    && apt-get -y install libaio-dev \
    && apt-get install postgresql-client

RUN mkdir extra

COPY scripts/airflow/init.sh ./init.sh
COPY scripts/airflow/check_init.sql ./extra/check_init.sql
COPY scripts/airflow/set_init.sql ./extra/set_init.sql
RUN chown -R airflow ./extra/

USER airflow

ENTRYPOINT ["./init.sh"]