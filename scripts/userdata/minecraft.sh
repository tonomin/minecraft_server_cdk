#!/bin/bash

sudo dnf -y update
sudo dnf -y install wget java-17-openjdk-headless-1:17.0.5.0.8-2.el8_6.x86_64
sudo useradd minecraft -M

mkdir /etc/minecraft/
cd /etc/minecraft
sudo wget https://piston-data.mojang.com/v1/objects/c9df48efed58511cdd0213c56b9013a7b5c9ac1f/server.jar
sudo java -Xmx1024M -jar server.jar nogui

sudo sed -i -e "s/false/true/" /etc/minecraft/eula.txt

touch boot.sh
echo '#!/bin/bash' >> /etc/minecraft/boot.sh
echo 'java -Xms$XMS_SIZE -Xmx$XMX_SIZE -jar /etc/minecraft/server.jar nogui' >> /etc/minecraft/boot.sh
chmod +x /etc/minecraft/boot.sh

touch environments
echo 'XMS_SIZE=1024M' >> /etc/minecraft/environments
echo 'XMX_SIZE=1024M' >> /etc/minecraft/environments

sudo chown -R minecraft:minecraft /etc/minecraft

touch /etc/systemd/system/minecraft-server.service
cat <<EOF > /etc/systemd/system/minecraft-server.service
[Unit]
Description=Minecraft Server
After=network-online.target

[Service]
ExecStart=/bin/bash /etc/minecraft/boot.sh
EnvironmentFile=/etc/minecraft/environments
WorkingDirectory=/etc/minecraft
Restart=always
User=minecraft
Group=minecraft

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable minecraft-server
sudo systemctl start minecraft-server