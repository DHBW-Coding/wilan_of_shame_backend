#!/bin/bash

# Schnittstellen
WAN_IF="eth0"
LAN_IF="wlan0"
CAPTIVE_PORT=8083
CAPTIVE_IP="192.168.4.1"

echo "[+] Setze iptables-Regeln für Captive Portal..."

# Alte Regeln löschen
iptables -F
iptables -t nat -F
iptables -X

# 1. NAT für spätere Internetweiterleitung
iptables -t nat -A POSTROUTING -o $WAN_IF -j MASQUERADE

# 2. DNS (Port 53) erlauben
iptables -A INPUT -i $LAN_IF -p udp --dport 53 -j ACCEPT
iptables -A INPUT -i $LAN_IF -p tcp --dport 53 -j ACCEPT

# 3. Captive Portal (Port 8083)
iptables -A INPUT -i $LAN_IF -p tcp --dport $CAPTIVE_PORT -j ACCEPT

# 4. Umleitung: HTTP-Port 80 → Captive Portal 8083
iptables -t nat -A PREROUTING -i $LAN_IF -p tcp --dport 80 -j REDIRECT --to-port $CAPTIVE_PORT

# 5. Blockiere jeglichen Internetzugriff (vor Login)
iptables -A FORWARD -i $LAN_IF -o $WAN_IF -j DROP

echo "[✓] Captive Portal Setup abgeschlossen."
