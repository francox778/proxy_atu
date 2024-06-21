import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)
    

import dbsqlite.sqlite_interface as sqlite_interface
import datetime
# Create a connection pool
import colored_logger
import logging
import colorama as cr
import sqlite3

logger = colored_logger.Logger("ISqlite", logging.DEBUG, cr.Fore.CYAN)
logger.add_stderr(logging.ERROR)


def enable(enable: bool):
    global enabledb
    enabledb = enable

def enable_decorator(func):
    def wrapper(*args, **kwargs):
        if enabledb:
            return func(*args, **kwargs)
    return wrapper


class IDb(sqlite_interface.ISqlite):
    def __init__(self, registro, posiciones, login, logout, ping, alerta, response, tickets, tarifa, hoja_de_ruta , dbname):
        super().__init__(dbname)
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
        self.create_table(f'''CREATE TABLE {self.registro} (
                    imei INTEGER PRIMARY KEY,
                    last_connection DATE
                  )''')
        if clean:
            self.insert(f'DELETE FROM {self.registro};')


    @enable_decorator
    def create_table_posiciones(self, clean : bool = False):
        self.create_table(f'''CREATE TABLE {self.posiciones} (
                    date DATE PRIMARY KEY,
                    imei INTEGER,
                    bytes INTEGER,
                    counter INTEGER,
                    last_update DATE,
                    FOREIGN KEY (imei) REFERENCES {self.registro}(imei)
                  )''')
        if clean:
            self.insert(f'DELETE FROM {self.posiciones};')

    @enable_decorator
    def create_table_login(self, clean : bool = False):
        self.create_table(f'''CREATE TABLE {self.login} (
            date DATE PRIMARY KEY,
            imei INTEGER,
            bytes INTEGER,
            counter INTEGER,
            last_update DATE,
            FOREIGN KEY (imei) REFERENCES {self.registro}(imei)
            )''')
        if clean:
            self.insert(f'DELETE FROM {self.login};')

    @enable_decorator
    def create_table_tickets(self, clean : bool = False):
        self.create_table(f'''CREATE TABLE {self.tickets} (
            date DATE PRIMARY KEY,
            imei INTEGER,
            bytes INTEGER,
            counter INTEGER,
            last_update DATE,
            FOREIGN KEY (imei) REFERENCES {self.registro}(imei)
            )''')
        if clean:
            self.insert(f'DELETE FROM {self.tickets};')

    @enable_decorator
    def create_table_logout(self, clean : bool = False):
        self.create_table(f'''CREATE TABLE {self.logout} (
            date DATE PRIMARY KEY,
            imei INTEGER,
            bytes INTEGER,
            counter INTEGER,
            last_update DATE,
            FOREIGN KEY (imei) REFERENCES {self.registro}(imei)
            )''')
        if clean:
            self.insert(f'DELETE FROM {self.logout};')

    @enable_decorator
    def create_table_ping(self, clean : bool = False):
        self.create_table(f'''CREATE TABLE {self.ping} (
            date DATE PRIMARY KEY,
            imei INTEGER,
            bytes INTEGER,
            counter INTEGER,
            last_update DATE,
            FOREIGN KEY (imei) REFERENCES {self.registro}(imei)
            )''')
        if clean:
            self.insert(f'DELETE FROM {self.ping};')

    @enable_decorator
    def create_table_alerta(self, clean : bool = False):
        self.create_table(f'''CREATE TABLE {self.alerta} (
            date DATE PRIMARY KEY,
            imei INTEGER,
            bytes INTEGER,
            counter INTEGER,
            last_update DATE,
            FOREIGN KEY (imei) REFERENCES {self.registro}(imei)
            )''')
        if clean:
            self.insert(f'DELETE FROM {self.alerta};')

    @enable_decorator
    def create_table_response(self, clean : bool = False):
        self.create_table(f'''CREATE TABLE {self.response} (
            date DATE PRIMARY KEY,
            imei INTEGER,
            bytes INTEGER,
            counter INTEGER,
            last_update DATE,
            FOREIGN KEY (imei) REFERENCES {self.registro}(imei)
            )''')
        if clean:
            self.insert(f'DELETE FROM {self.response};')

    @enable_decorator
    def create_table_tarifa(self, clean : bool = False):
        self.create_table(f'''CREATE TABLE {self.tarifa} (
            date DATE PRIMARY KEY,
            imei INTEGER,
            bytes INTEGER,
            counter INTEGER,
            last_update DATE,
            FOREIGN KEY (imei) REFERENCES {self.registro}(imei)
            )''')
        if clean:
            self.insert(f'DELETE FROM {self.tarifa};')

    @enable_decorator
    def create_table_hoja_de_ruta(self, clean : bool = False):
        self.create_table(f'''CREATE TABLE {self.hoja_de_ruta} (
            date DATE PRIMARY KEY,
            imei INTEGER,
            bytes INTEGER,
            counter INTEGER,
            last_update DATE,
            FOREIGN KEY (imei) REFERENCES {self.registro}(imei)
            )''')
        if clean:
            self.insert(f'DELETE FROM {self.hoja_de_ruta};')

    # todas las conexiones son en tiempo real asi que aqui pondre lo normal.
    @enable_decorator
    def update_row(self, imei:int, nbytes: int, filename: str):
        with self.ctx() as cursor:
            now = datetime.datetime.now()
            now_only_date = now.strftime('%Y-%m-%dT00:00:00')
            now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            row = self.read(f'SELECT * FROM {filename} WHERE imei = ? and date = ?', imei, now_only_date, cursor=cursor)
            if row:
                cbytes = row[0][2] + nbytes
                counter = row[0][3] + 1
                self.insert(f'UPDATE {filename} SET bytes = ?, counter = ?, last_update = ? WHERE date = ?', cbytes, counter, now, now_only_date, cursor=cursor)
            else:
                cbytes = nbytes
                counter = 1
                
                self.insert(f'INSERT INTO {filename} (date, imei, bytes, counter, last_update) VALUES (?, ?, ?, ?, ?)', now_only_date, imei, cbytes, counter, now,cursor=cursor)

    @enable_decorator
    def update_row_registro(self, imei:int):
        with self.ctx() as cursor:
            now = datetime.datetime.now()
            now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            row = self.read(f'SELECT * FROM {self.registro} WHERE imei = ?', imei, cursor=cursor)
            if row:
                self.insert(f'UPDATE {self.registro} SET last_connection = ? WHERE imei= ?', now, imei)
            else:
                self.insert(f'INSERT INTO {self.registro} (imei, last_connection) VALUES (?, ?)', imei, now, cursor=cursor)

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

    @enable_decorator
    def close(self):
        self.close_connection()
        
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
