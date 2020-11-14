#!/usr/bin/env python3

import socket
import sys

UDP_IP = ""
UDP_PORT = 5005

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
except OSError as error:
    print(error)
    sys.exit()    

while True:
    data, addr = sock.recvfrom(1024)
    print("recibi:", data.decode())
    #sent = sock.sendto(data, addr)
