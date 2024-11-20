
import threading
import socket
import time

import protocolV1_1.protocol_io as io
import protocolV1_1.protocol_layer_one as prtcl
import protocolV1_1.protocol_layer_two_content as content
import protocolV1_1.protocol_layer_two_request as request

import protocolV1_1.protocol_headers as prtcl_h
from translator_atu_http import ThttpRequests as thttp
from translator_atu_http import THttpAns, THttpError
import atuHttp
import echos

import db.db_interface as db
import posicionesInestabilidad
import posicionesInesParche


import colored_logger
import logging
import colorama as cr

logger = colored_logger.Logger("conn_thr", logging.DEBUG, cr.Fore.CYAN)
logger.add_stderr(logging.ERROR)

H_TXT_LEN = 9
def myfmt(log: str) -> str:
    return log.ljust(H_TXT_LEN)


class ConnectionThread(threading.Thread):
    def __init__(self, sock, addr, enable_posicion):
        super().__init__()
        self.version = 0
        self.logged = False
        self.end = False

        self.sock = sock
        self.addr = addr

        self.token = ""
        self.imei = "NN" #nomen nescio
        self.http = atuHttp.AtuHttp("https://billingws.gpstracking.pe/v1/api/")
        self.timeoutCnt = 0

        # Only for evaluate_posiciones
        self.posiciones_timer = time.perf_counter()
        self.posiciones_timeout = 15 # 100
        self.enable_posicion = enable_posicion 
        self.posiciones_inestabilidad = posicionesInestabilidad.PosicionesInestabilidad()
        # self.posiciones_prev_tuple = []
        # db
        self.db = db.globalDb


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
                    #logger.debug(f" {echos.bytearray2str(packet)}")
                    [packet_type,  packet_data]  = prtcl.Imain.factory_read(packet)
                    packet_type_choices = self.packet_type_choices.get(packet_type)
                    if packet_type_choices:
                        if packet_type != prtcl_h.packet_type.LOGIN.value:
                            logger.error(f"NN not logged")  
                            self.conexion_is_not_logged_handler(packet_data)  
                        else:
                            packet_type_choices(packet_data)
                    else:
                        logger.error(f"invalid packet type.")
                    if self.logged:
                        break
                except prtcl.WrongType:
                    logger.error(f"NN packet type invalido")       
                except io.TimeOutException:
                    self.timeoutCnt = self.timeoutCnt + 1
                    #logger.info(f"{myfmt('timeout1')}::{self.imei} timeout1 {timeout}s n:{self.timeoutCnt}x{timeout}seg")
                    if self.timeoutCnt == 10:
                        logger.info(f"{myfmt('timeout1')}::{self.imei} conexion inactiva {self.timeoutCnt}x{timeout}seg")
                        raise io.ClosedSocketException
                except BrokenPipeError as e:
                    logger.error(f"NN BrokenPipeError.")
                    raise
                except io.ClosedSocketException as e:
                    #logger.error(f"NN Conexion cerrada!")
                    raise 
                except (socket.timeout, socket.gaierror) as err:
                    #logger.error(f"NN timeout Conexion cerrada!")
                    raise
                except KeyboardInterrupt:
                    raise

                except Exception as e:
                    logger.error(f"NN {e}", exc_info=True)
                finally:
                    pass
            
            # Sesion Activa
            self.posiciones_inestabilidad.set_imei(self.imei)
            timeout = 5
            while True:
                try:
                    self.io.readBlocking(timeout)
                except io.ValidMessageException:
                    self.timeoutCnt = 0
                    packet = self.io.getPacket()
                    #logger.debug(f"{self.imei} {echos.bytearray2str(packet)}")
                    [packet_type,  packet_data]  = prtcl.Imain.factory_read(packet)
                    packet_type_choices = self.packet_type_choices.get(packet_type)
                    if packet_type_choices:
                        packet_type_choices(packet_data)
                    else:
                        logger.error(f"{myfmt('err')}::{self.imei} invalid packet type")
                    if not self.logged:
                        break    
                    if self.end:
                        raise io.ClosedSocketException   
                    self.periodic_send_posiciones()

                except io.TimeOutException:
                    self.timeoutCnt = self.timeoutCnt + 1
                    #logger.info(f"{myfmt('timeout2')}::{self.imei} {timeout}s n:{self.timeoutCnt}x{timeout}seg")
                    if self.timeoutCnt == 500:
                        logger.info(f"{myfmt('timeout2')}::{self.imei} conexion inactiva {self.timeoutCnt}x{timeout}seg")
                        raise io.ClosedSocketException
                    self.periodic_send_posiciones()

                except BrokenPipeError as e:
                    logger.error(f"{self.imei} BrokenPipeError.")
                    raise
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
            pass
        except Exception as e:
            logger.error(f"{self.imei} {e}", exc_info=True)
        finally:
            self.sock.close()
            logger.info(f"{self.imei}::conexion_cerrada") 
            #logger.debug(f"{self.imei} conexion_cerrada")


    def periodic_send_posiciones(self):
        if not self.enable_posicion:
            return
        if time.perf_counter() - self.posiciones_timer > self.posiciones_timeout:
            
            nPosiciones = self.send_posiciones()

            if nPosiciones > 0:
                self.posiciones_timer = time.perf_counter()
                self.posiciones_timeout = 12
                logger.info(f"{myfmt('pos')}::{self.imei} posiciones activo {nPosiciones}!!")
            else:
                self.posiciones_timer = time.perf_counter()
                self.posiciones_timeout = 30
                logger.info(f"{myfmt('pos')}::{self.imei} posiciones inactivo!!")

            """ # 1. interpreto la data
            Tposiciones_orig = thttp.posiciones(self.http, self.version) 
            # 2. Actualizo el estabilizador.
            #self.posiciones_inestabilidad.new_message(Tposiciones)
            
            #Tposiciones = self.posiciones_inestabilidad.position
            Tposiciones = self.posiciones_keeper.process(Tposiciones_orig)
            Bposiciones = prtcl.Icontent.posicionesW(Tposiciones)
            self.io.write(Bposiciones) 
            self.db.update_row_posiciones(self.imei, len(Bposiciones))
            # 3. Si la data del estabilizador cambio con respecto al ultimo dato que envie. hare el envio.
            #if not self.posiciones_inestabilidad.position_equal(self.posiciones_prev_tuple):
            #    Bposiciones = prtcl.Icontent.posicionesW(Tposiciones)
            #    self.io.write(Bposiciones) 
            #    self.db.update_row_posiciones(self.imei, len(Bposiciones))
            # 4. a conenction thread solo le importa comparar lo ultimo que envio!.            
            #self.posiciones_prev_tuple = Tposiciones

            # 5. si la data es 0 consultare cada 30 segundos? en lugar de 10
            if len(Tposiciones_orig) > 0:
                self.posiciones_timer = time.perf_counter()
                self.posiciones_timeout = 15
                logger.info(f"{myfmt('pos_detec')}::{self.imei} posiciones activo orig {len(Tposiciones_orig)} new {len(Tposiciones)} !!")
            else:
                self.posiciones_timer = time.perf_counter()
                self.posiciones_timeout = 30
                logger.info(f"{myfmt('pos_detec')}::{self.imei} posiciones inactivo!!") """
    


    def send_posiciones(self) -> int:
        #INTERMITENCIA.
        # 1. interpreto la data
        Tposiciones = thttp.posiciones(self.http, self.version)
        # 2. Actualizo el estabilizador.
        self.posiciones_inestabilidad.new_message(Tposiciones)

        Bposiciones = prtcl.Icontent.posicionesW(Tposiciones)
        self.io.write(Bposiciones)
        self.db.update_row_posiciones(self.imei, len(Bposiciones))
    
        for index, posicion in enumerate(Tposiciones):
            logger.debug(f"{myfmt('pos')}::{self.imei} --------------- ") 
            logger.debug(f"{myfmt('pos')}::{self.imei} - {index} {posicion.type}") 
            logger.debug(f"{myfmt('pos')}::{self.imei} - {index} {posicion.plate}") 
            logger.debug(f"{myfmt('pos')}::{self.imei} - {index} {posicion.difference}") 
        logger.debug(f"{myfmt('pos')}::{self.imei} --------------- ") 
        return len(Tposiciones)


    def waiting_login(self):
        pass

    def active_session(self):
        pass

    
    def conexion_is_not_logged_handler(self, packet_data):
        Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                        prtcl_h.response.ACK.value,
                                        prtcl_h.error_codes.CONEXION_IS_NOT_LOGGED.value))
        self.io.write(Bresponse)


    def login_handler(self, packet_data):
        # Validamos al usuario
        Tlogin = prtcl.login.read(packet_data)
        logger.info(f"{myfmt('login')}:: intento de conexion : {Tlogin}")
        self.version = Tlogin.ver
        self.imei = str(Tlogin.imei)
        self.token = Tlogin.token
        self.db.update_row_registro(self.imei)
        # Enviamos authenticate o NACK
        if len(Tlogin.token) > 0:
            Bdata = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.logged = True
            self.io.write(Bdata)
            logger.info(f"{myfmt('login')}:: Usuario ya cuenta con un token, conexion automatica")
            self.http.setToken(self.token.decode('latin-1'))
            self.db.update_row_login(self.imei, len(packet_data) + len(Bdata) + 2) # 5 ans
            return
        try:
            Tauth = thttp.login(self.http, Tlogin)
            self.logged = True
            Bauth = prtcl.Icontent.authW(Tauth)
            self.io.write(Bauth)
            logger.info(f"{myfmt('login')}::{self.imei} conexion Exitosa!")       
            self.db.update_row_login(self.imei, len(packet_data) + len(Bauth) + 2)

        except (ValueError, THttpError, THttpAns) as e:
            self.logged = False
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.ID_ERRONEO.value))
            self.io.write(Bresponse)
            logger.error(f"{myfmt('login')}::{self.imei} Error de conexion! {e}") 
            self.db.update_row_response(self.imei, len(Bresponse) + 2)

    def logout_handler(self, packet_data):
        # Enviamos ACK
        self.db.update_row_logout(self.imei, len(packet_data) + 2) # 5 ans
        self.logged = False
        Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.OK.value))
        self.io.write(Bresponse)
        self.end = True
        logger.info(f"{myfmt('logout')}::{self.imei} recibido!")


    def ping_handler(self, packet_data):
        try:
            # Enviamos ACK
            Tping = prtcl.Imain.pingR(packet_data)
            Bping = prtcl.Imain.pingW(Tping)
            self.io.write(Bping)
            logger.info(f"{myfmt('ping')}::{self.imei} {Tping.timens}ms consulta Exitosa!")
            self.db.update_row_ping(self.imei, len(packet_data)+ len(Bping) + 2) # 5 ans
        except ValueError as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.OK.value))
            self.io.write(Bresponse)
            logger.info(f"{myfmt('ping')}::{self.imei} ERROR {e}")
            self.db.update_row_response(self.imei, len(Bresponse) + 2)

    def cmd_handler(self, packet_data):
        pass

    def response_handler(self, packet_data):
        self.db.update_row_response(self.imei, len(packet_data))
        try:
            self.db.update_row_response(self.imei, 5)
            Tresponse = prtcl.Imain.responseR(packet_data)
            if Tresponse.ack == prtcl_h.response.ACK.value:
                logger.info(f"{myfmt('response')}::{self.imei}, ACK, ec: {Tresponse.ec}")
            else:
                logger.info(f"{myfmt('response')}::{self.imei}, NACK, ec: {Tresponse.ec}")
        except ValueError as e:
            logger.error(f"{myfmt('response')}::{self.imei}, {e}")

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
            logger.info(f"{myfmt('tarifa')}::{self.imei} consulta Exitosa!") 
            self.db.update_row_tarifa(self.imei,  len(Btarifa) + 4)
        except THttpAns as e:
            self.end = True
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.VUELVE_A_CONECTAR.value))
            self.io.write(Bresponse)
            logger.info(f"{myfmt('tarifa')}::{self.imei} Vuelve a conectar! {e}") 
            self.db.update_row_response(self.imei, len(Bresponse) + 4)
        except (ValueError, THttpError) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.TARIFA_ERROR.value))
            self.io.write(Bresponse)
            logger.error(f"{myfmt('tarifa')}::{self.imei} {e}") 
            self.db.update_row_response(self.imei, len(Bresponse) + 4)



    def tickets_req_handler(self, data):
        #tickets = prtcl.request.factory( prtcl_h.content_type.TICKETS,data)
        #tickets.read()
        pass

    def hoja_de_ruta_req_handler(self, data):
        try:
            Thojaderuta = thttp.hoja_de_ruta(self.http)
            Bhojaderuta = prtcl.Icontent.hoja_de_rutaW(Thojaderuta)
            self.io.write(Bhojaderuta)
            logger.info(f"{myfmt('hoja')}::{self.imei} consulta Exitosa! {len(Thojaderuta)}") 
            self.db.update_row_hoja_de_ruta(self.imei, len(Bhojaderuta) + 2)
        except THttpAns as e:
            self.end = True
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.VUELVE_A_CONECTAR.value))
            self.io.write(Bresponse)
            logger.error(f"{myfmt('hoja')}::{self.imei} Vuelve a conectar! {e}")   
            self.db.update_row_response(self.imei, len(Bresponse) + 4)

        except (ValueError, THttpError, THttpAns) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.HOJA_DE_RUTA_ERROR.value))
            self.io.write(Bresponse)
            logger.error(f"{myfmt('hoja')}::{self.imei} {e}") 
            self.db.update_row_response(self.imei, len(Bresponse) + 4)


    def posiciones_req_handler(self, data):
        try:
            logger.info(f"{myfmt('pos')}::{self.imei} req from device handler") 
            self.send_posiciones()
        except THttpAns as e:
            self.end = True
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.VUELVE_A_CONECTAR.value))
            self.io.write(Bresponse)
            logger.error(f"{myfmt('hoja')}::{self.imei} Vuelve a conectar! {e}")  
            self.db.update_row_response(self.imei, len(Bresponse) + 4)
        except (ValueError, THttpError, THttpAns) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.POSICIONES_ERROR.value))
            self.io.write(Bresponse)
            logger.error(f"{myfmt('pos')}::{self.imei} {e}") 
            self.db.update_row_response(self.imei, len(Bresponse) + 4)

