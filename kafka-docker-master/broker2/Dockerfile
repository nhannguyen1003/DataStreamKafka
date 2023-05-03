FROM kafka-base:1.0

# Overwrite existing configuration files
COPY ./* /conf

RUN mkdir /var/lib/zookeeper && \
    echo "2" > /var/lib/zookeeper/myid