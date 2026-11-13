# HBase 2.6.7 w trybie standalone (wbudowany ZooKeeper) + serwer Thrift dla Pythona (happybase)
FROM eclipse-temurin:17-jre-jammy

ARG HBASE_VERSION=2.6.7

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl procps \
 && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL "https://archive.apache.org/dist/hbase/${HBASE_VERSION}/hbase-${HBASE_VERSION}-bin.tar.gz" \
    | tar -xz -C /opt \
 && ln -s "/opt/hbase-${HBASE_VERSION}" /opt/hbase \
 && mkdir -p /data

ENV HBASE_HOME=/opt/hbase \
    PATH=/opt/hbase/bin:$PATH

COPY hbase-site.xml /opt/hbase/conf/hbase-site.xml

EXPOSE 16010 9090

# start HBase w tle, potem serwer Thrift na pierwszym planie (utrzymuje kontener)
CMD ["bash", "-c", "/opt/hbase/bin/start-hbase.sh && exec /opt/hbase/bin/hbase thrift start -p 9090"]
