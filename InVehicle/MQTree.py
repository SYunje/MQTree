import paho.mqtt.client as mqtt
import hashlib
import json
import requests
import re
import os
import time
import subprocess
import shutil

class BinaryHashTree:
    def __init__(self):
        self.root_hash = None

    def compute_file_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.digest()

    def build_tree(self, directory_path):
        ino_files = self.get_ino_files(directory_path)
        data = [self.compute_file_hash(file) for file in ino_files]
        self.root_hash = self.build_binary_hash_tree(data)

    def get_ino_files(self, directory_path):
        ino_files = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(".ino"):
                    ino_files.append(os.path.join(root, file))
        return ino_files

    def build_binary_hash_tree(self, data):
        if len(data) == 0:
            return None
        if len(data) == 1:
            return data[0]
        mid = len(data) // 2
        left_data = data[:mid]
        right_data = data[mid:]
        left_hash = self.build_binary_hash_tree(left_data)
        right_hash = self.build_binary_hash_tree(right_data)
        return hashlib.sha256(left_hash + right_hash).digest()

    def get_root_hash(self):
        return self.root_hash



# MQTT 클라이언트 콜백 함수 설정
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(subTopic)  # 토픽 구독

message_count = 0


def get_next_firmware_filename(directory):
    # 디렉토리 내의 모든 파일 목록을 가져옵니다.
    files = os.listdir(directory)
    # 파일 이름에서 숫자를 추출하기 위한 정규 표현식
    pattern = re.compile(r'^(\d+). SecureOTA.ino$')
    max_number = 0
    for filename in files:
        match = pattern.match(filename)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
    # 다음 파일 번호를 반환합니다.
    return f"{max_number + 1}.SecureOTA.ino"


def compute_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


#여기가 Main 부분임
def on_message(client, userdata, msg):
    global message_count, root_hash  # root_hash를 전역 변수로 사용
    payload = json.loads(msg.payload)  # MQTT로부터 받은 메시지 json 페이로드
    firmwareURL = payload['URL']
    firmwareLocation = f"http://{brokerIp}{firmwareURL}"
    print(payload)
    print('=======================================================')
    print()

    # 모터 버전을 비교하여 업데이트가 필요한 경우
    if float(payload['Version']) > moterVersion:
        # 사용자에게 업데이트 진행 여부를 묻기.
        user_input = input("New firmware version available. Do you want to update? (Y/N): ")
        if user_input.lower() in ["y", "yes"]:
            print("Proceeding with firmware update...")
            time.sleep(1)
            # 펌웨어 업데이트 로직
            try:
                response = requests.get(firmwareLocation)
                response.raise_for_status()  # 오류 발생 시 예외 발생

                # 다운로드된 내용을 파일에 저장
                firmwareDirectory = './Firmware/'
                firmwareFilename = get_next_firmware_filename(firmwareDirectory)
                firmwarePath = os.path.join(firmwareDirectory, firmwareFilename)
                with open(firmwarePath, 'wb') as file:
                    file.write(response.content)

                time.sleep(1)
                print(f"Firmware downloaded and saved to {firmwarePath}")


                # 파일이 성공적으로 저장된 후에 해시 계산
                downloaded_file_hash = compute_file_hash(firmwarePath)

                if payload["FileHash"] == downloaded_file_hash:
                    time.sleep(1)
                    print("FileHash match. Firmware is verified.")
                    print('=======================================================')
                    print()


                else:
                    print("FileHash do not match. Firmware might be tampered or updated.")

                with open(firmwarePath, 'wb') as file:
                    file.write(response.content)

                time.sleep(1)
                print(f"Firmware downloaded and saved to {firmwarePath}")
                print("저장하고 루트해시 계산")
                print('=======================================================')
                print()

                # 이진 해시 트리 재구축 및 루트 해시 값 계산
                bht = BinaryHashTree()
                bht.build_tree('./Firmware')
                root_hash = bht.get_root_hash().hex()
                time.sleep(1)
                print("New Root Hash:", root_hash)
                print('=======================================================')
                print()

                # 루트 해시와 받은 해시를 비교
                if payload["RootHash"] == root_hash:
                    time.sleep(1)
                    print("RootHashes match. Firmware is verified.")
                    print('=======================================================')
                    print()
                    ##여기에 이제 아두이노 cli만 적용하면 된다.##
                    # 연결된 보드 리스트를 가져오는 명령 실행

                    target_directory = '/1.SecureOTA/'
                    target_path = os.path.join(target_directory, os.path.basename(firmwarePath))
                    shutil.move(firmwarePath, target_path)

                    print(f"File moved to {target_path}")


                    result = subprocess.run(['arduino-cli', 'board', 'list'], stdout=subprocess.PIPE, text=True)
                    board_list_output = result.stdout

                    # "Arduino"로 시작하는 보드 이름을 가진 포트를 찾기 위한 정규 표현식
                    pattern = re.compile(r'(\/dev\/tty[A-Za-z0-9]+)\s+.*Arduino.*')

                    # 정규 표현식을 사용하여 출력된 결과에서 원하는 포트 찾기
                    matches = pattern.findall(board_list_output)
                    if matches:
                        # 첫 번째 일치하는 포트 사용
                        port = matches[0]
                        print(f"Found Arduino board at port: {port}")
                    else:
                        print("No Arduino board found.")
                        exit(1)  # Arduino 보드를 찾지 못한 경우 스크립트 종료

                    # FQBN 설정: Arduino Uno WiFi Rev2의 경우
                    fqbn = "arduino:megaavr:uno2018"

                    # 업로드할 스케치 파일 경로
                    sketch_path = "./Firmware/1.SecureOTA.ino"

                    # 컴파일 명령 실행
                    compile_command = ['arduino-cli', 'compile', '--fqbn', fqbn, sketch_path]
                    subprocess.run(compile_command)

                    # 업로드 명령 실행
                    upload_command = ['arduino-cli', 'upload', '-p', port, '--fqbn', fqbn, sketch_path]
                    subprocess.run(upload_command)


                else:
                    print("RootHashes do not match. Firmware might be tampered or updated.")
            except requests.RequestException as e:
                print(f"Error downloading the firmware: {e}")

        else:
            print("Firmware update canceled.")
            return
    else:
        print("No new firmware update required.")



# MQTT 클라이언트 인스턴스 생성 및 설정
userId = "kusecar"
userPw = "kusetest"

client = mqtt.Client()
client.username_pw_set(userId, userPw)
client.on_connect = on_connect
client.on_message = on_message

# MQTT 브로커에 연결
subTopic = "/MoSE/mqtt"
brokerIp = 'kuse.kookmin.ac.kr'
port = 3000
client.connect(brokerIp, port, 60)

global moterVersion
moterVersion = 0.7


global lightVersion
lightVersion = 0.7

# 네트워크 루프 시작
client.loop_forever()

