import uuid
from pymongo import MongoClient
import json
from datetime import datetime
import pandas as pd
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants

TIPO_DOCUMENTO = 0
TIPO_OBJETO = 1
LLAVE = 2
ORDEN = 3
CAMPO = 4
DESCRIPCION_CAMPO = 5
TIPO_DATO = 6
LONGITUD_DATO = 7
AYUDA_BUSQUEDA = 8
FORMATO = 9
METADATO_AUTORIZACION = 10
FRENTE = 11
DESCRIPCION_HOMOLOGADA = 12
METADATO = 13
SISTEMA = 14
TIPO_OBJETO_AUTORIZACION = 15
AMBITO_OBJETO_AUTORIZACION = 16
MULTIPLE = 17

M_SIN_SISTEMA = "Sin sistema"
M_SISTEMA_NO_EN_CATALOGO = "Este sistema no está en el catálogo de sistemas"
M_SIN_TIPO_DOCUMENTO = "Sin tipo documento"
M_SIN_TIPO_OBJETO = "Sin tipo objeto"
M_SIN_METADATOS = "Sin metadatos"
M_NO_VALIDADO = "No validado"
M_NULL = "null"

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SAMPLE_SPREADSHEET_ID = '1PZQnb9OIBUmXwvl2kHsK5bS0pMc5ILuJs5ApOczNBL0'
SAMPLE_RANGE_NAME = 'MongoDB!A:R'

TIMESTAMP = f"{datetime.now().year}-{(datetime.now().month):02d}-{(datetime.now().day):02d}T{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}:{datetime.now().microsecond}Z"

class Documento:
    
    def __init__(self, tipo_documento:str, tipo_objeto:str, sistema:str, es_multiple:bool):
        self.tipo_documento = tipo_documento
        self.tipo_objeto = tipo_objeto
        self.metadatos = []
        self.sistema = sistema
        self.valid = False
        self.multiple = es_multiple
        self.valid_message = M_NO_VALIDADO
        
    
    def validate(self, sistemas_autorizados):
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
        if self.sistema not in sistemas_autorizados:
            self.valid_message = M_SISTEMA_NO_EN_CATALOGO
            return
        
        for metadato in self.metadatos:
            if metadato["metadato"] == M_NULL:
                self.valid_message = "Metadato en null"
                return
            if 'orden' in metadato and metadato["orden"] == -1:
                self.valid_message = f"Llave sin orden {metadato['campo']}"
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
        
        
def lee_sistemas_autorizados(sistemas_file):
    sistemas_autorizados = []
    
    with open(sistemas_file, 'r') as f:
        for line in f:
            sistemas_autorizados.append(line.replace("\n", ""))
    return sistemas_autorizados

def genera_catalogo_sistemas_autorizados(sistemas_autorizados):
    s = []
    for sistema in sistemas_autorizados:
        s.append({
            "id_sistema" : str(uuid.uuid4()),
            "sistema" : sistema,
            "descripcion" : sistema,
            "fecha_registro" : "%DATE_PH%"             
        })
    return s

def genera_catalogo_metadatos(documentos):
    metadatos = []
    acc = []
    for d in documentos:
        if d.valid:
            for m in d.metadatos:
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

def upload_to_mongodb(json_data, commit = True):
    if not commit:
        return
    #CONNECTION_STRING = "INSERT_YOUR_CREDENTIALS_HERE"
    CONNECTION_STRING = "mongodb+srv://mongodb_admin:YQJrrYHKRsW7eEAt@cluster0.ciy9iep.mongodb.net"

    client = MongoClient(CONNECTION_STRING)
    driver = client["Metadatos"]
    collection = driver["metadatos"]
    
    # Delete the collection in the mongodb server
    collection.drop()

    # Write the new data
    collection.insert_many(json_data)       

def transform_json_to_pure_string(json_content):
    st_json = json.dumps(json_content, ensure_ascii=False, indent = 4)
    formatted_json=json.loads(st_json, parse_int=str)
    return json.dumps(formatted_json, ensure_ascii=False, indent = 4).replace('false','"false"').replace('true','"true"')


def write_output(sistemas_catalogo_filename, metadatos_filename, json_filename, errors_filename, documentos_validos, 
                 sistemas_autorizados, json_data, documentos_no_validos):
    # Crear el catálogo de sistemas:    
    sistemas_autorizados_file = open(sistemas_catalogo_filename, "w")
    sistemas_autorizados_file.writelines(json.dumps(genera_catalogo_sistemas_autorizados(sistemas_autorizados), ensure_ascii=False, indent = 4).replace('"%DATE_PH%"', f'ISODate("{TIMESTAMP}")'))
    sistemas_autorizados_file.close()
    
    # Crear el catálogo de metadatos de los documentos validos    
    catalogo_metadatos = genera_catalogo_metadatos(documentos_validos)
    catalogo_metadatos_file = open(metadatos_filename, "w")
    catalogo_metadatos_file.writelines(json.dumps(catalogo_metadatos, ensure_ascii=False, indent = 4).replace('"%DATE_PH%"', f'ISODate("{TIMESTAMP}")'))
    catalogo_metadatos_file.close()
    
    # Write the json object into the json file
    json_file = open(json_filename, "w")
    #json_file.writelines(transform_json_to_pure_string(json_data))
    #json_file.writelines(json.dumps(json_data, ensure_ascii=False, indent = 4))
    json_file.writelines(json.dumps(json_data, ensure_ascii=False, indent = 4).replace('"null"','null'))
    json_file.close()           
        
    # Escribir los documentos que no fueron válidos
    
    errors_file = open(errors_filename, "w")
    errors_file.writelines(json.dumps(documentos_no_validos, ensure_ascii=False, indent=4, default=vars))
    errors_file.close()
    
