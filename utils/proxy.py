# utils/proxy.py
import requests
import logging
import re

log = logging.getLogger(__name__)

def load_proxies(filename):
    """Memuat daftar proxy dari file (satu proxy per baris, format: host:port)."""
    proxies = []
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line and validate_proxy_format(line):  # Validasi format
                    proxies.append(line)
                else:
                    log.warning(f"Skipping invalid proxy line: {line}")
    except FileNotFoundError:
        log.error(f"Proxy file not found: {filename}")
    return proxies

def validate_proxy_format(proxy):
    """Memvalidasi format proxy (host:port)."""
    pattern = r"^[a-zA-Z0-9\.-]+:\d+$"  # Hostname atau IP, titik dua, port (angka)
    return bool(re.match(pattern, proxy))


def check_proxy(proxy, url="http://www.google.com", timeout=5):
    """
    Memeriksa apakah proxy berfungsi.  Ini adalah contoh yang sangat sederhana.

    Args:
        proxy:  String proxy (format: "host:port").
        url: URL untuk test koneksi (default: google.com).
        timeout: Timeout dalam detik.

    Returns:
        True jika proxy berfungsi, False jika tidak.
    """
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"https://{proxy}",  # Tambahkan dukungan HTTPS
        }
        response = requests.get(url, proxies=proxies, timeout=timeout)
        response.raise_for_status()  # Raise HTTPError untuk bad responses (4xx atau 5xx)
        return True
    except requests.exceptions.RequestException as e:
        log.debug(f"Proxy check failed for {proxy}: {e}") # Debug, not error.
        return False
    except Exception as e:
        log.exception(f"An unexpected error occurred: {e}")
        return False


# Contoh penggunaan (dan untuk pengujian):
if __name__ == "__main__":
    # Buat file proxy palsu untuk pengujian
    with open("test_proxies.txt", "w") as f:
        f.write("1.2.3.4:8080\n")
        f.write("proxy.example.com:3128\n")
        f.write("invalid-proxy\n")  # Baris yang tidak valid
        f.write("5.6.7.8:80\n")

    proxies = load_proxies("test_proxies.txt")
    print(f"Loaded proxies: {proxies}")

    for p in proxies:
        if check_proxy(p):
            print(f"Proxy {p} is working.")
        else:
            print(f"Proxy {p} is NOT working.")