import socket
import time

import struct
import json

doc={}
doc["imei"] = "866989058575975"
doc["project"] = "test_project" #  //no es necesario..
doc["ota"]= "true"
doc["cmd"]= "true"
doc["sw"] = "6.6.6"
doc["hw"] = "1.1"
doc["otaV"] = "1.0"

#print(json.dumps(doc))
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('127.0.0.1',22222)) #localhost, 22222 ('18.229.227.108',65431)
clientsocket.settimeout(100)



###########################    Simulado Device OTA    ###################################
def deviceInfo(data):
    return json.dumps(data)


if __name__ == "__main__" :
    
    while True:
        #clientsocket.send((json.dumps(doc).encode()))
        

        ans = struct.pack("<BHBBBHB", 0xAA,3,1,0,0,1234,0xBB )
        clientsocket.send(ans) 
        time.sleep(5)
        ans = struct.pack("<BHBBBHB", 0xAA,3,2,1,0,1236,0xBB )
        clientsocket.send(ans) 
        time.sleep(5)