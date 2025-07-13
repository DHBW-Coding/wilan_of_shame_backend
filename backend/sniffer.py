import asyncio
import string
from time import sleep
from scapy.all import sniff, DNS, TCP, IP, Ether, Packet
import bisect
from dataclasses import dataclass, field
from typing import Optional, Literal, Dict, Any
from datetime import datetime
import requests

from websocket_manager import ws_manager
import json

#LEASE_FILE = '/var/lib/misc/dnsmasq.leases'                # For Raspberry Pi
#INTERFACE = 'wlan0'
#NETWORK_IP = '192.168.4.1'
LEASE_FILE = '/var/lib/NetworkManager/dnsmasq-wlp2s0.leases'
INTERFACE = 'wlp2s0'
NETWORK_IP = '10.42.0.1'

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
            temp_vendor = self.resolve_mac()
            if temp_vendor and "(" in temp_vendor:
                temp_vendor = temp_vendor.split("(", 1)[0].strip()
            self.vendor = temp_vendor       
        if ip_address:
            self.device_name = self.request_device_name()

    def __lt__(self, other):
        return self.mac_address < other.mac_address

    def to_dict(self):
        """ Convert the device event to a dictionary for easy serialization """
        return {
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "timestamp": self.timestamp,
            "vendor": self.vendor,
            "device_name": self.device_name,
            "os_version": self.os_version,
            "event_trigger": self.event_trigger,
            "dns_query": self.dns_queries[-1] if self.dns_queries else None,
            "http_request_details": vars(self.http_request_details) if self.http_request_details else None,
        }

    def resolve_mac(self):
        
        # We will use an API to get the vendor details
        url = "https://api.macvendors.com/"
        formatted_mac = self.mac_address.replace(":", "")
        # Use get method to fetch details
        response = requests.get(url+formatted_mac)
        if response.status_code != 200:
            print("[!] Invalid MAC Address!")
            if self.device_name:
                if self.device_name.startswith("iPhone") or self.device_name.startswith("iPad"):
                    return "Apple, Inc." # Default to Apple Inc. for testing purposes
                if self.device_name.startswith("S"):
                    return "Samsung Electronics Co.,Ltd"
            return "N/A"
        return response.content.decode()
    
    def add_event(self, event_type: Literal["NEW_DEVICE", "DNS_QUERY", "HTTP_REQUEST_UNSECURE"], details = None):
        """ Add an event to the device """
        self.event_trigger = event_type
        if event_type == "DNS_QUERY" and details:
            details = self.filter_relevant_dns_queries(details)
            if details:
                self.dns_queries.append(details)
                return True
        elif event_type == "HTTP_REQUEST_UNSECURE" and details:
            self.http_request_details = HTTPRequestDetails(
                url=details.get('url', ''),
                method=details.get('method', '')
            )
        return False
        
    def filter_relevant_dns_queries(self, details):
        """Filter out DNS queries that are not relevant and update the list."""

        # Helper to check similarity (same domain, last two labels)
        def is_similar(q1, q2):
            def get_domain(q):
                parts = q.strip('.').split('.')
                return '.'.join(parts[-2:]) if len(parts) >= 2 else q
            return get_domain(q1) == get_domain(q2)
        
        def sanitize_query(q):
            parts = q.strip('.').split('.')
            if q.startswith('www'):
                return q
            elif parts.length > 3:
                return '.'.join(parts[-3:])
            return q
        
        def lookup_interesting_domains(q):
            
            readable_name = interesting_domains.get(q)
            if readable_name == "Not relevant":
                return None
            elif readable_name:
                return readable_name
            return q

        last_queries = self.dns_queries[-5:] if len(self.dns_queries) >= 5 else self.dns_queries
        if details not in last_queries and not any(is_similar(details, q) for q in last_queries):
            return details
        else:
            return None

    def request_device_name(self, lease_file=LEASE_FILE):
        """ Request the device name from the lease file based on the IP address """
        ip = self.ip_address
        try:
            with open(lease_file) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 4 and parts[2] == ip:
                        return parts[3] if parts[3] != '*' else 'Unknown'
        except FileNotFoundError:
            print(f"File not found: {lease_file}")
        except Exception as e:
            print(f"Error: {e}")
        return None

#Create a class dont declare global variables    
device_list = []
interesting_domains = None

def device_exist(mac_src=None):
        ''' Check if and where the device is in the list '''
        #return bisect.bisect_left(device_list, mac_src, key=lambda d: d.ip_address) -1 
        i = 0
        for device in device_list:
            if device.mac_address == mac_src:
                return i
            i = i + 1
            
        return -1
        

def add_device(ip_src, mac_src, timestamp=None):
    ''' Add a new device to the list '''
    device_event = DeviceEvent(ip_address=ip_src, mac_address=mac_src, timestamp=timestamp)
    #bisect.insort(device_list, device_event)
    device_list.append(device_event)
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
def packet_callback(packet: Packet, event_queue=None):
    if packet.haslayer(DNS) and packet.haslayer(IP):
        ip_src = packet[IP].src
        mac = packet[Ether].src if packet.haslayer(Ether) else "N/A"
        timestamp = packet.time
        device_index = device_exist(mac)

        if device_index == -1:
            add_device(ip_src, mac, timestamp)
            print(f"New device detected: {mac} ({ip_src}) at {datetime.fromtimestamp(timestamp).isoformat()}")
            # Sent over WebSocket
            if event_queue:
                print("New Device index: ", device_index, len(device_list))
                event_json = json.dumps(device_list[-1].to_dict())
                event_queue.put(event_json)
        else:
            device_list[device_index].timestamp = datetime.fromtimestamp(timestamp).isoformat()
            if packet[DNS].qd:
                if device_list[device_index].add_event("DNS_QUERY", packet[DNS].qd.qname.decode('utf-8')):
                    #print_device_events(device_list[device_index])
                    print(device_index, len(device_list))
                    ## Sent over WebSocket
                    if event_queue:
                        event_json = json.dumps(device_list[device_index].to_dict())
                        event_queue.put(event_json)
                        print("Event sent:", device_list[device_index].mac_address)

def start_sniffing(event_queue):
    # Load interesting domains
    try:
        with open("interesting_domains.json", "r") as f:
            interesting_domains = json.load(f)
    except Exception as e:
        print(f"Error loading interesting_domains.json: {e}")

    # Filters
    filter_no_gw = "not src " + NETWORK_IP

    # Start sniffing packets on the 'wlp2s0' interface
    sniff(filter=filter_no_gw, prn=lambda pkt: packet_callback(pkt, event_queue), store=False, iface=INTERFACE)

    # nslookup 157.240.223.61 // Facebook Whatsapp IP