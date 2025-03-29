from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

# Avro Value 스키마 정의
value_schema_str = """
{
  "namespace": "example.avro",
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "first_name", "type": "string"},
    {"name": "last_name", "type": "string"},
    {"name": "age", "type": "int"}
  ]
}
"""

value_schema = avro.loads(value_schema_str)

# 전송할 Avro 메시지 값
value = {
    "first_name": "Bruce",
    "last_name": "Wayne",
    "age": 35
}

# 메시지 전송 후 콜백
def delivery_report(err, msg):
    if err is not None:
        print(f"메시지 전송 실패: {err}")
    else:
        print(f"메시지 전송 완료: {msg.topic()} [{msg.partition()}]")

# Avro Producer 생성
producer = AvroProducer({
    'bootstrap.servers': 'kafka_01.com:9092,kafka_02.com:9092,kafka_03.com:9092',
    'schema.registry.url': 'http://kafka_01.com:8081'
}, default_value_schema=value_schema)

# 메시지 전송
producer.produce(topic='opensearch-sink', value=value, callback=delivery_report)
producer.flush()
