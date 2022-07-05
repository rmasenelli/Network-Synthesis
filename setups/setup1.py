import os

if os.geteuid() != 0:
    print("Please run this script as sudo! (sudo python3 setups/setup2.py)")
    exit(-1)

# python
os.system('sudo apt-get install python3-pip -y')

# prettytable
os.system('python3 -m pip install -U prettytable')

# pyyaml
os.system('sudo pip3 install pyyaml')
os.system('sudo pip3 install --upgrade pyyaml')

# faucet
os.system('sudo apt-get install curl gnupg apt-transport-https lsb-release -y')
os.system('''echo "deb https://packagecloud.io/faucetsdn/faucet/$(lsb_release -si | awk '{print tolower($0)}')/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/faucet.list''')
os.system('sudo curl -1sLf https://packagecloud.io/faucetsdn/faucet/gpgkey -o /etc/apt/trusted.gpg.d/faucet.asc')
os.system('sudo apt-get update')
os.system('sudo apt-get install faucet-all-in-one -y')

# open vswitch
os.system('sudo apt-get install apt-transport-https curl lsb-release -y')
os.system('sudo curl -1sLf https://dl.cloudsmith.io/public/wand/openvswitch/gpg.2E801E8CCE233F26.key -o /etc/apt/trusted.gpg.d/wand-openvswitch.asc')
os.system('curl -1sLf "https://dl.cloudsmith.io/public/wand/openvswitch/config.deb.txt?distro=$(lsb_release -is)&codename=$(lsb_release -sc)" | sudo tee /etc/apt/sources.list.d/wand-openvswitch.list')
os.system('sudo apt-get update')
os.system('sudo apt-get install openvswitch-switch -y')

# bird
os.system('sudo apt-get install bird')
os.system('sudo systemctl stop bird')
os.system('sudo systemctl stop bird6')