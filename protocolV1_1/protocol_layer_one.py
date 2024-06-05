import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)

import struct
import typing

import protocolV1_1.protocol_headers as protocol_headers
import protocolV1_1.protocol_layer_two_request as protocol_layer_two_request  
import protocolV1_1.protocol_layer_two_content as protocol_layer_two_content
from protocolV1_1.utils import trunc_1byte
import echos

class WrongType(Exception):
    pass



#			LOGIN
#   ___________________________________________________
#  |     |        |      |     |     |     |     |     |
#  | SOF | Len    | type | VER | IMEI|  ID | CRC | EOF |
#  |_____|________|______|__Y__|__Y__|__Y__|__X__|_____|
#    1B      2B      1B    2B    8B    2B    4B	   1B
#                  type ver imei id crc -> solo recibira estos campos. 


class login_tuple(typing.NamedTuple):
    ver: int
    imei: int
    pattern_code: bytearray
    token:        bytearray
    def __str__(self):
        return "Login Tuple ver: {0}, imei: {1}, pattern_code: {2}, token: {3}".format( self.ver,
                                                                                        self.imei,
                                                                                        self.pattern_code.decode("latin-1"),
                                                                                        self.token.decode("latin-1"))


class login():
    endianess = f"{protocol_headers.ENDIANESS}HQ" 
    @staticmethod        
    def read(buff: bytearray) -> login_tuple:
        idx = 0
        [ver, imei] = struct.unpack(login.endianess, buff[idx:idx+10])
        idx = 10
        data_list = [] 
        for _ in range(2):
            data_end = buff.find(0, idx)
            data = buff[idx: data_end]
            idx+= len(data) + 1
            data_list.append(data)

        result = login_tuple(ver, imei, *data_list)
        return result

    @staticmethod
    def write( data : login_tuple):
        numbers = struct.pack(login.endianess, data.ver, data.imei)
        pattern_code = data.pattern_code + bytearray([0])
        token = data.token + bytearray([0])
        return  numbers + pattern_code + token


 
 #      LOGOUT
 #  _________________________________
 # |     |        |     |     |     |
 # | SOF | Len    | TYPE| CRC | EOF |
 # |_____|________|_____|__X__|_____|
 #   1B      2B     1B    4B    1B    
class logout():
    def __init__(self):
        pass
    
    @staticmethod
    def write(self):
        return bytearray()
    
 #  _________________________________
 # |     |        |     |     |     |
 # | SOF |  Len   | type| CRC | EOF |
 # |_____|________|_____|__X__|_____|
 #   1B      2B     1B     2B    1B   
class ping_tuple(typing.NamedTuple):
    timens: int
    def __str__(self):
        return "Ping Tuple ver: {0}".format( self.timens )

class ping():
    endianess = f"{protocol_headers.ENDIANESS}Q" 
    def __init__(self):
        pass 
    
    @staticmethod
    def read( buff: bytearray) -> ping_tuple:
        [timens] = struct.unpack(ping.endianess, buff[0:8])
        return ping_tuple(timens)
    
    @staticmethod
    def write( data: ping_tuple):
        return struct.pack(ping.endianess, data.timens)
    



class cmd():
    endianess = f"{protocol_headers.ENDIANESS}B" 
    def __init__(self):
        self.cmd = cmd 

    @staticmethod
    def read(self, buf):
        [self.cmd] = struct.unpack(cmd.endianess, buf)

    @staticmethod
    def write(self, cmd):
        return struct.pack(cmd.endianess, cmd)
 
 #  RESPONSE
 # _________________________________________________
 # |     | Packet |      |        |		 |     |     |
 # | SOF | Len    | Type | Status |	EC	 | CRC | EOF |
 # |_____|________|______|________|______|__X__|_____|
 #   1B      2B      1B      1B      1B	    4B    1B

class response_tuple(typing.NamedTuple):
    ack: int
    ec: int

    def __str__(self):
        return "Response Tuple ack: {0}, ec {1}".format( self.ack , self.ec)

class response():
    endianess = f"{protocol_headers.ENDIANESS}BB"

    @staticmethod
    def read(buf) -> response_tuple:
        [status, ec] = struct.unpack(response.endianess, buf)
        return response_tuple(status, ec)

    @staticmethod
    def write(r: response_tuple):
        return  struct.pack(response.endianess, r.ack, r.ec)


 #  REQUEST
 #  _________________________________________
 # |     |        |      |     	 |     |     |
 # | SOF | Len    | Type |  DATA | CRC | EOF |
 # |_____|________|______|___Y___|__X__|_____|
 #   1B      2B      1B      XB     4B    1B    

