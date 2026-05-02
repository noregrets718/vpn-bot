import base64
import json
import os


def _load_bypass_domains() -> list[str]:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bypass_domains.txt")
    domains = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    domains.append(f"domain:{line}")
    except FileNotFoundError:
        pass
    return domains


def make_routing_deeplink() -> str:
    """Возвращает happ://routing/onadd/{base64} deep link с bypass-профилем для RU-трафика."""
    direct_sites = [
        "geosite:private",
        "geosite:category-ru",
        *_load_bypass_domains(),
    ]

    profile = {
        "Name": "RU Bypass",
        "GlobalProxy": "false",
        "UseChunkFiles": "true",
        "RemoteDNSType": "DoH",
        "RemoteDNSDomain": "https://8.8.8.8/dns-query",
        "RemoteDNSIP": "8.8.8.8",
        "DomesticDNSType": "DoH",
        "DomesticDNSDomain": "https://77.88.8.8/dns-query",
        "DomesticDNSIP": "77.88.8.8",
        "RouteOrder": "block-proxy-direct",
        "DirectSites": direct_sites,
        "DirectIp": ["geoip:private"],
        "ProxySites": [],
        "ProxyIp": [],
        "BlockSites": ["geosite:category-ads"],
        "BlockIp": [],
        "DomainStrategy": "IPIfNonMatch",
        "FakeDNS": "false",
    }

    payload = json.dumps(profile, ensure_ascii=False, separators=(",", ":"))
    encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
    return f"happ://routing/onadd/{encoded}"