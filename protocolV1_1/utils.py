import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)

import colored_logger
import logging
import colorama as cr

logger = colored_logger.Logger("utils", logging.DEBUG, cr.Fore.CYAN)
logger.add_stderr(logging.ERROR)

def trunc_byte(a: int, nbytes: int):
    i = 1 << 8*nbytes
    if a > i - 1:
        a = a%i
        logger.error("number longer than expected %d, %d", a ,nbytes)
        return a.to_bytes(nbytes, byteorder='little')
    else:
        return a.to_bytes(nbytes, byteorder='little')    


def trunc_number(a: int, nbytes: int):
    i = 1 << 8*nbytes
    if a > i - 1:
        a = a%i
        logger.error("number longer than expected %d, %d", a ,nbytes)
        return a
    else:
        return a       

if "__main__" == __name__:
    i = 258
    print(trunc_byte(i, 1))
    i = 18446744073709552000
    print(trunc_byte(i, 8)) 
    i = 254
    print(trunc_byte(i, 8)) 