from CONFIG import App


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

    try:
        acceptor = acceptor_thread.AcceptorThread(ACCEPTOR_IP, ACCEPTOR_PORT)
        acceptor.start()
        acceptor.join()
    except KeyboardInterrupt:
        logger.debug("CTRL+C close")
        exit(1)
        