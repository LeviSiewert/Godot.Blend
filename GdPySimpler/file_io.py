from .core.structure import _FileTypeIoHandler, _Resource 
# from .transformers.tscn import GdToPyTransformer, PyToGdTranformer

class FileIoTxt[D:str, T:str](_FileTypeIoHandler):
    extensions = ("uid","txt")

    def convert_from(self, data:D)->T:
        return data
    
    def convert_to(self, data:T)->D:
        return data