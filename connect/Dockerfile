FROM confluentinc/cp-kafka-connect:7.7.1

USER root

ARG DEBEZIUM_VERSION=2.7.3.Final
ARG PLUGIN_DIR=/usr/share/confluent-hub-components

RUN mkdir -p "$PLUGIN_DIR" \
    && curl -fsSL \
        "https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/${DEBEZIUM_VERSION}/debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin.tar.gz" \
        | tar -xzf - -C "$PLUGIN_DIR" \
    && confluent-hub install --no-prompt confluentinc/kafka-connect-elasticsearch:14.1.2

USER appuser
