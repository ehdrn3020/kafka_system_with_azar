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
sh setting_aws/setup_server.sh ${EC2_NAME}
```

### scp keypair.pem
```commandline
scp -i setting_aws/keypair.pem setting_aws/keypair.pem ec2-user@111.222.333.444:~
```

### SSH 접속
```commandline
ssh -i setting_aws/keypair.pem ec2-user@111.222.333.444
```

### ansible key-gen
```commandline
ssh-agent bash
ssh-add keypair.pem
ssh-keygen
cat /home/ec2-user/.ssh/id_rsa.pub > /home/ec2-user/.ssh/authorized_keys
ssh zookeeper_02.com
```

### group_var host 관련 수정
```commandline
group_vars/all.yml 파일 호스트 수정
git push
배포할 서버에서 git pull
```

```commandline
cd /home/ec2-user/kafka_system_with_azar/ansible/
ansible-playbook -i inventory/hosts init.yml
ansible-playbook -i inventory/hosts zookeeper.yml
```

변수가 제대로 바인딩되는지 확인
ansible-playbook -i inventory zookeeper.yml --check --diff

zookeeper
zoo.cfg
myid

host를 각 서버마다 적용하는 법
ssh로 ansible 하는 법