#######################################  CONTENT  #####################################################
    def alerta_content_handler(self, data):  # si hay
        self.db.update_row_alerta(self.imei, len(data) + 2)
        try:
            Talerta = prtcl.Icontent.alertaR(data)
            http_code = thttp.alerta(self.http, Talerta)
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.ALERTA_ENVIADA.value))
            self.io.write(Bresponse)
            logger.info(f"{myfmt('alerta')}::{self.imei} envio Exitoso!") 
            self.db.update_row_response(self.imei, len(Bresponse) + 2)
        except THttpAns as e:
            self.end = True
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.VUELVE_A_CONECTAR.value))
            self.io.write(Bresponse)
            logger.info(f"{myfmt('alerta')}::{self.imei} Vuelve a conectar! {e}")    
            self.db.update_row_response(self.imei, len(Bresponse) + 2) 
        except (ValueError, THttpError) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.ALERTA_NO_ENVIADA.value))
            self.io.write(Bresponse)
            logger.error(f"{myfmt('alerta')}::{self.imei} {e}")  
            self.db.update_row_response(self.imei, len(Bresponse) + 2) 

    def tarifa_content_handler(self, data): 
        # no hay 
        pass

    def tickets_content_handler(self, data): # si hay
        self.db.update_row_tickets(self.imei, len(data) + 2) 
        try:
            Ttickets = prtcl.Icontent.ticketsR(data)
            http_code = thttp.tickets(self.http ,Ttickets)
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.TICKETS_RECIBIDOS.value))
            self.io.write(Bresponse)
            logger.info(f"{myfmt('tickets')}::{self.imei} tickets recibidos {len(Ttickets)}") 
            self.db.update_row_response(self.imei, len(Bresponse) + 2)
        except THttpAns as e:
            self.end = True
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.ACK.value,
                                                    prtcl_h.error_codes.VUELVE_A_CONECTAR.value))
            self.io.write(Bresponse)
            logger.error(f"{myfmt('tickets')}::{self.imei} Vuelve a conectar! {e}")     
            self.db.update_row_response(self.imei, len(Bresponse) + 2)
        except (ValueError, THttpError) as e:
            Bresponse = prtcl.Imain.responseW(prtcl.response_tuple(
                                                    prtcl_h.response.NACK.value,
                                                    prtcl_h.error_codes.TICKETS_RECIBIDOS_ERROR.value))
            self.io.write(data)
            logger.error(f"{myfmt('tickets')}::{self.imei} {e}")  
            self.db.update_row_response(self.imei, len(Bresponse) + 2)

    def hoja_de_ruta_content_handler(self, data):
        # no hay
        pass  

    def posiciones_content_handler(self, data):
        # no hay    
        pass

