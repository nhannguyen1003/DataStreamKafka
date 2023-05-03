FROM openjdk:11-jdk

RUN apt update && \
    apt upgrade -y && \
    apt install -y curl 

RUN curl -O https://dlcdn.apache.org/kafka/3.1.0/kafka_2.13-3.1.0.tgz && \
    tar -xzf kafka_2.13-3.1.0.tgz

COPY conf/* /conf/

COPY kafka-runner.sh .
ENTRYPOINT [ "./kafka-runner.sh" ]
