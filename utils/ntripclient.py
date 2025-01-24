import base64
import socket
from math import acos, asin, atan2, cos, pi, sin, sqrt

# ************* NTRIP request ***************

def create_ntrip_request(host, port, mountpoint, user, password):
    """
    Creates and returns a socket connected to the NTRIP caster and sends
    an HTTP GET request for the specified mountpoint with basic auth.
    """
    # Create a basic authentication string
    user_pass = f"{user}:{password}"
    user_pass_b64 = base64.b64encode(user_pass.encode()).decode()

    # Construct the NTRIP request
    request_header = (
        f"GET /{mountpoint} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"User-Agent: NTRIP PythonClient/1.0\r\n"
        f"Authorization: Basic {user_pass_b64}\r\n"
        f"Ntrip-Version: Ntrip/2.0\r\n"
        f"Accept: */*\r\n"
        f"Connection: close\r\n"
        "\r\n"
    )

    # Create a TCP socket
    ntrip_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ntrip_socket.settimeout(5)

    # Connect to caster
    ntrip_socket.connect((host, port))

    # Send request
    ntrip_socket.send(request_header.encode())

    # Read response header
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = ntrip_socket.recv(4096)
        if not chunk:
            raise ConnectionError("No response or incomplete response from NTRIP server.")
        response += chunk

    # Check if the response indicates success (e.g., HTTP/1.1 200 OK)
    if b"200 OK" not in response:
        print("NTRIP connection failed. Response header:")
        print(response.decode(errors='ignore'))
        raise ConnectionError("Failed to connect to NTRIP caster.")

    print("Connected to NTRIP caster successfully.")
    return ntrip_socket

def renew_request(ntrip_socket, host, port, mountpoint, user, password):
    """
    Creates and returns a socket connected to the NTRIP caster and sends
    an HTTP GET request for the specified mountpoint with basic auth.
    """
    # Create a basic authentication string
    user_pass = f"{user}:{password}"
    user_pass_b64 = base64.b64encode(user_pass.encode()).decode()

    # Construct the NTRIP request
    request_header = (
        f"GET /{mountpoint} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"User-Agent: NTRIP PythonClient/1.0\r\n"
        f"Authorization: Basic {user_pass_b64}\r\n"
        f"Ntrip-Version: Ntrip/2.0\r\n"
        f"Accept: */*\r\n"
        f"Connection: close\r\n"
        "\r\n"
    )
    print(request_header)
    # Send request
    ntrip_socket.close()
    ntrip_socket.connect()
    ntrip_socket.send(request_header.encode())

    # Read response header
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = ntrip_socket.recv(4096)
        if not chunk:
            raise ConnectionError("No response or incomplete response from NTRIP server.")
        response += chunk

    # Check if the response indicates success (e.g., HTTP/1.1 200 OK)
    if b"200 OK" not in response:
        print("NTRIP connection failed. Response header:")
        print(response.decode(errors='ignore'))
        raise ConnectionError("Failed to connect to NTRIP caster.")

    print("Successfully reconnected to NTRIP caster")

def ntrip_getmountpoints(host, port, user, password):
    """
    Creates and returns a socket connected to the NTRIP caster and sends
    an HTTP GET request for the specified mountpoint with basic auth.
    """
    # Create a basic authentication string
    user_pass = f"{user}:{password}"
    user_pass_b64 = base64.b64encode(user_pass.encode()).decode()

    # Construct the NTRIP request
    request_header = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"User-Agent: NTRIP PythonClient/1.0\r\n"
        f"Authorization: Basic {user_pass_b64}\r\n"
        f"Ntrip-Version: Ntrip/2.0\r\n"
        f"Accept: */*\r\n"
        f"Connection: close\r\n"
        "\r\n"
    )

    # Create a TCP socket
    ntrip_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ntrip_socket.settimeout(5)

    # Connect to caster
    ntrip_socket.connect((host, port))

    # Send request
    ntrip_socket.send(request_header.encode())

    # Read response header
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = ntrip_socket.recv(4096)
        if not chunk:
            raise ConnectionError("No response or incomplete response from NTRIP server.")
        response += chunk

    # Check if the response indicates success (e.g., HTTP/1.1 200 OK)
    if b"200 OK" not in response:
        print("NTRIP connection failed. Response header:")
        print(response.decode(errors='ignore'))
        raise ConnectionError("Failed to connect to NTRIP caster.")

    mountpoints=""
    mountdict=[]
    while True:
        chunk = ntrip_socket.recv(4096)
        if not chunk:
            break
        mountpoints += chunk.decode()
    mountpointlist = mountpoints.splitlines()
    for mpt in mountpointlist:
        l = mpt.split(";")
        if len(l)<19: continue
        mountdict.append({'name':l[1],'locality':l[2],'protocol':l[3],'constellations':l[6],'country':l[8],'latitude':float(l[9]),'longitude':float(l[10]),'material':l[13],'network':l[18]})
    return mountdict

def sphericaldist(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    radius: int = 6378.137,
) -> float:
    """
    Calculate spherical distance in km between two coordinates using haversine formula.

    NB suitable for coordinates greater than around 50m apart. For
    smaller separations, use the planar approximation formula.

    :param float lat1: lat1
    :param float lon1: lon1
    :param float lat2: lat2
    :param float lon2: lon2
    :param float radius: radius in km (Earth = 6378.137 km)
    :return: spherical distance in km
    :rtype: float
    """

    phi1, lambda1, phi2, lambda2 = [c * pi / 180 for c in (lat1, lon1, lat2, lon2)]
    dist = radius * acos(
        cos(phi2 - phi1) - cos(phi1) * cos(phi2) * (1 - cos(lambda2 - lambda1))
    )

    return dist