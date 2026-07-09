import os
import sys
import subprocess
import socket
import urllib.request
import shutil

BASE = "/etc/tunnel-manager"
BIN_PATH = "/usr/local/bin/backhaul"

def run(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except: ip = '127.0.0.1'
    finally: s.close()
    return ip

def make_persistent(name, commands):
    script_path = f"{BASE}/{name}_setup.sh"
    with open(script_path, "w") as f:
        f.write("#!/bin/bash\nsleep 10\n" + "\n".join(commands))
    os.chmod(script_path, 0o755)
    service = f"""[Unit]
Description=Tunnel {name}
After=network-online.target
[Service]
Type=oneshot
ExecStart={script_path}
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target"""
    with open(f"/etc/systemd/system/tunnel-{name}.service", "w") as f: f.write(service)
    run("systemctl daemon-reload")
    run(f"systemctl enable --now tunnel-{name}.service")

def setup_native():
    os.system("clear")
    print("1) GRE\n2) GRETAP\n3) IPIP\n4) VXLAN\n0) Back")
    ch = input("Select: ")
    if ch == '0': return
    types = {"1": "gre", "2": "gretap", "3": "ipip", "4": "vxlan"}
    t = types.get(ch)
    if not t: return

    dev = input("Interface name (default tun1): ") or "tun1"
    rem = input("Remote Public IP: ")
    my_t = input("Local Tunnel IP: ")
    rem_t = input("Remote Tunnel IP: ")

    cmds = [f"ip link del {dev} || true"]
    if t == "vxlan":
        cmds.append(f"ip link add {dev} type vxlan id 100 remote {rem} local {get_ip()} dstport 4789")
        cmds.append(f"ip addr add {my_t}/30 dev {dev}")
    elif t == "gretap":
        cmds.append(f"ip link add {dev} type gretap remote {rem} local {get_ip()} ttl 255")
        cmds.append(f"ip addr add {my_t}/30 dev {dev}")
    else:
        cmds.append(f"ip link add {dev} type {t} remote {rem} local {get_ip()} ttl 255")
        cmds.append(f"ip addr add {my_t} peer {rem_t} dev {dev}")
    
    cmds.append(f"ip link set {dev} up")
    cmds.append("sysctl -w net.ipv4.ip_forward=1")
    cmds.append("iptables -t nat -A POSTROUTING -j MASQUERADE")
    
    for c in cmds: os.system(c)
    if input("Auto-start on reboot? (y/n): ") == 'y': make_persistent(dev, cmds)

def setup_backhaul():
    if not os.path.exists(BIN_PATH):
        print("Downloading Backhaul...")
        url = "https://github.com/Musixal/Backhaul/releases/latest/download/backhaul_linux_amd64.tar.gz"
        urllib.request.urlretrieve(url, "/tmp/bh.tar.gz")
        shutil.unpack_archive("/tmp/bh.tar.gz", "/tmp/bh")
        shutil.move("/tmp/bh/backhaul", BIN_PATH)
        os.chmod(BIN_PATH, 0o755)
    
    name = input("Tunnel Name: ")
    mode = input("Mode (server/client): ")
    port = input("Port: ")
    token = input("Token: ")
    
    cfg = f"[{mode}]\nbind_addr = '0.0.0.0:{port}'\ntoken = '{token}'"
    os.makedirs(f"{BASE}/configs", exist_ok=True)
    with open(f"{BASE}/configs/{name}.toml", "w") as f: f.write(cfg)
    
    svc = f"""[Unit]
Description=Backhaul {name}
[Service]
ExecStart={BIN_PATH} -c {BASE}/configs/{name}.toml
Restart=always
[Install]
WantedBy=multi-user.target"""
    with open(f"/etc/systemd/system/bh-{name}.service", "w") as f: f.write(svc)
    run("systemctl enable --now bh-" + name)
    print("Backhaul tunnel created!")

def main():
    if os.geteuid() != 0: exit("Run as root!")
    os.makedirs(BASE, exist_ok=True)
    while True:
        os.system("clear")
        print("--- TUNNEL MANAGER ---\n1) Backhaul\n2) Native Tunnel\n0) Exit")
        c = input("Select: ")
        if c == '1': setup_backhaul()
        elif c == '2': setup_native()
        elif c == '0': break

if __name__ == "__main__": main()