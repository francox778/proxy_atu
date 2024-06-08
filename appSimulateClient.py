import socket
import time
import traceback
import threading
import queue

import colorama as cr
import logging
import colored_logger
import protocolV1_1.protocol_io as io
import protocolV1_1.protocol_layer_one as prtcl
import protocolV1_1.protocol_layer_two_content as content
import protocolV1_1.protocol_layer_two_request as request

import protocolV1_1.protocol_headers as prtcl_h
from translator_atu_http import ThttpRequests as thttp

import atuHttp

logger = colored_logger.Logger("main", logging.DEBUG, cr.Fore.CYAN)
#logger.add_stderr(logging.ERROR)


class InputThread(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q
    def run(self):
        while True:
            try:
                self.display_menu()
                data = input()
                logger.debug(f"debug {data}")
                self.q.put(data)
            except ValueError as e:
                logger.error(f"InputThread err: {e}")

    def display_menu(self):
        print(""" 
            INTRODUCE UNA OPCION            
            0: send login
            1: send logout
            2: send ping

            3: send alerta
            4: req tarifa
            5: send tickets
            6: req hoja de ruta
            7: req posiciones                                               
            """)


class ConnectionThread(threading.Thread):
    def __init__(self, ip, port, q):
        super().__init__()
        self.ip = ip
        self.port = port
        self.token = ""
        self.imei = ""
        self.q = q

        self.packet_type_choices = {
            prtcl_h.packet_type.LOGIN.value      : self.login_handler ,
            prtcl_h.packet_type.LOGOUT.value     : self.logout_handler ,
            prtcl_h.packet_type.PING.value       : self.ping_handler ,
            #prtcl_h.packet_type.CMD.value        : self.cmd_handler ,
            prtcl_h.packet_type.RESPONSE.value   : self.response_handler ,
            prtcl_h.packet_type.REQUEST.value    : self.request_handler ,
            prtcl_h.packet_type.DATA.value       : self.data_handler ,
        }
        self.request_type_choices = {
            prtcl_h.content_type.ALERTA.value         : self.alerta_req_handler ,
            prtcl_h.content_type.TARIFA.value         : self.tarifa_req_handler ,
            prtcl_h.content_type.TICKETS.value        : self.tickets_req_handler,
            prtcl_h.content_type.HOJA_DE_RUTA.value   : self.hoja_de_ruta_req_handler ,
            prtcl_h.content_type.POSICIONES.value     : self.posiciones_req_handler ,
        }
        self.data_type_choices = {
            prtcl_h.content_type.ALERTA.value         : self.alerta_data_handler ,
            prtcl_h.content_type.TARIFA.value         : self.tarifa_data_handler ,
            prtcl_h.content_type.TICKETS.value        : self.tickets_data_handler,
            prtcl_h.content_type.HOJA_DE_RUTA.value   : self.hoja_de_ruta_data_handler ,
            prtcl_h.content_type.POSICIONES.value     : self.posiciones_data_handler ,
            prtcl_h.content_type.AUTHENTICATION.value : self.auth_data_handler,
        }

    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.port))
            self.io = io.packet_reader(s)
            while True:
                Tlogin = prtcl.login_tuple(ver = 1,
                                          imei = 866989058568582,
                                          pattern_code = b"4053",
                                          token = b"")
                Blogin = prtcl.Imain.loginW(Tlogin)
                self.io.write(Blogin)
                try:
                    self.io.readBlocking(30.0)
                except io.ValidMessageException:
                    packet = self.io.getPacket()
                    [packet_type,  packet_data]  = prtcl.Imain.factory_read(packet)
                    if packet_type == prtcl_h.packet_type.RESPONSE.value:
                        Tresponse = prtcl.Imain.responseR(packet_data)
                        logger.debug(f"Login NACK {Tresponse.ack} {Tresponse.ec}")
                        break
                    if packet_type == prtcl_h.packet_type.DATA.value:
                        [packet_type,  packet_data]  = prtcl.Icontent.factory_read(packet_data)
                        if packet_type == prtcl_h.content_type.AUTHENTICATION.value:
                            Tauth = prtcl.Icontent.authR(packet_data)
                            self.token = Tauth.token.decode('latin-1')
                            logger.debug(f"Auth {Tauth}")
                        break
                except io.TimeOutException:
                    logger.info(f"{self.imei}  timeout2 {30}s")
                    pass
                except io.ClosedSocketException as err:
                    logger.error(f"{self.imei} Conexion cerrada!")
                    raise
                except socket.timeout as err:
                    logger.error(f"{self.imei} Conexion cerrada!")
                    raise
                except Exception as e:
                    logger.error(f"{self.imei} {e}", exc_info=True)
                finally:
                    pass
            
            # Sesion activa.
            while True:
                item = None
                try:
                    item = self.q.get(block=False)
                    self.TestSend(item)
                except queue.Empty:
                    pass
                    
                try:
                    self.io.readBlocking(3.0)
                except io.ValidMessageException:
                    packet = self.io.getPacket()
                    [packet_type,  packet_data]  = prtcl.Imain.factory_read(packet)
                    packet_type_choices = self.packet_type_choices.get(packet_type)
                    if packet_type_choices:
                        packet_type_choices(packet_data)

                except io.TimeOutException:
                    pass
                except io.ClosedSocketException as err:
                    print(f"{err}")
                    raise
                except socket.timeout as err:
                    logger.error(f"{self.imei} Conexion cerrada!")
                    raise
                except Exception as e:
                    logger.error(f"{self.imei} {e}", exc_info=True)
                finally:
                    pass

        except Exception as e:
            logger.error(f"Conexion cerrada {self.imei}, {e}")
            s.close()

    def login_handler(self, packet_data):
        # Validamos al usuario
        pass

    def logout_handler(self, packet_data):
        # Enviamos ACK
        pass

    def ping_handler(self, packet_data):
        # Enviamos ACK
        Tping = prtcl.Imain.pingR(packet_data)
        elapsed_time = int(time.time() * 1000) - Tping.timens
        logger.debug(f"{self.imei}, {elapsed_time}ms")
        Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(prtcl_h.response.ACK.value, prtcl_h.error_codes.NOT_SPECIFIED.value))     
        self.io.write(Bresponse)

    def cmd_handler(self, packet_data):
        #puede ser
        pass

    def response_handler(self, packet_data):
        Tresponse = prtcl.Imain.responseR(packet_data)
            
        if Tresponse.ack == prtcl_h.response.ACK.value:
            logger.debug(f"response_h> {self.imei}, {Tresponse}")
        else:
            logger.debug(f"response_h> {self.imei}, {Tresponse}")
    


    def request_handler(self, packet_data):
        [type, data] = prtcl.Irequest.factory_read(packet_data)
        request_type_choices = self.request_type_choices.get(type)
        if request_type_choices:
            request_type_choices(data)


    def data_handler(self, packet_data):
        [type, data] = prtcl.Icontent.factory_read(packet_data)
        data_type_choices = self.data_type_choices.get(type)
        if data_type_choices:
            data_type_choices(data)


