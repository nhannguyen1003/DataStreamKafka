FROM kafka-base:1.0

# Overwrite existing configuration files
COPY ./* /conf

RUN mkdir /var/lib/zookeeper && \
    echo "3" > /var/lib/zookeeper/myid