FROM solr:6.5.1-alpine
USER root
RUN mkdir -p /opt/solr/server/solr/mycores
RUN chown -R solr:solr/opt/solr/server/solr/mycores
USER solr
RUN /opt/docker-solr/scripts/precreate-core mycore
COPY solrconfig.xml /opt/solr/server/solr/mycores/mycore/conf/solrconfig.xml
RUN rm  /opt/solr/server/solr/mycores/mycore/conf/managed-schema
COPY schema.xml /opt/solr/server/solr/mycores/mycore/conf/schema.xml
ENTRYPOINT ["docker-entrypoint.sh", "solr-precreate", "mycore"]
