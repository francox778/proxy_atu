import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)
    

import sqlite3
from contextlib import contextmanager

# Create a connection pool
import colored_logger
import logging
import colorama as cr

logger = colored_logger.Logger("isql", logging.DEBUG, cr.Fore.CYAN)
logger.add_stderr(logging.ERROR)

class ISqlite():
    def __init__(self, bdname):
        self._conn = sqlite3.connect(bdname, check_same_thread=False)


    
    def create_table(self, cmd):
        try:
            cursor = self._conn.cursor()
            cursor.execute(cmd)
        except sqlite3.OperationalError as e:
            logger.info("tabla ya existia")
        finally:
            cursor.close()  

    def insert(self, cmd, *args, cursor=None):
        try:
            cCursor = self._conn.cursor() if not cursor else cursor
            cCursor.execute(cmd, args)
            self._conn.commit()
        except sqlite3.Error as err:
            logger.error("fail insert %s %s-> %s", cmd, args, err)
            raise err
        finally:
            if not cursor:
                cCursor.close()



    def read(self, cmd, *args, cursor=None):
        try:
            cCursor = self._conn.cursor() if not cursor else cursor
            cCursor.execute(cmd, args)
            return cursor.fetchall()
        except sqlite3.Error as err:
            logger.error("fail read %s %s-> %s", cmd, args, err)
            raise err 
        finally:
            if not cursor:
                cCursor.close()

    @contextmanager
    def ctx(self): 
        try:
            cursor = self._conn.cursor()
            yield cursor
        except sqlite3.Error as err:
            logger.error("fail read %s", err)
            cursor.close()
        finally:
            cursor.close()

    def close_connection(self):
        self._conn.close()