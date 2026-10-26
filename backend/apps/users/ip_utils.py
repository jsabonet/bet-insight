"""Client IP resolution for registration and security checks."""
import ipaddress

from django.conf import settings


def _trusted_proxy_networks():
    networks = []
    for value in getattr(settings, 'TRUSTED_PROXY_IPS', ()):
        try:
            networks.append(ipaddress.ip_network(value, strict=False))
        except ValueError:
            continue
    return networks


def get_client_ip(request):
    """Trust forwarded IPs only when REMOTE_ADDR belongs to a configured proxy."""
    try:
        remote_addr = ipaddress.ip_address(request.META.get('REMOTE_ADDR', ''))
    except ValueError:
        return None

    trusted_networks = _trusted_proxy_networks()
    if not any(remote_addr in network for network in trusted_networks):
        return str(remote_addr)

    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    try:
        chain = [ipaddress.ip_address(value.strip()) for value in forwarded.split(',') if value.strip()]
    except ValueError:
        return str(remote_addr)

    current = remote_addr
    for hop in reversed(chain):
        if not any(current in network for network in trusted_networks):
            break
        current = hop
    return str(current)
