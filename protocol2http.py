from protocolV1_1.protocol_layer_two_content import *
from protocolV1_1.protocol_layer_one import *
import datetime
#
# auth_json.get('datas',{}).get('user', {}).get('name')
import logging
import colorama as cr
import colored_logger

# auth_json.get('datas',{}).get('user', {}).get('name')
logger = colored_logger.Logger("pro2http", logging.DEBUG, cr.Fore.RED)
logger.add_stderr(logging.ERROR)


class protocol2http():
    @staticmethod
    def login( data: login_tuple) -> dict:
        return {"pattern_code": data.pattern_code.decode('latin-1'), "id": str(data.imei)}
    

    @staticmethod
    def alerta(timestamp: int) -> dict:
        return {"timestamp": timestamp}
    
    @staticmethod
    def hoja_de_ruta() -> dict:
        return dict()

    @staticmethod
    def posiciones() -> dict:
        return dict()
    
    @staticmethod
    def tarifa() -> dict:
        return dict()
    
    @staticmethod
    def tickets( tickets: "list[tickets_data_tuple]" )-> dict:
        result = dict()
        #payed  
        payed = []
        #candeled
        canceled = []
        for ticket in tickets:
            ticketDict = {
                "tariff_id": ticket.tariff_id,
                "ticket"   : ticket.ticket_n,
                "timestamp": ticket.timestamp
            } 
            if ticket.type == 1:
                payed.append(ticketDict)
            else:
                canceled.append(ticketDict)

        result.update({"payed": payed})
        result.update({"canceled": canceled})
        return result
    


if __name__ == "__main__":
    l = login_tuple(1.1, 564165416, "g1234", "asdasdasdasasdas")
    login = protocol2http.login(l)
    print(login)

    alerta = protocol2http.alerta("6666558899412")
    print(alerta)

    ticket0 = tickets_data_tuple(1, 5, 10000000001, 654646546)
    ticket1 = tickets_data_tuple(1, 6, 10000000002, 654646547)
    ticket2 = tickets_data_tuple(1, 8, 10000000003, 654646548)
    ticket3 = tickets_data_tuple(1, 9, 10000000004, 654646549)
    tickets = [ ticket0, ticket1, ticket2, ticket3]
    tickets = protocol2http.tickets(tickets)
    print(tickets)