class Irequest():
    @staticmethod
    def factory_read( buf: bytearray):
        rtype = buf[0]
        data = buf[1:] if len(buf) > 1 else None
        if rtype == protocol_headers.content_type.ALERTA.value:
            return [None, None]
        
        if rtype == protocol_headers.content_type.AUTHENTICATION.value:
            return [None, None]
        
        if rtype == protocol_headers.content_type.TARIFA.value:
            return [rtype, data]
        
        if rtype == protocol_headers.content_type.TICKETS.value:
            return [rtype, data]
        
        if rtype == protocol_headers.content_type.HOJA_DE_RUTA.value:
            return [rtype, data]
        
        if rtype == protocol_headers.content_type.POSICIONES.value:
            return [rtype, data]
        raise WrongType()

    @staticmethod
    def tarifaW() -> bytearray:
        return trunc_1byte(protocol_headers.packet_type.REQUEST.value) + trunc_1byte(protocol_headers.content_type.TARIFA.value) + protocol_layer_two_request.tarifa_request.write()

    @staticmethod
    def hoja_de_rutaW() -> bytearray:
        return trunc_1byte(protocol_headers.packet_type.REQUEST.value) +  trunc_1byte(protocol_headers.content_type.HOJA_DE_RUTA.value) + protocol_layer_two_request.hoja_de_ruta_request.write()

    @staticmethod
    def posicionesW() -> bytearray:
        return trunc_1byte(protocol_headers.packet_type.REQUEST.value) + trunc_1byte(protocol_headers.content_type.POSICIONES.value) + protocol_layer_two_request.posiciones_request.write()
    
    @staticmethod
    def factory_write(type: protocol_headers.content_type, buff: bytearray):
        return trunc_1byte(type) + buff

 #  DATA  
 #  _________________________________________
 # |     | Packet |     |     	|     |     |
 # | SOF | Type   | Len |  DATA | CRC | EOF |
 # |_____|________|_____|___Y___|__X__|_____|
 #   1B      1B     2B      XB     4B    1B    
class Icontent():
    @staticmethod 
    def factory_read(buf: bytearray):
        dtype = buf[0]
        data = buf[1:]
        if dtype == protocol_headers.content_type.ALERTA.value:
            return [dtype, data]
        if dtype == protocol_headers.content_type.AUTHENTICATION.value:
            return [dtype, data]
        if dtype == protocol_headers.content_type.TARIFA.value:
            return [dtype, data]
        if dtype == protocol_headers.content_type.TICKETS.value:
            return [dtype, data]
        if dtype == protocol_headers.content_type.HOJA_DE_RUTA.value:
            return [dtype, data]
        if dtype == protocol_headers.content_type.POSICIONES.value:
            return [dtype, data]
        raise WrongType()
    
    @staticmethod
    def authW( data : protocol_layer_two_content.authentication_data_tuple)->bytearray:
        buff = protocol_layer_two_content.authentication_data.write(data)
        return trunc_1byte(protocol_headers.packet_type.DATA.value) +\
               trunc_1byte(protocol_headers.content_type.AUTHENTICATION.value) + buff

    @staticmethod
    def authR( buff: bytearray) -> protocol_layer_two_content.authentication_data_tuple:
        Tauth = protocol_layer_two_content.authentication_data.read(buff)
        return Tauth

    @staticmethod
    def tarifaW(data : protocol_layer_two_content.tarifa_data_tuple):
        buff = protocol_layer_two_content.tarifa_data.write(data)
        return trunc_1byte(protocol_headers.packet_type.DATA.value) +\
               trunc_1byte(protocol_headers.content_type.TARIFA.value) + buff

    @staticmethod
    def tarifaR(buff : bytearray) -> protocol_layer_two_content.tarifa_data_tuple:
        Ttarifa = protocol_layer_two_content.tarifa_data.read(buff)
        return Ttarifa

    @staticmethod
    def hoja_de_rutaW(data : protocol_layer_two_content.hoja_de_ruta_data_tuple) -> bytearray:
        buff = protocol_layer_two_content.hoja_de_ruta_data.write(data)
        return trunc_1byte(protocol_headers.packet_type.DATA.value) +\
               trunc_1byte(protocol_headers.content_type.HOJA_DE_RUTA.value) + buff


    @staticmethod
    def hoja_de_rutaR(data : bytearray) -> protocol_layer_two_content.hoja_de_ruta_data_tuple:
        Thojaderuta = protocol_layer_two_content.hoja_de_ruta_data.read(data)
        return Thojaderuta

    @staticmethod
    def posicionesR(buff : bytearray)-> protocol_layer_two_content.posiciones_data_tuple:
        Tposiciones = protocol_layer_two_content.posiciones_data.read(buff)
        return Tposiciones
    

    @staticmethod
    def posicionesW(data : protocol_layer_two_content.posiciones_data_tuple)-> bytearray:
        buff = protocol_layer_two_content.posiciones_data.write(data)
        return trunc_1byte(protocol_headers.packet_type.DATA.value) + trunc_1byte(protocol_headers.content_type.POSICIONES.value) + buff


    @staticmethod
    def alertaR(buff: bytearray) -> protocol_layer_two_content.alerta_data_tuple:
        Talerta = protocol_layer_two_content.alerta_data.read(buff)
        return Talerta
    
    @staticmethod
    def alertaW(data: protocol_layer_two_content.alerta_data_tuple) -> bytearray:
        buff = protocol_layer_two_content.alerta_data.write(data) 
        return trunc_1byte(protocol_headers.packet_type.DATA.value) +\
               trunc_1byte(protocol_headers.content_type.ALERTA.value) + buff
                 
    
    @staticmethod
    def ticketsR(buff: bytearray) -> protocol_layer_two_content.tickets_data_tuple:
        Ttickets = protocol_layer_two_content.tickets_data.read(buff)
        return Ttickets

    @staticmethod
    def factory_write(type: protocol_headers.content_type, buff: bytearray):
        return trunc_1byte(protocol_headers.packet_type.DATA.value) + trunc_1byte(type) + buff
        
    

