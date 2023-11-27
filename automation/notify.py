from automation import logger as logger
import requests
from raspberry.settings import AUTOMATION

baseURL = "https://api.plivo.com/v1"

class Client:
    def __init__(self, authId, authToken):
        self.authId = authId
        self.authToken = authToken

    def __smsURL(self):
        return "{}/Account/{}/Message/".format(baseURL, self.authId)

    def __successfulResponse(self, status):
        return [200, 201, 202, 204].count(status) > 0
   
    def sendSMS(self, destiny, text, source="59899223344"):
        if type(destiny) is list:
            destiny = ",".join(destiny)
        payload = {'src': source,
                   'dst': destiny,
                   'text': text}
        logger.debug("payload: {}".format(payload))
        resp = requests.post(self.__smsURL(), auth=(self.authId, self.authToken), json=payload)
        if not self.__successfulResponse(resp.status_code):
            logger.error("Status:{}. Reason:{}".format(resp.status_code, resp.reason))
        else:
            logger.info("SMS sent to {}".format(destiny))

def defaultClient():
    return Client("XXX", "YYY")

def test():
    c = defaultClient()
    c.sendSMS(AUTOMATION["notifyPhone"], "Plivo SMS test")