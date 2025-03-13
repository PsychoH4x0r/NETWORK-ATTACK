# utils/spoofing.py
import random
import re

def generate_random_ip():
    """Menghasilkan alamat IP acak (v4)."""
    # Hindari beberapa rentang khusus (misalnya, localhost, multicast)
    while True:
        ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
        if not (ip.startswith("127.") or  # Loopback
                ip.startswith("0.") or  # Reserved
                ip.startswith("255.") or # Broadcast
                ip.startswith("169.254.") or # Link-local
                (int(ip.split(".")[0]) >= 224 and int(ip.split(".")[0]) <= 239) ): #Multicast
                break
    return ip

def generate_random_mac():
    """Menghasilkan alamat MAC acak."""
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def validate_ip(ip_address):
    """Memvalidasi format alamat IPv4."""
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(pattern, ip_address):
        parts = ip_address.split(".")
        if all(0 <= int(part) <= 255 for part in parts):
            return True
    return False

def validate_mac(mac_address):
    """Memvalidasi format alamat MAC."""
    pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return bool(re.match(pattern, mac_address))