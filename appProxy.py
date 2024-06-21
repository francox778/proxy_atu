from CONFIG import App

import dbsqlite.db_interface as db


import colored_logger
import logging
import colorama as cr
import acceptor_thread

logger = colored_logger.Logger("main", logging.DEBUG, cr.Fore.CYAN)
logger.add_stderr(logging.ERROR)


if __name__ == "__main__":
    logger.info("==========******* APLICACION INICIADA ********==========")
    ENVIROMENT = App.config().get(section="ENVIROMENT", option="ENVIROMENT")
    ACCEPTOR_IP = App.config().get(section=ENVIROMENT, option="IP")
    ACCEPTOR_PORT = App.config().getint(section=ENVIROMENT, option="PORT")
    logger.info(f"conf IP:{ACCEPTOR_IP} PORT:{ACCEPTOR_PORT}")
    
    ENABLE_DB = App.config().getboolean(section=ENVIROMENT, option="ENABLE_DB")
    REGISTRO_DB = App.config().get(section=ENVIROMENT, option="REGISTRO_DB")
    POSICIONES_DB = App.config().get(section=ENVIROMENT, option="POSICIONES_DB")
    LOGIN_DB = App.config().get(section=ENVIROMENT, option="LOGIN_DB")
    LOGOUT_DB = App.config().get(section=ENVIROMENT, option="LOGOUT_DB")
    RESPONSE_DB = App.config().get(section=ENVIROMENT, option="RESPONSE_DB")
    PING_DB = App.config().get(section=ENVIROMENT, option="PING_DB")
    TICKETS_DB = App.config().get(section=ENVIROMENT, option="TICKETS_DB")
    TARIFA_DB = App.config().get(section=ENVIROMENT, option="TARIFA_DB")
    HOJA_DE_RUTA_DB = App.config().get(section=ENVIROMENT, option="HOJA_DE_RUTA_DB")
    DBNAME = App.config().get(section=ENVIROMENT, option="DBNAME")
    ALERTA_DB = App.config().get(section=ENVIROMENT, option="ALERTA_DB")
    ENABLE_POSICION = App.config().getboolean(section=ENVIROMENT, option="ENABLE_POSICION")
    CLEAN_DB = App.config().getboolean(section=ENVIROMENT, option="CLEAN_DB")
    
    dbCredentials = {
        "registro" : REGISTRO_DB,
        "posiciones" : POSICIONES_DB, 
        "login" : LOGIN_DB,
        "logout" : LOGOUT_DB,
        "ping": PING_DB,
        "response": RESPONSE_DB,
        "tickets" : TICKETS_DB,
        "tarifa" : TARIFA_DB,
        "hoja_de_ruta" : HOJA_DE_RUTA_DB,
        "alerta" : ALERTA_DB,
        "dbname" : DBNAME
    }
    logger.info(f"""
ENABLE_DB: {ENABLE_DB}, 
CLEAN_DB {CLEAN_DB}
ENABLE_POSICION {ENABLE_POSICION}
{dbCredentials}""")
    
    db.enable(ENABLE_DB)
    db = db.IDb(**dbCredentials)
    db.create_table_registro(CLEAN_DB)
    db.create_table_posiciones(CLEAN_DB)
    db.create_table_login(CLEAN_DB)
    db.create_table_logout(CLEAN_DB)
    db.create_table_response(CLEAN_DB)
    db.create_table_tickets(CLEAN_DB)
    db.create_table_tarifa(CLEAN_DB)
    db.create_table_hoja_de_ruta(CLEAN_DB)
    db.create_table_ping(CLEAN_DB)
    db.create_table_alerta(CLEAN_DB)
    db.close()
    try:
        acceptor = acceptor_thread.AcceptorThread(ACCEPTOR_IP, ACCEPTOR_PORT, ENABLE_POSICION, dbCredentials)
        acceptor.start()
        acceptor.join()
    except KeyboardInterrupt:
        logger.debug("CTRL+C close")
        exit(1)
        