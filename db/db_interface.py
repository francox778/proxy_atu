import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)
    

import db.psql_interface as psql_interface
import datetime
# Create a connection pool
import colored_logger
import logging
import colorama as cr


logger = colored_logger.Logger("ISqlite", logging.DEBUG, cr.Fore.CYAN)
logger.add_stderr(logging.ERROR)


def init(enable: bool, **credentials):
    global enabledb
    global globalDb
    enabledb = enable
    globalDb = IDb(**credentials)
def enable_decorator(func):
    def wrapper(*args, **kwargs):
        if enabledb:
            return func(*args, **kwargs)
    return wrapper


class IDb(psql_interface.Postgresql):
    def __init__(self, registro, posiciones, login, logout, ping, alerta, response, tickets, tarifa, hoja_de_ruta , **kwargs):
        super().__init__(**kwargs)
        self.registro = registro
        self.posiciones = posiciones
        self.login = login
        self.logout = logout
        self.ping = ping
        self.alerta = alerta
        self.response = response
        self.tickets = tickets
        self.tarifa = tarifa
        self.hoja_de_ruta = hoja_de_ruta


    @enable_decorator
    def create_table_registro(self, clean : bool = False):
        self.insert(f"SET CONSTRAINTS ALL DEFERRED;")
        if self._check_table_existance(self.registro):
            logger.info(f"ya existe {self.registro}")
            return
        try:
            self.insert(f'''CREATE TABLE {self.registro} (
                        imei BIGINT PRIMARY KEY,
                        last_connection TIMESTAMP
                    )''')
            if clean:
                self.sqlite.insert(f'DELETE FROM {self.registro};')
        except:
            pass



    def _check_table_existance(self, tablename: str):     
        presence = self.read(f"""	SELECT EXISTS (
                                SELECT 1
                                FROM pg_tables
                                WHERE schemaname = 'public'
                                AND tablename = '{tablename}'
                            );""")
        return presence[0][0]
        
    def _create_table(self, table_name, registro ,clean : bool = False ):
        
        if self._check_table_existance(table_name):
            logger.info(f"ya existe {table_name}")
            return
        try:
            self.insert(f'''CREATE TABLE {table_name} (
                    id BIGSERIAL PRIMARY KEY,
                    date DATE,
                    imei BIGINT,
                    bytes BIGINT,
                    counter BIGINT,
                    last_update TIMESTAMP,
                    FOREIGN KEY (imei) REFERENCES {registro}(imei)
                    )''')
            if clean:
                self.insert(f'DELETE FROM {table_name};')
        except:
            pass

    @enable_decorator
    def create_table_posiciones(self, clean : bool = False):
        self._create_table(self.posiciones, self.registro, clean)

    @enable_decorator
    def create_table_login(self, clean : bool = False):
        self._create_table(self.login, self.registro, clean)

    @enable_decorator
    def create_table_tickets(self, clean : bool = False):
        self._create_table(self.tickets, self.registro, clean)

    @enable_decorator
    def create_table_logout(self, clean : bool = False):
        self._create_table(self.logout, self.registro, clean)

    @enable_decorator
    def create_table_ping(self, clean : bool = False):
        self._create_table(self.ping, self.registro, clean)

    @enable_decorator
    def create_table_alerta(self, clean : bool = False):
        self._create_table(self.alerta, self.registro, clean)

    @enable_decorator
    def create_table_response(self, clean : bool = False):
        self._create_table(self.response, self.registro, clean)

    @enable_decorator
    def create_table_tarifa(self, clean : bool = False):
        self._create_table(self.tarifa, self.registro, clean)

    @enable_decorator
    def create_table_hoja_de_ruta(self, clean : bool = False):
        self._create_table(self.hoja_de_ruta, self.registro, clean)

    # todas las conexiones son en tiempo real asi que aqui pondre lo normal.
    @enable_decorator
    def update_row(self, imei:int, nbytes: int, filename: str):

        now = datetime.datetime.now()
        now_only_date = now.strftime('%Y-%m-%dT00:00:00')
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        row = self.read(f'SELECT * FROM {filename} WHERE imei = %s and date = %s', imei, now_only_date)
        if row:
            cbytes = row[0][3] + nbytes
            counter = row[0][4] + 1
            self.insert(f'UPDATE {filename} SET bytes = %s, counter = %s, last_update = %s WHERE date = %s AND imei = %s', cbytes, counter, now, now_only_date, imei)
        else:
            cbytes = nbytes
            counter = 1             
            self.insert(f'INSERT INTO {filename} (date, imei, bytes, counter, last_update) VALUES (%s, %s, %s, %s, %s)', now_only_date, imei, cbytes, counter, now)

    @enable_decorator
    def update_row_registro(self, imei:int):
        now = datetime.datetime.now()
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        row = self.read(f'SELECT * FROM {self.registro} WHERE imei = %s', imei)
        if row:
            self.insert(f'UPDATE {self.registro} SET last_connection = %s WHERE imei= %s', now, imei)
        else:
            self.insert(f'INSERT INTO {self.registro} (imei, last_connection) VALUES (%s, %s)', imei, now)

    @enable_decorator
    def update_row_posiciones(self, imei:int, nbytes: int):
        self.update_row(imei, nbytes, self.posiciones)

    @enable_decorator
    def update_row_login(self, imei:int, nbytes: int):
        self.update_row(imei, nbytes, self.login)

    @enable_decorator
    def update_row_logout(self, imei:int, nbytes: int):
        self.update_row(imei, nbytes, self.logout)

    @enable_decorator
    def update_row_tickets(self, imei:int, nbytes: int):
        self.update_row(imei, nbytes, self.tickets)

    @enable_decorator
    def update_row_tarifa(self, imei:int, nbytes: int):
        self.update_row(imei, nbytes, self.tarifa)

    @enable_decorator
    def update_row_hoja_de_ruta(self, imei:int, nbytes: int):
        self.update_row(imei, nbytes, self.hoja_de_ruta)

    @enable_decorator
    def update_row_ping(self, imei:int, nbytes: int):
        self.update_row(imei, nbytes, self.ping)

    @enable_decorator
    def update_row_response(self, imei:int, nbytes: int):
        self.update_row(imei, nbytes, self.response)

    @enable_decorator
    def update_row_alerta(self, imei:int, nbytes: int):
        self.update_row(imei, nbytes, self.alerta)


        
if __name__ == "__main__":
    idb = IDb(  registro ="registro",
                posiciones ="posiciones", 
                login ="login",
                tickets = "tickets",
                tarifa = "tarifa",
                hoja_de_ruta = "hoja_de_ruta" ,
                response = "response",
                dbname = "prueba.db")
    idb.create_table_registro()
    idb.create_table_posiciones()
    idb.create_table_login()
    idb.create_table_logout()
    idb.create_table_tickets()
    idb.create_table_tarifa()
    idb.create_table_hoja_de_ruta()
    idb.create_table_ping()
    idb.create_table_alerta()
    idb.create_table_response()

    idb.update_row_registro(66666666666)
    idb.update_row_registro(77777777777)
    idb.update_row_registro(888888888888)
    idb.update_row_registro(99999999999)
    idb.update_row_registro(55555555555)
    idb.update_row_registro(4444444444)

    for i in range(5):
        idb.update_row_registro(66666666666)
        idb.update_row_posiciones(77777777777, 7)
        idb.update_row_login(888888888888, 8)
        idb.update_row_tickets(99999999999, 9)
        idb.update_row_tarifa(55555555555, 5)
        idb.update_row_hoja_de_ruta(4444444444, 4)
