FROM python:3-slim

WORKDIR /python-consumer

RUN apt update && \
    apt upgrade -y && \
    python -m pip install kafka-python

COPY producer.py .

CMD ["python", "producer.py"]