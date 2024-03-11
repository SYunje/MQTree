# MQTree
MQTree: Secure OTA Protocol using MQTT and MerkleTree

## Install Mosquitto:
sudo apt-get update

sudo apt-get install mosquitto

sudo apt-get install mosquitto-clients

sudo systemctl start mosquitto


## Arduino CLI Setup
**Start by downloading and installing the latest version of Arduino CLI with the following command:**
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

**After installation, add Arduino CLI to your system's path to make it accessible from any terminal session**
cd bin/
sudo cp arduino-cli /usr/local/bin/

**Verify Installation : To ensure that Arduino CLI is installed correctly, run the following command:**
arduino-cli version

**Initialization : Initialize Arduino CLI to create a default configuration file. This step is essential for first-time setup:**
arduino-cli config init

**Install the necessary core to use common boards like Uno or Mega:**
arduino-cli core install arduino:avr

**this command updates the list of available boards and cores:**
arduino-cli core update-index

**For projects that require the megaAVR architecture (e.g., "Arduino Uno WiFi Rev2"), install the megaAVR core:**
arduino-cli core install arduino:megaavr

**arduino-cli core list**
Verify that the core installation was successful:

##Clone Project and Navigate

**Clone your project repository and navigate to the relevant directory:**
git clone https://github.com/SYunje/MQTree.git
cd ./MQTree/InVehicle

**Give execution permissions to your environment setup script and run it:**
chmod +x setup_environment.sh
./setup_environment.sh

**If you encounter errors, it might be due to Windows line endings. Correct this issue by running:**
sed -i 's/\r$//' setup_environment.sh

###Start
python3 MQTree.py
