
import socket
import time
import urllib.request
import urllib.parse
import urllib.error
import json


DNS_SERVERS = {
    "Google": "8.8.8.8",
    "Cloudflare": "1.1.1.1",
    "Quad9": "9.9.9.9"
}

DOH_PROVIDERS = {
    "Cloudflare": "https://cloudflare-dns.com/dns-query",
    "Google": "https://dns.google/resolve"
}

QUERY_NAME = "example.com"
TIMEOUT = 5


def check_udp_dns(name, server, timeout=TIMEOUT):
    """Perform an actual DNS A-record query over UDP."""

    print(f"\nTesting {name} DNS ({server})...")

    # DNS query for example.com A record
    query_id = 12345
    question = (
        QUERY_NAME.split(".")
    )

    encoded_name = b"".join(
        bytes([len(part)]) + part.encode("ascii")
        for part in question
    ) + b"\x00"

    dns_query = (
        query_id.to_bytes(2, "big")
        + b"\x01\x00"  # Standard query, recursion desired
        + b"\x00\x01"  # One question
        + b"\x00\x00\x00\x00\x00\x00"
        + encoded_name
        + b"\x00\x01"  # A record
        + b"\x00\x01"  # Internet class
    )

    start = time.perf_counter()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.sendto(dns_query, (server, 53))

            response, _ = sock.recvfrom(4096)

        elapsed = (time.perf_counter() - start) * 1000

        if len(response) < 12:
            raise ValueError("Incomplete DNS response.")

        response_id = int.from_bytes(response[:2], "big")
        flags = int.from_bytes(response[2:4], "big")
        rcode = flags & 0x000F

        if response_id != query_id:
            raise ValueError("DNS transaction ID mismatch.")

        if not flags & 0x8000:
            raise ValueError("Response is not a DNS response.")

        if rcode != 0:
            raise ValueError(f"DNS server returned response code {rcode}.")

        print(f"[SUCCESS] DNS query answered.")
        print(f"Response time: {elapsed:.2f} ms")

    except socket.timeout:
        print(f"[TIMEOUT] No DNS response within {timeout} seconds.")

    except (socket.error, ValueError) as error:
        print(f"[FAILURE] DNS query failed: {error}")


def check_doh(name, url, timeout=TIMEOUT):
    """Perform a DNS query using DNS over HTTPS."""

    print(f"\nTesting {name} DNS over HTTPS...")

    params = urllib.parse.urlencode({
        "name": QUERY_NAME,
        "type": "A"
    })

    request_url = f"{url}?{params}"

    headers = {
        "Accept": "application/dns-json"
    }

    request = urllib.request.Request(
        request_url,
        headers=headers
    )

    start = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))

        elapsed = (time.perf_counter() - start) * 1000

        if data.get("Status") != 0:
            print(
                f"[FAILURE] DNS response code: {data.get('Status')}"
            )
            return

        answers = data.get("Answer", [])

        addresses = [
            answer["data"]
            for answer in answers
            if answer.get("type") == 1
        ]

        if not addresses:
            print("[WARNING] No IPv4 A records returned.")
            return

        print("[SUCCESS] DNS query answered.")
        print(f"Response time: {elapsed:.2f} ms")
        print(f"IP addresses: {', '.join(addresses)}")

    except (urllib.error.URLError, TimeoutError, OSError) as error:
        print(f"[FAILURE] DoH request failed: {error}")

    except (ValueError, KeyError) as error:
        print(f"[FAILURE] Invalid DNS response: {error}")


def main():
    print("=" * 60)
    print("DNS AND DNS OVER HTTPS HEALTH AUDIT")
    print(f"Query: {QUERY_NAME} (A record)")
    print("=" * 60)

    print("\n--- 1. Traditional DNS over UDP ---")

    for name, server in DNS_SERVERS.items():
        check_udp_dns(name, server)

    print("\n--- 2. DNS over HTTPS ---")

    for name, url in DOH_PROVIDERS.items():
        check_doh(name, url)

    print("\n" + "=" * 60)
    print("DNS AUDIT COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
