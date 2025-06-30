def get_hostname_by_ip(ip, lease_file='/var/lib/NetworkManager/dnsmasq-wlp2s0.leases'):
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

# Example usage:
ip = '10.42.0.254'
print(get_hostname_by_ip(ip))
