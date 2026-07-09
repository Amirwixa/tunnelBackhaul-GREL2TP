#!/bin/bash
# Fixed Installer
echo "Starting installation..."

# ایجاد دایرکتوری ها
mkdir -p /etc/tunnel-manager
mkdir -p /etc/tunnel-manager/configs

# فقط مطمئن میشیم پایتون نصبه (دیگه به curl دست نمیزنیم)
apt-get update -y
apt-get install -y python3

# دانلود فایل اصلی منیجر
echo "Downloading manager..."
if command -v curl &> /dev/null; then
    curl -sSL https://raw.githubusercontent.com/Amirwixa/tunnelBackhaul-GREL2TP/refs/heads/main/manager.py -o /etc/tunnel-manager/manager.py
else
    wget -qO /etc/tunnel-manager/manager.py https://raw.githubusercontent.com/Amirwixa/tunnelBackhaul-GREL2TP/refs/heads/main/manager.py
fi

# ساخت دستور میانبر
echo '#!/bin/bash' > /usr/local/bin/tunnel-manager
echo 'python3 /etc/tunnel-manager/manager.py' >> /usr/local/bin/tunnel-manager
chmod +x /usr/local/bin/tunnel-manager

echo "------------------------------------------------"
echo "Done! Everything is ready."
echo "Just type 'tunnel-manager' to start."
echo "------------------------------------------------"