class Imain():
    @staticmethod
    def factory_read(buf: bytearray):
        ptype = buf[0]
        try:
            data = buf[1:]
        except IndexError:
            data = None
        
        if ptype == protocol_headers.packet_type.LOGIN.value:
            return [ ptype, data]
        if ptype == protocol_headers.packet_type.LOGOUT.value:
            return [ ptype, data]
        if ptype == protocol_headers.packet_type.PING.value:
            return [ ptype, data]
        if ptype == protocol_headers.packet_type.CMD.value:
            return [ ptype, data]
        if ptype == protocol_headers.packet_type.RESPONSE.value:
            return [ ptype, data]
        if ptype == protocol_headers.packet_type.REQUEST.value:
            return [ ptype, data]
        if ptype == protocol_headers.packet_type.DATA.value:
            return [ ptype, data]    
        raise WrongType()

    @staticmethod
    def responseW(data : response_tuple) -> bytearray:
        buff = response.write(data)
        return trunc_1byte(protocol_headers.packet_type.RESPONSE.value) + buff

    @staticmethod
    def responseR( buff: bytearray ) -> response_tuple:
        Tresponse = response.read(buff)
        return Tresponse


    @staticmethod
    def loginW( data: login_tuple) -> bytearray:
        Blogin = login.write(data)
        return trunc_1byte(protocol_headers.packet_type.LOGIN.value) + Blogin

    @staticmethod
    def loginR( buff: bytearray) -> login_tuple:
        Tlogin = login.read(buff)
        return Tlogin
    
    @staticmethod
    def logoutW( ) -> bytearray:
        return trunc_1byte(protocol_headers.packet_type.LOGOUT.value)

    @staticmethod
    def pingW( data: ping_tuple) -> bytearray:
        Bping = ping.write(data)
        return trunc_1byte(protocol_headers.packet_type.PING.value) + Bping

    @staticmethod
    def pingR( buff: bytearray) -> ping_tuple :
        Tping = ping.read(buff)
        return Tping

    @staticmethod
    def factory_write(type: protocol_headers.packet_type, buff: bytearray):
        return trunc_1byte(type) + buff
    








if __name__ == "__main__":
    buf = login.write(login_tuple(ver=1, imei=866989058568582, pattern_code=b"4053", token=b""))
    
    print(echos.bytearray2str(buf))
    buf = login.read(buf)
    print(buf)