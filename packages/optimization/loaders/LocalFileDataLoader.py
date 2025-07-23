from loaders.DataLoader import DataLoader

class LocalFileDataLoader(DataLoader):
    
    def __init__(self, file_path):
        self.file_path = file_path

    def load_json_string(self) -> str:
        with open(self.file_path, 'r') as f:
            return f.read()