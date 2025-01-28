# Schema Registry
### 설치
```commandline
cd ~
sudo wget http://packages.confluent.io/archive/6.1/confluent-community-6.1.0.tar.gz -O /opt/confluent-community-6.1.0.tar.gz
sudo tar zxf /opt/confluent-community-6.1.0.tar.gz -C /usr/local/
sudo ln -s /usr/local/confluent-6.1.0 /usr/local/confluent
```

### 설정
```commandline
vi /usr/local/confluent/etc/schema-registry/schema-registry.properties
프로젝트의 schema_registry/schema-registry.properties 참조하여 업데이트
```

### 실행
```commandline
sudo vi /etc/systemd/system/schema-registry.service
프로젝트의 schema_registry/schema-registry.properties 참조하여 업데이트
sudo systemctl daemon-reload
sudo systemctl start schema-registry
sudo systemctl status schema-registry
```

### 호환성 확인
```commandline
curl -X GET http://kafka_01.com:8081/config
>>> 출력 값
{"compatibilityLevel":"FULL"}
```

### python 파일을 통해 메세지 전송
```commandline
# 가상환경에 필요한 모듈 설치
cd /home/ec2-user/kafka_system_with_azar/schema_registry
python -m venv venv
source  venv/bin/activate
pip install confluent-kafka[avro]

# 모듈 설치시 호환성
- 해당 예제는 confluent-kafka==2.8.0 설치하여 librdkafka 1.8.2 이상의 버전이 필요합니다.
- confluent-kafka Python라이브러리는 librdkafka를 래핑(wrapping)한 라이브러리입니다.
- librdkafka는 Apache Kafka 브로커와 통신하는 역할을 하며, Kafka 브로커의 버전과 호환성이 있습니다.
- python3.9 이상에서는 librdkafka 1.x.x 이상이 설치되지만, python3.7은 librdkafka 0.11.x 버전이 설치됩니다.
- librdkafka 0.11.x 버전은 confluent-kafka 1.0.0 이하와 호환되므로, 아래 py파일의 코드가 실행되지 않을 수 있습니다. 

# 메세지 전송 ( Schema Registry가 실행 중인 서버 )
python producer_avro.py
>>> Message delivered to kafka-avro2 [0]

# 메세지 확인
python consumer_avro.py
>>> {'name': 'Peter', 'class': 1}
```

### 스키마 전용 확인
```commandline
curl http://kafka_01.com:8081/schemas | python -m json.tool
>>>
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   375  100   375    0     0  16769      0 --:--:-- --:--:-- --:--:-- 17045
[
    {
        "subject": "kafka-avro2-value",
        "version": 1,
        "id": 1,
        "schema": "{
            \"type\":\"record\",
            \"name\":\"Student\",
            \"namespace\":\"student.avro\",
            \"doc\":\"This is an example of Avro.\",
            \"fields\":[
                {\"name\":\"name\",\"type\":[\"null\",\"string\"],\"doc\":\"Name of the student\",\"default\":null},
                {\"name\":\"class\",\"type\":\"int\",\"doc\":\"Class of the student\",\"default\":1}
            ]
        }"
    }
]
```

