
# Constants

TIPO_DOCUMENTO = 0
TIPO_OBJETO = 1
LLAVE = 2
ORDEN = 3
METADATO = 4
DESCRIPCION_CAMPO = 5
TIPO_DATO = 6
LONGITUD_DATO = 7
AYUDA_BUSQUEDA = 8
FORMATO = 9
METADATO_AUTORIZADO = 10
FRENTE = 11
DESCRIPCION_HOMOLOGADA = 12
METADATO_HOMOLOGADO = 13


class Documento:
    
    def __init__(self, tipo_documento:str, tipo_objeto:str):
        self.tipo_documento = tipo_documento
        self.tipo_objeto = tipo_objeto
        self.metadatos = []
        self.sistemas = {
            "sistema" : "SAP"
        }