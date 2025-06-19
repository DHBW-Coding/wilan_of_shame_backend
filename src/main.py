from scapy.all import sniff, DNS, TCP, IP, Ether, Packet
import bisect
from dataclasses import dataclass, field
from typing import Optional, Literal, Dict, Any
from datetime import datetime
import requests


@dataclass
class HTTPRequestDetails:
    url: str
    method: str


class DeviceEvent:
    def __init__(self, ip_address, mac_address: str, timestamp: Optional[str] = None):
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.timestamp = timestamp if timestamp else datetime.now(datetime.timezone.utc).isoformat()
        self.vendor: Optional[str] = None
        self.device_name: Optional[str] = None
        self.os_version: Optional[str] = None
        self.event_trigger: Literal["NEW_DEVICE", "DNS_QUERY", "HTTP_REQUEST_UNSECURE"] = "NEW_DEVICE"
        self.dns_queries: Optional[list[str]] = []
        self.http_request_details: Optional[HTTPRequestDetails] = None

        # Try to resolve manufacturer from MAC address using a local OUI database if available
        if mac_address:
            self.mac_address = mac_address.lower()
            self.vendor = self.resolve_mac(self.mac_address)

    def __lt__(self, other):
        return self.mac_address < other.mac_address
    
    def resolve_mac(self, mac_address):
        
        # We will use an API to get the vendor details
        url = "https://api.macvendors.com/"
        
        # Use get method to fetch details
        response = requests.get(url+mac_address)
        if response.status_code != 200:
            raise Exception("[!] Invalid MAC Address!")
        return response.content.decode()
    
        
    def filter_relevant_dns_queries(self):
        """ Filter out DNS queries that are not relevant """
        pass
    


def main():
    # Filters
    filter_tcp_out = "tcp and not src net 10.42.0.0/24"
    filter_no_gw = "not src 10.42.0.1"
    device_list = []

    def device_exist(mac_src=None):
        ''' Check if and where the device is in the list '''
        return bisect.bisect_left(device_list, mac_src, key=lambda d: d.ip_address) -1 ## TODO: The returned index is not right or something i get index out of range errors if there are more then one deivce, maybe you can not simply access the array by the index or something

    def add_device(ip_src, mac_src, timestamp=None):
        ''' Add a new device to the list '''
        device_event = DeviceEvent(ip_address=ip_src, mac_address=mac_src, timestamp=timestamp)
        bisect.insort(device_list, device_event)
        return True

    def print_device_events(device):
        ''' Print only non-null fields of the device '''
        attrs = [
            ("MAC", device.mac_address),
            ("IP", device.ip_address),
            ("Vendor", device.vendor if device.vendor and device.vendor != "N/A" else None),
            ("Timestamp", device.timestamp),
            ("Device Name", device.device_name),
            ("OS Version", device.os_version),
            ("DNS Query", device.dns_queries[-1] if device.dns_queries else None),
            ("HTTP Requests", device.http_request_details),
        ]
        print(", ".join(f"{name}: {value}" for name, value in attrs if value))

    # Define a callback function to process each packet
    def packet_callback(packet: Packet):
        if packet.haslayer(DNS) and packet.haslayer(IP):
            ip_src = packet[IP].src
            mac = packet[Ether].src if packet.haslayer(Ether) else "N/A"
            timestamp = packet.time
            device_index = device_exist(mac)

            if device_index == -1:
                add_device(ip_src, mac, timestamp)
                print(f"New device detected: {mac} ({ip_src}) at {datetime.fromtimestamp(timestamp).isoformat()}")
            else:
                device_event = device_list[device_index]
                device_event.timestamp = datetime.fromtimestamp(timestamp).isoformat()
                device_event.event_trigger = "DNS_QUERY"
                device_event.dns_queries.append(packet[DNS].qd.qname.decode('utf-8'))
                print_device_events(device_list[device_index])

    # Start sniffing packets on the 'wlp2s0' interface
    sniff(filter=filter_no_gw, prn=packet_callback, store=False, iface='wlp2s0')



# nslookup 157.240.223.61 // Facebook Whatsapp IP
# Network IP: 10.42.0.0


if __name__ == "__main__":
    main()