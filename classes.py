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
M_SIN_TIPO_DOCUMENTO = "Sin tipo documento"
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
        if len(self.tipo_documento) < 1 or self.tipo_documento == M_SIN_TIPO_DOCUMENTO:
            self.valid_message = M_SIN_TIPO_DOCUMENTO
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
        self.verifica_campos_llave()
        self.verifica_campos_duplicados()
        
    def verifica_campos_duplicados(self):
        acc_campos = []
        for m in self.metadatos:
            if not m["campo"] in acc_campos:
                acc_campos.append(m["campo"])
            else:
                self.valid = False
                self.valid_message = f"Campos duplicados: {m['campo']}"
            
    def verifica_campos_llave(self):
        acc_llave = []
        for m in self.metadatos:
            if "llave" in m and m["llave"]:                
                if not "orden" in m:
                    self.valid = False
                    self.valid_message = f"Marcado como llave pero sin orden -> {m['campo']}"
                    return
                if m["orden"] not in acc_llave:
                    acc_llave.append(m["orden"])
                else:
                    self.valid = False
                    self.valid_message = f"Error en llaves duplicadas"
                    return
        if len(acc_llave) < 1:
            self.valid = False
            self.valid_message = f"No tiene ninguna llave"
        
        



def genera_catalogo_metadatos(documentos):
    metadatos = []
    acc = []
    for d in documentos:
        if d.valid:
            for m in d.metadatos:
                if m["metadato"] == "Archivo":
                    print("Archivo")
                if m["metadato"] not in acc:
                    acc.append(m["metadato"])
                    metadatos.append(
                        {
                            "id_metadato" : str(uuid.uuid4()),
                            "metadato" : m["metadato"],
                            "fecha_registro" : "%DATE_PH%"
                        }
                    )        
    return metadatos