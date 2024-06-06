# Que es lo que quiero?
#   Quiero un logger que se pueda configurar desde un archivo central? (Eso despues).
#   Quiero crear un handler de un nivel para enviar notificaciones de cosas importantes que tendrian un hisotrial.
#   Quiero poder configurar el color.
#       Para mantener un estado necesito que sea una clase.
#   

import sys

import logging
import colorama as cr
# https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings
# https://stackoverflow.com/questions/8162419/python-logging-specific-level-only    especific log level.
# https://www.codingem.com/log-file-in-python/   Filemode para poner a 0.

# interesanting
# https://stackoverflow.com/questions/59789105/python-logging-using-filename-and-line-number


# Si quiero usar removeHandler()
#   necesitaria que un handler sea parte de una clase o este en un array para identificarlo


# stdout y stderr
# https://stackoverflow.com/questions/56496458/does-python-logging-write-to-stdout-or-stderr-by-default

levelMapping = {
    'DEBUG' : logging.DEBUG,
    'INFO' : logging.INFO,
    'WARNING' : logging.WARNING,
    'ERROR' : logging.ERROR,
    'CRITICAL' : logging.CRITICAL
}



cr.init(autoreset=True)



class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno == self.__level

class FilterExclude(object):
    def __init__(self, level, exclude_level):
        self._level = level
        self._exclude_level = exclude_level

    def filter(self, logRecord):
        include = True
        if self._exclude_level:
            include = False if logRecord.levelno == self._exclude_level else True 
        return logRecord.levelno >= self._level and include # Retorna falso se cancela.


class Logger:
    def __init__(self, name, level, color = cr.Fore.WHITE, exclude_level=None): 
        self._color = color
        self._level = level
        self._exclude_level = exclude_level
        self._logger = logging.getLogger(name)
        self.format = "[%(asctime)s][%(name)-8s][%(levelname)-5s] %(message)s"
        formatter = logging.Formatter(fmt= f"{self._color} {self.format}", datefmt='%d-%m-%y %H:%M:%S') #%b
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(self._level)
        handler.addFilter(FilterExclude(self._level, exclude_level))
        self._logger.setLevel(self._level)
        self._logger.addHandler(handler)
        self._logger.propagate = 0

    def add_stderr(self, level= logging.ERROR):
        handler = logging.StreamHandler(stream=sys.stderr)
        handler.setLevel(level = level)
        formatter = logging.Formatter(fmt = self.format, datefmt='%d-%m-%y %H:%M:%S')
        handler.setFormatter(formatter)
        handler.addFilter(MyFilter(level = level))
        self._logger.addHandler(handler)

    def add_logger_file(self, log_file, level = logging.ERROR, mode = "w" , encoding = "utf-8"):
        file_handler = logging.FileHandler(log_file, encoding = 'utf-8', mode = 'a') #a de append w sobreescribe.
        file_handler.setLevel(level = level)
        formatter = logging.Formatter(fmt = self.format, datefmt='%d-%m-%y %H:%M:%S')
        file_handler.setFormatter(formatter)
        file_handler.addFilter(MyFilter(level= level)) # type: ignore
        self._logger.addHandler(file_handler)

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)





if __name__ == "__main__":
    logger = Logger("test", logging.DEBUG, cr.Fore.RED)
    logger.add_logger_file("xxx.log", logging.ERROR, "w", "utf-8")
    logger.debug("hola %d", 5)
    logger.info("hola %d", 5)
    logger.warning("hola %d", 5)
    logger.error("hola .................%d", 5)
    logger.critical("hola %d", 5)

    logger2 = Logger("test2", logging.DEBUG, cr.Fore.MAGENTA)
    logger2.add_stderr(logging.ERROR)
    logger2.debug("que pasa chavales")
    logger2.debug("que pasa chavales")
    logger2.debug("que pasa chavales")
    logger2.info("que pasa chavales")
    logger2.error("me mandaron al stderr. Buenas aqui es?")

    logger3 = Logger("test3", logging.DEBUG, cr.Fore.YELLOW ,logging.ERROR)
    logger3.add_stderr(logging.ERROR)
    logger3.add_logger_file("xxx.log", logging.ERROR, "w", "utf-8")

    logger3.debug("hola %d", 5)
    logger3.info("hola %d", 5)
    logger3.warning("hola %d", 5)
    logger3.error("hola .................%d", 5)
    logger3.critical("hola %d", 5)