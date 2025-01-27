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

### 확인
```commandline
curl -X GET http://kafka_01.com:8081/config
>>> 출력 값
{"compatibilityLevel":"FULL"}
```
