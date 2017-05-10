import requests
import base64

class Connection:
    """
    Main class for the CloudRun-Connection
    """
    
    verifySSL = True    # Verify SSL-Cert?
    timeout = 60        # Timeout in seconds
    auth = None         # HTTP-auth if necessary
    proxies = None      # Proxies if necessary
    
    
    def __init__(self, url, port, token=""):
        """
        Construct a new 'Connection' object with an authentication token
        
        :param url: URL of the server, WITH "http://" or "https://"!
        :param port: Port of the server
        :param token: Your authentication token. If not set it defaults to ""
        :return: Returns nothing
        """
        
        self.url = url
        self.port = port
        self.token = token
    
    
    def __request(self, handler, payload):
        """
        Private method for a request
        
        :param handler: The handler that shall be used
        :param payload: What you want to send to the server
        :return: Returns the response from the request
        """
        
        req = requests.post(str(self.url) + ":" + str(self.port) + "/" + str(handler) + "/", 
                            json=payload, 
                            verify=self.verifySSL, 
                            timeout=self.timeout,
                            auth=self.auth,
                            proxies=self.proxies)
        
        req.raise_for_status() # Exception auslösen wenn Statuscode Fehler anzeigt
        answer = req.json(); # Antwort des Servers in Dictionary umwandeln
        
        if 'error' in answer:   # If CloudRun answered with an error
            raise CloudRunError("Error " + str(answer['error']['code']) + ": " + str(answer['error']['message']))
            return None
        else:
            return req
        
    
    def sendRequest(self, module, data):
        """
        Send a request (to /request/ handler)
        
        :param module: The module you want to use
        :param data: The data you want to send to the module
        :return: 'Response' object containing the response of the request
        """
        
        payload = {'token': self.token, 'module': module, 'data': data}
        req = self.__request("request", payload)
        
        return Response(req)
    
    
    def sendPreparedRequest(self, request):
        """
        Send a prepared request (to /request/ handler)
        
        :param request: 'Request' object contaning the request information
        :return: 'Response' object containing the response of the request
        """
        
        if type(request) is Request:
            return self.sendRequest(request.module, request.data)
        else:
            raise ValueError('request has to be a Request object')
    
    
    def sendCustomRequest(self, handler, data={ }):
        """
        Send a custom request to a handler of your choice
        
        :param handler: The handler you want to use
        :param data: The data you want to send to the handler
        :return: 'Response' object containing the response of the request
        """
        
        payload = {'token': self.token, 'data': data}
        req = self.__request(handler, payload)
        return Response(req)



class Request:
    """
    Request class used for prepared requests
    """
    
    data = {}       # Empty data
    
    
    def __init__(self, module):
        """
        Construct a new 'Request' object
        
        :param module: The module you want to use
        :return: Returns nothing
        """
        
        self.module = module
     
        
    def setData(self, name, value):
        """
        Sets a data field to the specified value
        
        :param name: Name of the data field
        :param value: Value of the data field
        :return: Returns nothing
        """
        
        self.data[name] = value
    
    
    def setDataFromFile(self, name, file):
        """
        Sets a data field with the contents of a file (base64 encoded)
        
        :param name: Name of the data field
        :param file: the file you want to use
        :type file: 'file' object (returned by open())
        :return: Returns nothing
        .. note:: Always open the file in binary mode! 
        """
        
        self.data[name] = base64.standard_b64encode(
            file.read()).decode('ascii')
        file.close()
        
        
    def removeData(self, name):
        """
        Removes a data field
        
        :param name: Name of the data field
        :return: Returns nothing
        """
        
        del self.data[name]
    
    
    def clearData(self):
        """
        Clears the data field
        
        :return: Returns nothing
        """    
        
        self.data.clear()
        
        
        
class Response:
    """
    Response class, contains the response
    """
    
    raw = None          # Raw response if needed
    response = None     # Dictionary of the response
    status_code = None  # Status code
    headers = None      # Response headers (dictionary)
    
    
    def __init__(self, response):
        """
        Construct a new 'Response' object
        
        :param response: The response of the request
        :return: Returns nothing
        """
        
        self.raw = response
        self.response = response.json()
        self.status_code = response.status_code
        self.headers = response.headers
        

class CloudRunError(Exception):
    """
    CloudRunError Exception, will be raised when CloudRun submits an error
    """
    
    pass