from DataAccessor import DataAccessor

class LocalDataAccessor(DataAccessor):
    def __init__(self, root_path: str = "."):
        self.root_path = root_path

    def load_string(self, storage_path: str) -> str:
        with open(self.__build_full_path(storage_path), 'r') as f:
            return f.read()
        
    def write_string_to_path(self, content: str, storage_path: str):
        with open(self.__build_full_path(storage_path), 'w') as f:
            f.write(content)

    def __build_full_path(self, storage_path: str) -> str:
        return f"{self.root_path}/{storage_path}"
