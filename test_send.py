#!/usr/bin/env python3

import socket
import sys

UDP_IP = "<broadcast>"
UDP_PORT = 5005
MESSAGE = "Hello, World!".encode()

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(3)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    #resp = sock.recvfrom(1024)
except OSError as error:
    print(error)
    sys.exit()
finally:
    sock.close()
   
print ("termine de enviar")