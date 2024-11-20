import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)

import struct
import typing
import protocolV1_1.protocol_io as io
import protocolV1_1.protocol_headers as protocol_headers
import protocolV1_1.protocol_layer_one as prtcl
import protocolV1_1.protocol_layer_two_request as protocol_layer_two_request  
import protocolV1_1.protocol_layer_two_content as protocol_layer_two_content

from protocolV1_1.utils import trunc_byte
import echos



if __name__ == "__main__":
    layer_zero = io.packet_reader
    authentication = protocol_layer_two_content.authentication_data_tuple(    
                name =          b'name',
                lastname =      b'lastname',
                doc_number =    b'doc_number',
                pattern_code =  b'pattern_code',
                route_code =    b'route_code',
                name_company =  b'name_company',
                logo =          b'logo',
                ruc =           b'ruc',
                ruc_soat =      b'ruc_soat',
                policy =        b'policy',
                company =       b'company',
                token=          b'1561565165169196165161651616',
                ticket_init =   10000000001,
                from_time =     1200,
                to_time =       1500)
    #Bauth = protocol_layer_two_content.authentication_data.write(authentication) #en bytes
    Bauth = prtcl.Icontent.authW(authentication)
    Bauth = layer_zero.writeBuff(Bauth)
    print( echos.bytearray2str(Bauth) )

    tarifa0 = protocol_layer_two_content.tarifa_data_tuple(
                id = 1, 
                type = 1, 
                ticket_type = 0, 
                value = 100,
                ticket_description = b"Escolar"
                )
    tarifa1 = protocol_layer_two_content.tarifa_data_tuple(
                id = 2, 
                type = 1, 
                ticket_type = 0, 
                value = 150,
                ticket_description = b"Zonal/Social"
                ) 
    tarifa2 = protocol_layer_two_content.tarifa_data_tuple(
                id = 2, 
                type = 1, 
                ticket_type = 0, 
                value = 200,
                ticket_description = b"Urbano"
                )    
    tarifa3 = protocol_layer_two_content.tarifa_data_tuple(
                id = 2, 
                type = 1, 
                ticket_type = 0, 
                value = 250,
                ticket_description = b"Interurbano"
                )        
    tarifa = [ tarifa0, tarifa1, tarifa2, tarifa3 ]

    Btarifa = prtcl.Icontent.tarifaW(tarifa)
    Btarifa = layer_zero.writeBuff(Btarifa)
    print( echos.bytearray2str(Btarifa) )