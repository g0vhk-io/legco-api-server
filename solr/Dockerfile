FROM solr:6.5.1-alpine
USER root
USER solr
RUN /opt/docker-solr/scripts/precreate-core mycore
COPY solrconfig.xml /opt/solr/server/solr/mycores/mycore/conf/solrconfig.xml
RUN rm  /opt/solr/server/solr/mycores/mycore/conf/managed-schema
COPY schema.xml /opt/solr/server/solr/mycores/mycore/conf/schema.xml
ENTRYPOINT ["docker-entrypoint.sh", "solr-precreate", "mycore"]
