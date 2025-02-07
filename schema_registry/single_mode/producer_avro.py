#https://github.com/confluentinc/confluent-kafka-python
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

value_schema_str = """
{"namespace": "student.avro",
 "type": "record",
 "doc": "This is an example of Avro.",
 "name": "Student",
 "fields": [
     {"name": "first_name", "type": ["null", "string"], "default": null, "doc": "First name of the student"},
     {"name": "last_name", "type": ["null", "string"], "default": null, "doc": "Last name of the student"},
     {"name": "class", "type": "int", "default": 1, "doc": "Class of the student"}
 ]
}
"""

value_schema = avro.loads(value_schema_str)
value = {"first_name": "Peter", "last_name": "Parker", "class": 1} # 전송할 메시지

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

avroProducer = AvroProducer({
    'bootstrap.servers': 'kafka_01.com,kafka_02.com,kafka_03.com',
    'on_delivery': delivery_report,
    'schema.registry.url': 'http://kafka_01.com:8081'
    }, default_value_schema=value_schema)

avroProducer.produce(topic='kafka-avro2', value=value)
avroProducer.flush()