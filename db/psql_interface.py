
from encodings import utf_8
import psycopg2
from psycopg2 import pool
import threading

import colored_logger 
import logging
import colorama as cr
from contextlib import contextmanager
import os

logger = colored_logger.Logger("psql", logging.DEBUG, cr.Fore.CYAN)
logger.add_stderr(level=logging.ERROR)

"""
README.md
    Conexion a postgres mediante un ThreadedConnectionPool.
    un cursor se puede obtener a partir de una conexion sin demora.
    insert(self, cmd)           -> 
    insert(self, cmd, *args):   ->
    read(self, cmd):            ->
    read(self, cmd, *args)      ->
    @contextmanager
        def ctx(self):          -> Permite abrir una conexion, y realizar varios read and writes sin pedir nueva conexion.
                                En teoria no habria necesidad de dar esta facilidad, porque al usar el threadpool se hace rapido
                                porque no hay necesidad de "crear" nuevas conexiones.

MODO DE USO:
    Es la clase base, colabora con la clase "db", la clase "db" implementa todo lo necesario para el proyecto.
    Colabora con "loadDb.py" este es la implementacion de metodos.                                
                                
                                
                                
"""





class Postgresql():
    def __init__(self, **kwargs):
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(20, 40, **kwargs

#                        host= os.environ.get("HOST") if not os.environ.get("HOST") else '127.0.0.1',
#                        user= os.environ.get("USER") if not os.environ.get("USER") else 'postgres',
#                        password= os.environ.get("PASSWORD") if not os.environ.get("PASSWORD") else '1234',
#                        database= os.environ.get("DATABASE") if not os.environ.get("DATABASE") else"test",
            )
        except psycopg2.OperationalError as err:
            logger.error( "init", err, exc_info=True)
            raise err

        
    def insert(self, cmd, *args):
        try:
            connection = self.pool.getconn()
            cursor = connection.cursor()
            cursor.execute(cmd, args)
            connection.commit()
        except psycopg2.Error as err:
            logger.error("fail insert %s -> %s", cmd, err)
            raise err
        finally:
            cursor.close()  
            self.pool.putconn(connection)
    
    def read(self, cmd, *args): 
        try:
            connection = self.pool.getconn()
            cursor = connection.cursor()
            cursor.execute(cmd, args)
            return cursor.fetchall()
        except psycopg2.Error as err: 
            logger.error("fail read %s -> %s", cmd, err)
            raise err 
        finally:
            cursor.close()
            self.pool.putconn(connection)

    @contextmanager
    def ctx(self): 
        try:
            connection = self.pool.getconn()
            yield connection
        except psycopg2.OperationalError as err: 
            logger.error("fail read %s", err)
            self.pool.putconn(connection)
            raise err
        finally:
            self.pool.putconn(connection)




            
    #necesito un open y close para manejar mas de una operacion.
    #def __enter__(self):
    #    self.connection = self.pool.getconn()
    #    return self.connection

    #def __exit__(self, exc_type, exc_val, exc_tb):
    #    if exc_type is None:
    #        cursor.close() 
    #        self.pool.putconn(self.ps_connection) 
    #    else:
    #        print('@ListProtect: Error occurred while processing the list. The changes are discarded.')
    #    return False


        
    def closeall(self):
        self.conn.closeall()

    def thread(func):
        def wrapper(*args, **kwargs):
            current_thread = threading.Thread(
                target=func, args=args, kwargs=kwargs, daemon=True)
            current_thread.start()
            #current_thread.join()  sin join para poder ....
        return wrapper


    @thread
    def insert_thread(self, cmd ):
        self.insert(self, cmd )

if __name__ == "__main__":
    db = Postgresql()
    lectura = db.read("SELECT * FROM disp_info;")
    print(lectura)
    for e in lectura:
        print(e)

    db.insert("""INSERT INTO disp_info  
                 (imei, schedule_fota, fota_state, current_code_ver, schedule_time, start_time, end_time, percentage, ota_result) 
                 VALUES 
                 (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                 666, '0', 'sin orden', '0.0.0', None, None, None, 0, '-'
              )







# class Postgresql():
#     def __init__(self):
#         self.conn = psycopg2.connect(
#                     host='18.229.227.108',
#                     user='ubuntu',
#                     password='feelsbadman123',
#                     database="mibanco",
#         )
#         self.cursor = self.conn.cursor()

#     def connect(self):
#         self.conn = psycopg2.connect(
#                     host='18.229.227.108',
#                     user='ubuntu',
#                     password='feelsbadman123',
#                     database="mibanco",
#         )
#         self.cursor = self.conn.cursor()

#     def insert(self, cmd ):
#         try:
#             self.connect();
#         except Exception as err: 
#             print(err)   
#             return 0;

#         try:
#             self.cursor.execute(cmd)
#             self.conn.commit()
#         except Exception as err: 
#             print(err);  
#             return 0;

#         return 1;

#     def read(self, cmd): 
#         try:
#             self.connect();
#         except Exception as err:    
#             return 0;
#         try:
#             self.cursor.execute(cmd)
#             self.conn.commit()
#         except Exception as err:   
#             return 0;

#         return self.cursor.fetchall();
        
#     def close(self):
#         self.conn.close()