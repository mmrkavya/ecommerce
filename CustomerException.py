class CustomException(Exception):
    message=None
    statusCode=None
    def __init__(self,message,statusCode):
        super()
        self.message=message
        self.statusCode=statusCode

    def getStatusCode(self):
        return self.statusCode

    def getMessage(self):
        return self.message


