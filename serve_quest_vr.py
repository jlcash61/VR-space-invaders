"""
One-Command Meta Quest 2 WebXR HTTPS Server
-------------------------------------------
Meta Quest Browser requires HTTPS to unlock WebXR ("ENTER VR") over local Wi-Fi.
Run this script with:
    python serve_quest_vr.py
Then open the printed https://<YOUR-PC-IP>:8443/space_invaders_vr.html URL
in your Meta Quest 2 Browser!
"""

import datetime
import http.server
import os
import socket
import ssl
import tempfile


def get_lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def ensure_self_signed_cert(cert_path: str, key_path: str, lan_ip: str) -> None:
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return

    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID
        import ipaddress

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"SpaceInvadersQuestVR"),
        ])
        alt_names = [
            x509.DNSName(u"localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
        ]
        try:
            alt_names.append(x509.IPAddress(ipaddress.ip_address(lan_ip)))
        except ValueError:
            pass

        now = datetime.datetime.now(datetime.timezone.utc)
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=365))
            .add_extension(x509.SubjectAlternativeName(alt_names), critical=False)
            .sign(key, hashes.SHA256())
        )

        with open(key_path, "wb") as f:
            f.write(
                key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        return
    except ImportError:
        # Fallback to openssl CLI if cryptography package isn't installed
        cmd = (
            f'openssl req -x509 -newkey rsa:2048 -keyout "{key_path}" '
            f'-out "{cert_path}" -days 365 -nodes -subj "/CN={lan_ip}"'
        )
        if os.system(cmd) != 0:
            raise RuntimeError(
                "Could not generate SSL certificate. Run: pip install cryptography"
            )


def main() -> None:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = 8443
    lan_ip = get_lan_ip()

    cert_dir = tempfile.gettempdir()
    cert_file = os.path.join(cert_dir, "quest_vr_cert.pem")
    key_file = os.path.join(cert_dir, "quest_vr_key.pem")

    ensure_self_signed_cert(cert_file, key_file, lan_ip)

    server_address = ("0.0.0.0", port)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print("=" * 68)
    print("  SPACE INVADERS VR // META QUEST 2 HTTPS SERVER RUNNING")
    print("=" * 68)
    print(f"  1. Put on your Meta Quest 2 (connected to the same Wi-Fi)")
    print(f"  2. Open the Meta Quest Browser and go to:")
    print(f"\n     https://{lan_ip}:{port}/space_invaders_vr.html\n")
    print(f"  3. Click 'Advanced' -> 'Proceed' on the self-signed cert prompt")
    print(f"  4. Click 'ENTER META QUEST 2 VR' and pull triggers to play!")
    print("=" * 68)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
