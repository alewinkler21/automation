
import socket
from time import sleep

import re
import threading
from automation.models import PioneerType

radio_volume = 81
chromecast_volume = 91

def toggle_pioneer(status, device):    
    pioneer = Pioneer(device)
    if pioneer.connect():
        if not status:
            pioneer.powerOff()
        else:
            if device.type == PioneerType.objects.get(name="Radio"):
                thread = threading.Thread(target=pioneer.radio,args=())
            elif device.type == PioneerType.objects.get(name="Chromecast"):
                thread = threading.Thread(target=pioneer.chromecast,args=())
            if not thread is None:
                thread.start()
        return True
    else:
        return False

class Pioneer:

    def __init__(self, device, sock=None):
        self.device = device
        if sock is None:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except msg:
                print ('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
        else:
            self.sock = sock
    
    def __powerOn(self):
        self.__send("?P");
        res = self.__readResponse()
        if res.rstrip() != "PWR0":
            print("Let's turn the device on")
            self.__send("PO");
        else:
            print("Device already turned on")
        
    def powerOff(self):
        self.__send("?P");
        res = self.__readResponse()
        if res.rstrip() == "PWR0":
            print("Let's turn the device off")
            self.__send("PF");
        else:
            print("Device already turned off")

    def __send(self, msg):
        msg += "\r\n";
        try :
            self.sock.sendall(msg)
        except socket.error:
            print("Send failed")
        sleep(0.3)
            
    def __getVolume(self):
        self.__send("?VOL");
        res = self.__readResponse()
        pattern = re.compile("\d\d\d")
        search = pattern.search(res)
        if search:
            volume = search.group()
            return int(volume)
        return -1
    
    def __readResponse(self):
        res = self.sock.recv(1024)
        sleep(0.2)
        return res

    def __configureVolume(self, desired_vol):
        vol = self.__getVolume()
        if vol < 0:
            print("Failed to obtain volume")
            return
        
        print("Volume is " + str(vol))
        while vol != desired_vol:
            if vol < desired_vol:
                self.__send("VU");
            else:
                self.__send("VD");
            self.__readResponse()
            vol = self.__getVolume()
            print("New volume is " + str(vol))

    def connect(self):
        try:
            self.sock.connect((self.device.address, 
                               self.device.port))
            return True
        except socket.error:
            self.sock.close()
            return False

    def __disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def radio(self):
        # turn on device
        self.__powerOn()
        # select radio
        self.__send("02FN");
        # select volume
        self.__configureVolume(radio_volume)
        # disconnect
        self.__disconnect()
        
    def chromecast(self):
        # turn on device
        self.__powerOn()
        # select video
        self.__send("10FN");
        # select volume
        self.__configureVolume(chromecast_volume)
        # disconnect
        self.__disconnect()
