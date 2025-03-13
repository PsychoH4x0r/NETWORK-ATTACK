# utils/scanner.py

import logging
import asyncio
from bleak import BleakScanner
from scapy.all import (  # Import scapy.all dengan benar
    Dot11,
    Dot11Beacon,
    Dot11Elt,
    sniff,
    RadioTap,
    AsyncSniffer,
    Scapy_Exception
)
import time

log = logging.getLogger(__name__)


def scan_wifi():
    """Memindai jaringan WiFi terdekat dan mengembalikan daftar dictionary."""

    networks = []
    aps = set()

    def packet_handler(pkt):
        if pkt.haslayer(Dot11Beacon):
            bssid = pkt[Dot11].addr2
            if bssid not in aps:
                 aps.add(bssid)
                 ssid = pkt[Dot11Elt].info.decode("utf-8", errors="ignore") #Decode ssdi
                 try:
                     channel = int(pkt[Dot11Elt:3].info.decode())
                 except:
                     channel = 0
                 networks.append({'ssid':ssid, 'bssid': bssid, 'channel': channel})
                 log.info(f"Menemukan WiFi: SSID={ssid}, BSSID={bssid}, Channel={channel}")

    # Sniff bingkai suar WiFi, yang berisi informasi jaringan.
    log.info("Memindai jaringan WiFi...")
    try:
      sniffer = AsyncSniffer(prn=packet_handler, store=False, iface="Wi-Fi") #Ganti "Wi-Fi" dengan Nama Interface Anda
      sniffer.start()
      time.sleep(10)  # Sniff selama 10 detik (sesuaikan kebutuhan)
      sniffer.stop()
    except Scapy_Exception as e:
         log.error(f"Scapy exception: {e}")
    except Exception as e:
         log.exception(f"Error selama pemindaian Wi-Fi: {e}")

    return networks



async def scan_bluetooth():
    """Memindai perangkat Bluetooth terdekat dan mengembalikan daftar tupel (alamat, nama)."""
    log.info("Memindai perangkat Bluetooth...")
    devices = await BleakScanner.discover(timeout=10.0)  # Temukan perangkat. Timeout
    log.info("Pemindaian Bluetooth selesai.")
    return [(device.address, device.name) for device in devices]