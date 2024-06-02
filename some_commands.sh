[Unit]
Description=BotYoutube2Telegram
After=network.target

[Service]
ExecStart=/bin/bash /home/pi/Desktop/bot-ytb2telegram/run.sh
WorkingDirectory=/home/pi/Desktop/bot-ytb2telegram/
User=pi
Group=pi
Restart=always
Environment="PATH=/home/pi/Desktop/bot-ytb2telegram/venv/bin:/usr/bin"
StandardOutput=file:/var/log/bot-ytb2telegram-output.log
StandardError=file:/var/log/bot-ytb2telegram-error.log

[Install]
WantedBy=multi-user.target

#############




mv systemd.service bot-ytb2telegram.service

cp bot-ytb2telegram.service /etc/systemd/system/bot-ytb2telegram.service

sudo nano /etc/systemd/system/bot-ytb2telegram.service

ln -s /var/log/bot-ytb2telegram/output.log output.log
ln -s /var/log/bot-ytb2telegram/error.log error.log


sudo systemctl enable bot-ytb2telegram.service


sudo systemctl start bot-ytb2telegram.service

sudo systemctl status bot-ytb2telegram.service

sudo systemctl restart bot-ytb2telegram.service

sudo mkdir -p /var/log/bot-ytb2telegram
sudo chown pi:pi /var/log/bot-ytb2telegram


sudo  nano /etc/systemd/system/bot-ytb2telegram.service