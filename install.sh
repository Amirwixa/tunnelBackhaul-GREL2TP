#!/bin/bash
apt update && apt install -y python3 curl
mkdir -p /etc/tunnel-manager
curl -sSL https://raw.githubusercontent.com/Amirwixa/tunnelBackhaul-GREL2TP/refs/heads/main/manager.py -o /etc/tunnel-manager/manager.py
echo '#!/bin/bash' > /usr/local/bin/tunnel-manager
echo 'python3 /etc/tunnel-manager/manager.py' >> /usr/local/bin/tunnel-manager
chmod +x /usr/local/bin/tunnel-manager
echo "Done! Type 'tunnel-manager' to start."