import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)
    

import protocol_headers

class ProtocolChoices():
    def __init__(self, http):
        self.http = http
        self.packet_type_choices = {
            protocol_headers.packet_type.LOGIN.value      : self.login_handler ,
            protocol_headers.packet_type.LOGOUT.value     : self.logout_handler ,
            protocol_headers.packet_type.PING.value       : self.ping_handler ,
            #protocol_headers.packet_type.CMD.value        : self.cmd_handler ,
            protocol_headers.packet_type.RESPONSE.value   : self.response_handler ,
            protocol_headers.packet_type.REQUEST.value    : self.request_handler ,
            protocol_headers.packet_type.DATA.value       : self.data_handler ,
        }

        self.request_type_choices = {
            protocol_headers.content_type.ALERTA.value         : self.alerta_req_handler ,
            protocol_headers.content_type.TARIFA.value         : self.tarifa_req_handler ,
            protocol_headers.content_type.TICKETS.value        : self.tickets_req_handler,
            protocol_headers.content_type.HOJA_DE_RUTA.value   : self.hoja_de_ruta_req_handler ,
            protocol_headers.content_type.POSICIONES.value     : self.posiciones_req_handler ,
        }

        self.data_type_choices = {
            protocol_headers.content_type.ALERTA.value         : self.alerta_data_handler ,
            protocol_headers.content_type.TARIFA.value         : self.tarifa_data_handler ,
            protocol_headers.content_type.TICKETS.value        : self.tickets_data_handler,
            protocol_headers.content_type.HOJA_DE_RUTA.value   : self.hoja_de_ruta_data_handler ,
            protocol_headers.content_type.POSICIONES.value     : self.posiciones_data_handler ,
        }