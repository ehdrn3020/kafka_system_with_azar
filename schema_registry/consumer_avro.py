from confluent_kafka import avro
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

# Define Avro schema
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

schema_registry_urls = [
    'http://kafka_01.com:8081',
    'http://kafka_02.com:8081',
    'http://kafka_03.com:8081'
]

value_schema = avro.loads(value_schema_str)

for url in schema_registry_urls:
    try:
        c = AvroConsumer(
            {
                'bootstrap.servers':'kafka_01.com,kafka_02.com,kafka_03.com',
                'group.id':'python-groupid01',
                'auto.offset.reset':'earliest',
                'schema.registry.url':url
            }, reader_value_schema=value_schema
        )

        c.subscribe(['kafka-avro2'])
        # Successfully connected
        print(f"Connected to Schema Registry at {url}")
        break

    except Exception as e:
        print(f"Failed to connect to Schema Registry at {url}, Error : {e}")

# Consume messages
while True:
    try:
        msg = c.poll(10)
    except SerializerError as e:
        print(f"Message deserialization failed for {msg}: {e}")
        break

    if msg is None:
        continue

    if msg.error():
        print(f"AvroConsumer error: {msg.error()}")
        continue

    print(msg.value())

c.close()
