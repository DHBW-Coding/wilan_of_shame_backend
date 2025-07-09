#!/bin/bash

# Schnittstellen
WAN_IF="eth0"
LAN_IF="wlan0"
CAPTIVE_PORT=8080
CAPTIVE_IP="192.168.4.1"

echo "[+] Setze iptables-Regeln für Captive Portal..."

# Alte Regeln:
iptables -L

# Alte Regeln löschen
iptables -F
iptables -t nat -F
iptables -X

# 1. NAT für spätere Internetweiterleitung
iptables -t nat -A POSTROUTING -o $WAN_IF -j MASQUERADE

# 2. DNS (Port 53) erlauben
iptables -A INPUT -i $LAN_IF -p udp --dport 53 -j ACCEPT
iptables -A INPUT -i $LAN_IF -p tcp --dport 53 -j ACCEPT

# 3. Captive Portal (Port 8080) erlauben
iptables -A INPUT -i $LAN_IF -p tcp --dport $CAPTIVE_PORT -j ACCEPT
iptables -A INPUT -i $LAN_IF -p tcp --dport 80 -j ACCEPT  # Wenn du HTTP benutzt

# 4. Umleitung: HTTP-Port 80 → Captive Portal 8080
iptables -t nat -A PREROUTING -i $LAN_IF -p tcp --dport 80 -j REDIRECT --to-port $CAPTIVE_PORT

# 5. Blockiere jeglichen Internetzugriff (vor Login)
iptables -A FORWARD -i $LAN_IF -o $WAN_IF -j DROP

echo "[✓] Captive Portal Setup abgeschlossen."

# Neue Regeln:
iptables -L
