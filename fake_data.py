import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)
    
import typing
import struct
import echos
import protocolV1_1.protocol_io as io
import protocolV1_1.protocol_layer_one as prtcl
import protocolV1_1.protocol_layer_two_content as content
import protocolV1_1.protocol_layer_two_request as request


# 0: next 1: current 2: before
posicion0 = content.posiciones_data_tuple(0, b"B3I-752", -5)
posicion1 = content.posiciones_data_tuple(0, b"BAW-915", -6)
posicion2 = content.posiciones_data_tuple(0, b"AAU-821", -7)
posicion3 = content.posiciones_data_tuple(1, b"ES UN PARADERO DE PRUEBA", -8)
posicion4 = content.posiciones_data_tuple(2, b"AHP-813", -9)
posicion5 = content.posiciones_data_tuple(2, b"BAW-914", -0)

#posicionesBuff = prtcl.Icontent.posicionesW( [posicion0, posicion1, posicion2 ,posicion3, posicion4, posicion5] )
posicionesBuff = [posicion0, posicion1, posicion2 ,posicion3, posicion4, posicion5]


# complete(3) current(2) previous(1) next(0)
paradero0 = content.hoja_de_ruta_data_tuple( b"CASABLANCA", 941, 938, 0,-2)
paradero2 = content.hoja_de_ruta_data_tuple( b"5 MARISCAL", 941, 953, 0,-30)
paradero2 = content.hoja_de_ruta_data_tuple( b"INICIO(B)", 944, 941, 1,-30)
paradero1 = content.hoja_de_ruta_data_tuple( b"MI BANCO BAYOVAR", 957, 0, 0,-30)
paradero3 = content.hoja_de_ruta_data_tuple( b"JOSE C. MARIATEGUI", 941, 951, 0,-35)

#paraderos = prtcl.Icontent.hoja_de_rutaW([ paradero0, paradero1, paradero2, paradero3])
paraderos = [ paradero0, paradero1, paradero2, paradero3]