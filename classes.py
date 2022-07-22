import uuid

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
SISTEMA = 14

M_SIN_SISTEMA = "Sin sistema"
M_TIPO_DOCUMENTO = "Sin tipo documento"
M_SIN_TIPO_OBJETO = "Sin tipo objeto"
M_SIN_METADATOS = "Sin metadatos"
M_NO_VALIDADO = "No validado"
M_NULL = "null"

class Documento:
    
    def __init__(self, tipo_documento:str, tipo_objeto:str, sistema:str):
        self.tipo_documento = tipo_documento
        self.tipo_objeto = tipo_objeto
        self.metadatos = []
        self.sistema = sistema
        self.valid = False
        self.valid_message = M_NO_VALIDADO
        
    
    def validate(self):
        self.valid = False
        if len(self.tipo_objeto) < 1 or self.tipo_objeto == M_SIN_TIPO_OBJETO:
            self.valid_message = M_SIN_TIPO_OBJETO
            return
        if len(self.tipo_documento) < 1 or self.tipo_documento == M_TIPO_DOCUMENTO:
            self.valid_message = M_TIPO_DOCUMENTO
            return        
        if len(self.metadatos) < 1:
            self.valid_message = M_SIN_METADATOS
            return
        if len(self.sistema) < 1 or self.sistema == M_SIN_SISTEMA:
            self.valid_message = M_SIN_SISTEMA
            return
        
        for metadato in self.metadatos:
            if metadato["metadato"] == M_NULL:
                self.valid_message = "Metadato en null"
                return
            if metadato["metadato_homologado"] == M_NULL:
                self.valid_message = "Metadato homologado en null"
                return
        
        self.valid = True
        self.valid_message = "OK"
        

def genera_catalogo_metadatos(documentos):
    metadatos = []
    acc = []
    for d in documentos:
        if d.valid:
            for m in d.metadatos:
                if m["metadato_homologado"] not in acc:
                    acc.append(m["metadato_homologado"])
                    metadatos.append(
                        {
                            "id_metadato" : str(uuid.uuid4()),
                            "metadato" : m["metadato_homologado"],
                            "fecha_registro" : "%DATE_PH%"
                        }
                    )        
    return metadatos