#######################################  REQ  #####################################################
    def alerta_req_handler(self, data):
        # no hay
        pass

    def tarifa_req_handler(self, data):
        # no hay
        pass

    def tickets_req_handler(self, data):
        # no hay
        pass

    def hoja_de_ruta_req_handler(self, data):
        # no hay
        pass

    def posiciones_req_handler(self, data):
        # no hay
        pass


#######################################  DATA  #####################################################
    def alerta_data_handler(self, data):  # si hay
        #no hay 
        pass

    def tarifa_data_handler(self, data):  # no hay
        Ttarifa = prtcl.Icontent.tarifaR(data) 
        logger.debug(f"tarifa recibida... {Ttarifa}")

    def tickets_data_handler(self, data): # si hay
        logger.error(f"Data. tickets_data_handler")

    def hoja_de_ruta_data_handler(self, data):  # no hay
        Thojaderuta = prtcl.Icontent.hoja_de_rutaR(data) 
        logger.debug(f"Hoja de ruta recibida... {Thojaderuta}")

    def posiciones_data_handler(self, data):    # no hay
        Tposiciones = prtcl.Icontent.posicionesR(data) 
        logger.debug(f"posiciones recibida... {Tposiciones}")

    def auth_data_handler(self, data):
        pass


    def TestSend(self, item):
        item = int(item)
        logger.debug(f"Test Send {item}")
        """ 
            INTRODUCE UNA OPCION       
            0: send login
            1: send logout
            2: send ping

            3: send alerta
            4: req tarifa
            5: send tickets
            6: req hoja de ruta
            7: req posiciones                                               
        """
        if item == 0:
            Blogin = prtcl.Imain.loginW( prtcl.login_tuple(ver = 1, imei = 866989058568582, pattern_code = b"4053", token = b""))
            self.io.write(Blogin)

        if item == 1:
            Blogout = prtcl.Imain.logoutW()
            self.io.write(Blogout)

        if item == 2:
            Bping = prtcl.Imain.pingW( prtcl.ping_tuple(int(time.time() * 1000)))
            self.io.write(Bping)

        if item == 3:
            Balerta = prtcl.Icontent.alertaW(content.alerta_data_tuple(timestamp= int(time.time())))
            self.io.write(Balerta)
        
        if item == 4:
            Btarifa = prtcl.Irequest.tarifaW()
            self.io.write(Btarifa)

        if item == 5:
            ticket0 = content.tickets_data_tuple(1, 5, 10000000001, 654646546)
            ticket1 = content.tickets_data_tuple(1, 6, 10000000002, 654646547)
            ticket2 = content.tickets_data_tuple(1, 8, 10000000003, 654646548)
            ticket3 = content.tickets_data_tuple(1, 9, 10000000004, 654646549)
            tickets =[ ticket0, ticket1, ticket2, ticket3]
            Btickets = prtcl.Icontent.ticketsW(tickets)
            self.io.write(Btickets)

        if item == 6:
            Bhojaderuta = prtcl.Irequest.hoja_de_rutaW()
            self.io.write(Bhojaderuta)

        if item == 7:
            BPosiciones = prtcl.Irequest.posicionesW()
            self.io.write(BPosiciones)


if __name__ == "__main__":
    q = queue.Queue()
    inputThread = InputThread(q)
    connectionThread = ConnectionThread(ip='127.0.0.1', port=22222, q=q)
    #connectionThread = ConnectionThread(ip='18.229.227.108', port=60001, q=q)
    inputThread.start()
    connectionThread.start()
    inputThread.join()
    connectionThread.join()