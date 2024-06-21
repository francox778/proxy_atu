import colored_logger

import threading
import colorama as cr
import logging
import socket
import connection_thread

import protocolV1_1.protocol_io as io

logger = colored_logger.Logger("acc_thr", logging.DEBUG, cr.Fore.GREEN)
logger.add_stderr(logging.ERROR)

class AcceptorThread(threading.Thread):
    def __init__(self, ip, port, enable_posicion, dbCredentials):
        super().__init__()
        self.ip = ip
        self.port = port
        self.dbCredentials = dbCredentials
        self.enable_posicion = enable_posicion

    def run(self):
        logger.info("iniciado")
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((self.ip, self.port))
        lsock.listen()
        try:
            while True:
                conn, addr = lsock.accept()
                logger.debug(f"nueva conexion {addr}")
                conn.settimeout(100)
                conn.setblocking(False)
                connection = connection_thread.ConnectionThread(conn, addr, self.enable_posicion, self.dbCredentials)
                connection.start()
        except KeyboardInterrupt:
            raise
        except io.ClosedSocketException as e:
            pass
        except Exception as err:
            logger.error(f"{err}", exc_info=True) 


