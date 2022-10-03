import logging

logging.basicConfig(filename='/var/log/automation/automation.log', format='[%(levelname)s][%(threadName)s]:%(message)s', level=logging.INFO)
log = logging.getLogger("AUTOMATION")

def debug(message):
    log.debug(message)

def info(message):
    log.info(message)
    
def warning(message):
    log.warning(message)

def error(message):
    log.error(message)
