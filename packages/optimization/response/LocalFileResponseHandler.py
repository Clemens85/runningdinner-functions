
from response.ResponseHandler import ResponseHandler

class LocalFileResponseHandler(ResponseHandler):
    
    def __init__(self, file_path):
        self.file_path = file_path

    def send(self, json_string: str):
        with open(self.file_path, 'w') as f:
            f.write(json_string)
            f.flush()
            f.close()