def extract_metadato_google(row, es_llave):

    t_campo = row[CAMPO] if not pd.isna(row[CAMPO]) else M_NULL
    t_desc_campo = row[DESCRIPCION_CAMPO] if not pd.isna(row[DESCRIPCION_CAMPO]) else M_NULL
    t_tipo_dato = row[TIPO_DATO] if not pd.isna(row[TIPO_DATO]) else M_NULL
    #t_longitud_dato = int(row[LONGITUD_DATO]) if not pd.isna(row[LONGITUD_DATO]) else M_NULL
    t_longitud_dato = int(row[LONGITUD_DATO]) if len(row[LONGITUD_DATO]) > 0 else M_NULL
    t_ayuda_busqueda = row[AYUDA_BUSQUEDA] if not pd.isna(row[AYUDA_BUSQUEDA]) else M_NULL
    t_formato = row[FORMATO] if not pd.isna(row[FORMATO]) else M_NULL
    
    t_metadato_autorizacion =  True if row[METADATO_AUTORIZACION] else False
    t_obligatorio = es_llave or t_metadato_autorizacion
    
    t_frente = row[FRENTE] if not pd.isna(row[FRENTE]) else M_NULL
    t_desc_homologada = row[DESCRIPCION_HOMOLOGADA] if not pd.isna(row[DESCRIPCION_HOMOLOGADA]) else M_NULL
    t_tipo_objeto_autorizacion = row[TIPO_OBJETO_AUTORIZACION] if not pd.isna(row[TIPO_OBJETO_AUTORIZACION]) else M_NULL
    t_metadato = row[METADATO] if not pd.isna(row[METADATO]) else M_NULL
    t_ambito_objeto_autorizacion = row[AMBITO_OBJETO_AUTORIZACION] if not pd.isna(row[AMBITO_OBJETO_AUTORIZACION]) else M_NULL
    
    metadato = {
        "llave" : False,
        "campo" : t_campo,
        "metadato" : t_metadato,
        "descripcion_campo" : t_desc_campo,
        "tipo_dato" : t_tipo_dato,
        "longitud_dato": t_longitud_dato,
        "ayuda_busqueda" : t_ayuda_busqueda,
        "formato" : t_formato,
        "metadato_autorizacion" : t_metadato_autorizacion,
        "frente" : t_frente,
        "descripcion_homologada" : t_desc_homologada, 
        "tipo_objeto_autorizacion" : t_tipo_objeto_autorizacion.strip(),
        "ambito_objeto_autorizacion" : t_ambito_objeto_autorizacion,
        "obligatorio" : t_obligatorio               
    }
    
    if es_llave:
        try:        
            t_orden = int(row[ORDEN]) if not pd.isna(row[ORDEN]) else M_NULL
            metadato["llave"] = True
            metadato["orden"] = t_orden
        except ValueError:
            metadato["llave"] = True
            metadato["orden"] = -1
    
    return metadato

def extract_metadato_excel(row, es_llave):

    t_campo = row[CAMPO] if not pd.isna(row[CAMPO]) else M_NULL
    t_desc_campo = row[DESCRIPCION_CAMPO] if not pd.isna(row[DESCRIPCION_CAMPO]) else M_NULL
    t_tipo_dato = row[TIPO_DATO] if not pd.isna(row[TIPO_DATO]) else M_NULL
    t_longitud_dato = int(row[LONGITUD_DATO]) if not pd.isna(row[LONGITUD_DATO]) else M_NULL
    t_ayuda_busqueda = row[AYUDA_BUSQUEDA] if not pd.isna(row[AYUDA_BUSQUEDA]) else M_NULL
    t_formato = row[FORMATO] if not pd.isna(row[FORMATO]) else M_NULL
    t_metadato_autorizado =  True if not pd.isna(row[MULTIPLE]) else False
    t_frente = row[FRENTE] if not pd.isna(row[FRENTE]) else M_NULL
    t_desc_homologada = row[DESCRIPCION_HOMOLOGADA] if not pd.isna(row[DESCRIPCION_HOMOLOGADA]) else M_NULL
    t_tipo_objeto_autorizacion = row[TIPO_OBJETO_AUTORIZACION] if not pd.isna(row[TIPO_OBJETO_AUTORIZACION]) else M_NULL
    t_metadato = row[METADATO] if not pd.isna(row[METADATO]) else M_NULL
    
    metadato = {
        "llave" : False,
        "campo" : t_campo,
        "metadato" : t_metadato,
        "descripcion_campo" : t_desc_campo,
        "tipo_dato" : t_tipo_dato,
        "longitud_dato": t_longitud_dato,
        "ayuda_busqueda" : t_ayuda_busqueda,
        "formato" : t_formato,
        "metadato_autorizacion" : t_metadato_autorizado,
        "frente" : t_frente,
        "descripcion_homologada" : t_desc_homologada, 
        "tipo_objeto_autorizacion" : t_tipo_objeto_autorizacion                  
    }
    
    if es_llave:        
        t_orden = int(row[ORDEN]) if not pd.isna(row[ORDEN]) else M_NULL
        metadato["llave"] = True
        metadato["orden"] = t_orden
    
    return metadato
        
def read_from_google():
    creds = None
    panda = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print("No data found")
            return panda

        #for row in values:
        #     print('%s, %s' % (row[0], row[4]))
        print(len(values[1][:18]))
        panda = pd.DataFrame(values[1:], columns=values[0])
        
    except HttpError as err:
        print(err.error_details)
        print(err.reason)
        return panda
    return panda