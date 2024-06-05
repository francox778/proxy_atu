
import threading
import socket


import protocolV1_1.protocol_io as io
import protocolV1_1.protocol_layer_one as prtcl
import protocolV1_1.protocol_layer_two_content as content
import protocolV1_1.protocol_layer_two_request as request

import protocolV1_1.protocol_headers as prtcl_h
from translator_atu_http import ThttpRequests as thttp
from translator_atu_http import THttpAns, THttpError
import atuHttp
import echos

import colored_logger
import logging
import colorama as cr

logger = colored_logger.Logger("connectionThread", logging.DEBUG, cr.Fore.CYAN)
logger.add_stderr(logging.ERROR)





class ConnectionThread(threading.Thread):
    def __init__(self, sock, addr):
        super().__init__()
        self.logged = False
        self.end = False

        self.sock = sock
        self.addr = addr

        self.token = ""
        self.imei = "NN" #nomen nescio
        self.http = atuHttp.AtuHttp("https://billingws.gpstracking.pe/v1/api/")
        self.timeoutCnt = 0

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
            prtcl_h.content_type.ALERTA.value         : self.alerta_content_handler ,
            prtcl_h.content_type.TARIFA.value         : self.tarifa_content_handler ,
            prtcl_h.content_type.TICKETS.value        : self.tickets_content_handler,
            prtcl_h.content_type.HOJA_DE_RUTA.value   : self.hoja_de_ruta_content_handler ,
            prtcl_h.content_type.POSICIONES.value     : self.posiciones_content_handler ,
        }


    def run(self):
        try:
            self.io = io.packet_reader(self.sock)
            # Authenticar. si manda con token asumire que su token es valido.
            timeout = 100
            while True:
                try:
                    self.io.readBlocking(timeout)
                except io.ValidMessageException:
                    self.timeoutCnt = 0
                    packet = self.io.getPacket()
                    logger.debug(f" {echos.bytearray2str(packet)}")
                    [packet_type,  packet_data]  = prtcl.Imain.factory_read(packet)
                    packet_type_choices = self.packet_type_choices.get(packet_type)
                    if packet_type_choices:
                        packet_type_choices(packet_data)
                    else:
                        logger.error(f"invalid packet type.")
                    if self.logged:
                        break
                except prtcl.WrongType:
                    logger.error(f"NN packet type invalido")       
                except io.TimeOutException:
                    self.timeoutCnt = self.timeoutCnt + 1
                    logger.info(f"{self.imei}  timeout1 {timeout}s n:{self.timeoutCnt}x{timeout}seg")
                    if self.timeoutCnt == 10:
                        logger.info(f"{self.imei}  conexion inactiva {self.timeoutCnt}x{timeout}seg")
                        raise io.ClosedSocketException
                except io.ClosedSocketException as e:
                    #logger.error(f"{self.imei} Conexion cerrada!")
                    raise 
                except (socket.timeout, socket.gaierror) as err:
                    #logger.error(f"{self.imei} timeout Conexion cerrada!")
                    raise
                except KeyboardInterrupt:
                    raise

                except Exception as e:
                    logger.error(f"{self.imei} {e}", exc_info=True)
                finally:
                    pass
            
            # Sesion Activa
            timeout = 10
            while True:
                try:
                    self.io.readBlocking(timeout)
                except io.ValidMessageException:
                    self.timeoutCnt = 0
                    packet = self.io.getPacket()
                    logger.debug(f" {echos.bytearray2str(packet)}")
                    [packet_type,  packet_data]  = prtcl.Imain.factory_read(packet)
                    packet_type_choices = self.packet_type_choices.get(packet_type)
                    if packet_type_choices:
                        packet_type_choices(packet_data)
                    else:
                        logger.error(f"invalid packet type.")
                    if not self.logged:
                        break    
                    if self.end:
                        raise io.ClosedSocketException       
                except io.TimeOutException:
                    self.timeoutCnt = self.timeoutCnt + 1
                    logger.info(f"{self.imei}  timeout2 {timeout}s n:{self.timeoutCnt}x{timeout}seg")
                    if self.timeoutCnt == 10:
                        logger.info(f"{self.imei}  conexion inactiva {self.timeoutCnt}x{timeout}seg")
                        raise io.ClosedSocketException
                    pass
                except io.ClosedSocketException as e:
                    #logger.error(f"{self.imei} Conexion cerrada!")
                    raise
                except KeyboardInterrupt:
                    raise
                except (socket.timeout, socket.gaierror) as err:
                    #logger.error(f"{self.imei} Conexion cerrada!")
                    raise
                except Exception as e:
                    logger.error(f"{self.imei} {e}", exc_info=True)

                finally:
                    pass
        except KeyboardInterrupt:
            raise
        except io.ClosedSocketException as e:
            logger.debug(f"{self.imei} conexion_cerrada")
            raise   
        except Exception as e:
            logger.error(f"{self.imei} {e}", exc_info=True)
        finally:
            self.sock.close()
            #logger.debug(f"{self.imei} conexion_cerrada")



    def waiting_login(self):
        pass

    def active_session(self):
        pass

    
    def login_handler(self, packet_data):
        # Validamos al usuario
        Tlogin = prtcl.login.read(packet_data)
        logger.info(f"login_h> intento de conexion : imei: {Tlogin.imei}, ver: {Tlogin.ver}, token: {Tlogin.token}, pcode: {Tlogin.pattern_code}")
        self.imei = str(Tlogin.imei)
        self.token = Tlogin.token
        
        # Enviamos authenticate o NACK
        if len(Tlogin.token) > 0:
            Bdata = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.logged = True
            self.io.write(Bdata)
            logger.info(f"login_h> Usuario ya cuenta con un token, conexion automatica")
            self.http.setToken(self.token.decode('latin-1'))
            return
        try:
            Tauth = thttp.login(self.http, Tlogin)
            self.logged = True
            Bauth = prtcl.Icontent.authW(Tauth)
            self.io.write(Bauth)

            logger.info(f"login_h> {self.imei}  conexion Exitosa!")            
        except (ValueError, THttpError, THttpAns) as e:
            self.logged = False
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(Bresponse)
            logger.error(f"login_h> Error de conexion! {self.imei} {e}") 
        

    def logout_handler(self, packet_data):
        # Enviamos ACK
        self.logged = False
        Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.OK.value))
        self.io.write(Bresponse)
        self.end = True
        logger.debug(f"logout_h> {self.imei} logout recibido!")


    def ping_handler(self, packet_data):
        try:
            # Enviamos ACK
            Tping = prtcl.Imain.pingR(packet_data)
            Bping = prtcl.Imain.pingW(Tping)
            self.io.write(Bping)
            logger.debug(f"ping_h> {self.imei} {Tping.timens}ns consulta Exitosa!")
        except ValueError as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(Bresponse)
            logger.debug(f"ping_h> ERROR {e}")

    def cmd_handler(self, packet_data):
        pass

    def response_handler(self, packet_data):
        try:
            Tresponse = prtcl.Imain.responseR(packet_data)
            if Tresponse.ack == prtcl_h.response.ACK.value:
                logger.debug(f"response_h> {self.imei}, ACK,  ec: {Tresponse.ec}")
            else:
                logger.debug(f"response_h> {self.imei}, NACK, ec: {Tresponse.ec}")
        except ValueError as e:
            logger.debug(f"response_h> {self.imei}, {e}")

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
        pass

    def tarifa_req_handler(self, data):
        #tarifa.write()
        #tarifa = prtcl.data.factory_write( prtcl_h.content_type.TARIFA,data)
        try:
            Ttarifa = thttp.tarifa(self.http)
            Btarifa = prtcl.Icontent.tarifaW(Ttarifa)
            self.io.write(Btarifa)
            logger.debug(f"tarifa_h> {self.imei} consulta Exitosa!") 
        except (ValueError, THttpError, THttpAns) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(Bresponse)
            logger.error(f"tarifa_h> {self.imei} {e}") 



    def tickets_req_handler(self, data):
        #tickets = prtcl.request.factory( prtcl_h.content_type.TICKETS,data)
        #tickets.read()
        pass

    def hoja_de_ruta_req_handler(self, data):
        try:
            Thojaderuta = thttp.hoja_de_ruta(self.http)
            Bhojaderuta = prtcl.Icontent.hoja_de_rutaW(Thojaderuta)
            self.io.write(Bhojaderuta)
            logger.debug(f"hoja_h>{self.imei} ") 
        except (ValueError, THttpError, THttpAns) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(Bresponse)
            logger.error(f"hoja_h> {self.imei} {e}") 

    def posiciones_req_handler(self, data):
        try:
            Tposiciones = thttp.posiciones(self.http)
            Bposiciones = prtcl.Icontent.posicionesW(Tposiciones)
            self.io.write(Bposiciones)
            logger.debug(f"posiciones> {self.imei} consulta Exitosa!") 
        except (ValueError, THttpError, THttpAns) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(Bresponse)
            logger.error(f"posiciones> {self.imei} {e}") 


#######################################  CONTENT  #####################################################
    def alerta_content_handler(self, data):  # si hay
        try:
            Talerta = prtcl.Icontent.alertaR(data)
            http_code = thttp.alerta(self.http, Talerta)
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(Bresponse)
            logger.debug(f"alerta_h> {self.imei} envio Exitoso!") 
            
        except (ValueError, THttpError, THttpAns) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(Bresponse)
            logger.error(f"alerta_h> {self.imei} {e}")  


    def tarifa_content_handler(self, data): 
        # no hay 
        pass

    def tickets_content_handler(self, data): # si hay
        try:
            Ttickets = prtcl.Icontent.ticketsR(data)
            http_code = thttp.tickets(self.http ,Ttickets)
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(Bresponse)
            logger.debug(f"tickets_h>{self.imei} ") 
        except (ValueError, THttpError, THttpAns) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(data)
            logger.error(f"tickets_h> {self.imei} {e}")  

    def hoja_de_ruta_content_handler(self, data):  
        # no hay
        pass  

    def posiciones_content_handler(self, data):
        # no hay    
        pass

