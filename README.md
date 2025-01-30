# kafka_system_with_azar
### 카프카 시스템 구성, 아자르 비즈니스 메트릭 생성 프로세스 참조
<img src="image/architecture_azar.png" width="600">

## AWS Server Setting
### .env 파일 생성
- setting_aws/env_example 참조하여 생성

### keypair.pem 키 생성
- ec2 접속을 위해 keypair.pem 키를 setting_aws 폴더에 생성
- 파일 권한 수정 : sudo chmod 600 setting_aws/keypair.pem

### EC2 서버 실행
```commandline
sh setting_aws/setup_server.sh server_1
sh setting_aws/setup_server.sh server_2
sh setting_aws/setup_server.sh server_3
```

### scp keypair.pem
```commandline
scp -i setting_aws/keypair.pem setting_aws/keypair.pem ec2-user@server_1_ip:~
```

### SSH 접속
```commandline
ssh -i setting_aws/keypair.pem ec2-user@server_1_ip
```

### ansible key-gen ( optional)
```commandline
ssh-agent bash
ssh-add keypair.pem 
ssh-keygen -t rsa -b 4096 -f /home/ec2-user/.ssh/id_rsa -N "" -q
cat /home/ec2-user/.ssh/id_rsa.pub >> /home/ec2-user/.ssh/authorized_keys
```

### group_var host 관련 수정
```commandline
inventory/hosts 파일의 ansible_host 변수 수정
git push
cd /home/ec2-user/kafka_system_with_azar/
git pull  ( server_1 에서 실행 )
```

## Zookeeper Setting
### zookeeper 설치
```commandline
cd /home/ec2-user/kafka_system_with_azar/ansible/
ansible-playbook -i inventory/hosts zookeeper.yml
```

### zookeeper 실행 확인
```commandline
systemctl status zookeeper
cat /data/zookeeper/myid
```

## Kafka Setting
### kafka 설치
```commandline
ansible-playbook -i inventory/hosts kafka.yml
```
### kafka 실행 확인
```commandline
# server_1에서 토픽생성 ( 자동토픽생성(Auto Topic Creation)으로 토픽 생성 생략가능 )
/usr/local/kafka/bin/kafka-topics.sh --bootstrap-server kafka_01.com:9092 --create --topic test-overview01 --partitions 1 --replication-factor 3

# server_2에서 consumer 실행 
/usr/local/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka_01.com:9092 --topic test-overview01

# server_1 producer로 메세지 전송
/usr/local/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka_02.com:9092 --topic test-overview01

# server_2에서 전송 된 메세지 확인
```


## Schema Registery
- server_1 에서 실행
- schema_registry/README.md 내용을 ansible 자동화

### 스키마 레지스트리 설치 및 실행
```commandline
# 설치, 설정파일 수정 및 실행
ansible-playbook -i inventory/hosts schema_registry.yml

# 데몬 확인
sudo systemctl status schema-registry

# 호환성 확인
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

### 스키마 적용 확인
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


