import logging

logging.basicConfig(format='%(asctime)s[%(levelname)s][%(threadName)s]:%(message)s', level=logging.DEBUG)
log = logging.getLogger("AUTOMATION")

def debug(message):
    log.debug(message)

def warning(message):
    log.warning(message)

def error(message):
    log.error(message)
