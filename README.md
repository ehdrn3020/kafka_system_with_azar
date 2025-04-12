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


## Elastic Search
### opensearch 설치
```commandline
# kafka01 호스트에 싱글 노드로 설치
ansible-playbook -i inventory/hosts opensearch.yml
```

### opensearch 확인
```commandline
sudo systemctl status opensearch

# 클러스터 내 각 노드의 정보
curl -X GET "http://kafka_01.com:9200/_cat/nodes?v"
# 클러스터의 전체 상태(Health) 를 조회
curl -X GET "http://kafka_01.com:9200/_cluster/health?pretty"
```


## Connector Sink
### 커넥터 설치
```commandline
ansible-playbook -i inventory/hosts connector.yml
```

### 커넥터 확인
```commandline
# 실행 확인
sudo systemctl status kafka-connect
# 에러시 로그 확인
journalctl -u kafka-connect -f

# 클러스터에 현재 등록된 커넥터 목록을 확인
curl http://localhost:8083/connectors | python -m json.tool
# 커넥터 플러그인 확인
curl http://localhost:8083/connector-plugins | jq
[
  {
    "class": "io.aiven.kafka.connect.opensearch.OpensearchSinkConnector",
    "type": "sink",
    "version": "3.1.1"
  },
...]
```

### 토픽 생성
```commandline
# 생성
/usr/local/kafka/bin/kafka-topics.sh --create \
    --bootstrap-server kafka_01.com:9092,kafka_02.com:9092,kafka_03.com:9092 \
    --replication-factor 3 \
    --partitions 3 \
    --topic opensearch-sink
/usr/local/kafka/bin/kafka-topics.sh --list --bootstrap-server kafka_01.com:9092,kafka_02.com:9092,kafka_03.com:9092

# 확인
/usr/local/kafka/bin/kafka-topics.sh --list --bootstrap-server kafka_01.com:9092
```

### 컨넥터 등록
```commandline
# API로 opensearch sink connector 등록
curl -X POST http://kafka_01.com:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "opensearch-sink",
  "config": {
    "connector.class": "io.aiven.kafka.connect.opensearch.OpensearchSinkConnector",
    "tasks.max": "1",
    "topics": "opensearch-sink",
    "connection.url": "http://kafka_01.com:9200",

    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "http://kafka_01.com:8081",
    "value.converter.schema.registry.url": "http://kafka_01.com:8081",

    "schema.registry.url": "http://kafka_01.com:8081",
    "value.converter.schemas.enable": "false",
    "schema.ignore": "true",
    "type.name": "kafka-connect"
  }
}'

# 등록 확인
curl http://localhost:8083/connectors | python -m json.tool
...
[
    "opensearch-sink"
]

# 상태 확인
curl -X GET http://kafka_01.com:8083/connectors/opensearch-sink/status | jq

# 커넥터 삭제
curl -X DELETE http://localhost:8083/connectors/opensearch-sink
```


## 실행 예제

### kafka 데이터 전송 예제 코드
```commandline
# 가상환경에 필요한 모듈 설치 ( kafka_01.com 호스트에서 실행 )
cd /home/ec2-user/kafka_system_with_azar/schema_registry
python -m venv venv
source  venv/bin/activate
pip install confluent-kafka[avro]

# 메세지 전송 ( Schema Registry가 실행 중인 서버 )
python opensearch_sink_example.py
>>> Message delivered to kafka-avro2 [0]
```

### schema 등록확인
```commandline
# subjects list 확인
curl http://kafka_01.com:8081/subjects
>>> ["opensearch-sink-value"]

# subject 버전 확인
curl http://kafka_01.com:8081/subjects/opensearch-sink-value/versions
>>> [1]

```

### opensearch index store 확인
```commandline
curl -X GET "http://kafka_01.com:9200/_cat/indices?v"
curl -X GET "http://kafka_01.com:9200/opensearch-sink*/_search?pretty"
```