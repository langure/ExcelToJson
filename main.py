import os
import pandas as pd
from datetime import datetime
import json
from pymongo import MongoClient
from classes import *

# ENV
EXCEL_FILE = "metadatos_1.xlsx"
JSON_FILE = "./files/1_metadatos.json"
ERRORS_FILE = "./files/1_metadatos_no_validos.json"
METADATOS_FILE = "./files/1_catalogo_metadatos_homologados.json"
SISTEMAS_FILE = "sistemasGestorContenido.txt"
SISTEMAS_CATALOGO_FILE = "./files/1_catalogo_sistemas.txt"
TIMESTAMP = f"{datetime.now().year}-{(datetime.now().month):02d}-{(datetime.now().day):02d}T{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}:{datetime.now().microsecond}Z"

def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')

def doMain(metadatos_source_file):
    clear_screen()

    if not os.path.exists('./files'):
        os.makedirs('./files')
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)
        print(f"The {JSON_FILE} file has been deleted successfully")
    if os.path.exists(ERRORS_FILE):
        os.remove(ERRORS_FILE)
        print(f"The {ERRORS_FILE} file has been deleted successfully")
    if os.path.exists(METADATOS_FILE):
        os.remove(METADATOS_FILE)
        print(f"The {METADATOS_FILE} file has been deleted successfully")    
    if os.path.exists(SISTEMAS_CATALOGO_FILE):
        os.remove(SISTEMAS_CATALOGO_FILE)
        print(f"The {SISTEMAS_CATALOGO_FILE} file has been deleted successfully") 
        
    # Abrir el objeto de excel y cargarlo en memoria
    excel_document = pd.read_excel(metadatos_source_file)
    columns = excel_document.columns
    excel_data = pd.DataFrame(excel_document, columns = columns)

    # Crear un acumulador para los tipos de documentos (eliminar repetidos)
    tipo_document_acumulator = []
    json_acumulator = []
    for index, row in excel_data.iterrows():
        t_tipo_documento = row[TIPO_DOCUMENTO] if not pd.isna(row[TIPO_DOCUMENTO]) else M_SIN_TIPO_DOCUMENTO
        if t_tipo_documento not in tipo_document_acumulator:
            t_tipo_objeto   = row[TIPO_OBJETO] if not pd.isna(row[TIPO_OBJETO]) else M_SIN_TIPO_OBJETO
            t_sistema       = row[SISTEMA] if not pd.isna(row[SISTEMA]) else M_SIN_SISTEMA
            t_multiple      = True if not pd.isna(row[MULTIPLE]) else False
            
            t_d = Documento(t_tipo_documento, t_tipo_objeto, t_sistema, t_multiple)
            tipo_document_acumulator.append(t_tipo_documento)
            json_acumulator.append(t_d)    

    # Contenedor final de los objetos a serializar
    json_data = []
    documentos_validos = []
    documentos_no_validos = []

    sistemas_autorizados = lee_sistemas_autorizados(SISTEMAS_FILE)

    for documento in json_acumulator:
        df = excel_data.query(f"{columns[TIPO_DOCUMENTO]} == '{documento.tipo_documento}'")
        #print(f"Inspecting {documento.tipo_documento}")
        
        metadatos = []        
        for index, row in df.iterrows():
            es_llave = not pd.isna(row[LLAVE])
            metadato = extract_metadato(row, es_llave)
            metadatos.append(metadato)
        
        documento.metadatos = metadatos
        documento.validate(sistemas_autorizados)
        if(documento.valid):
            documentos_validos.append(documento)
        else:
            documentos_no_validos.append(documento)
                
    # Formatear correctamente los documentos validos
    for d in documentos_validos:
        json_obj ={
            "tipo_documento" :  d.tipo_documento,
            "tipo_objeto" :     d.tipo_objeto,
            "metadatos" :       d.metadatos,
            "multiple":         d.multiple,
            "sistemas":[{ "sistema" : d.sistema }],                       
        }
        json_data.append(json_obj)

    total_documentos = len(json_acumulator)
    total_documentos_validos = len(documentos_validos)
    total_documentos_no_validos = len(documentos_no_validos)
    ruta_de_metadatos_json = JSON_FILE
    ruta_de_catalogo_metadatos_homologados = METADATOS_FILE
    print(f"Total de documentos del excel -> {len(json_acumulator)}")
    print(f"Total de documentos válidos -> {len(documentos_validos)}")
    print(f"Total de documentos NO válidos -> {len(documentos_no_validos)}")

    write_output(SISTEMAS_CATALOGO_FILE, METADATOS_FILE, JSON_FILE, ERRORS_FILE, documentos_validos, sistemas_autorizados, json_data, documentos_no_validos)

    # Start mongoDB atlas connection
    upload_to_mongodb(json_data, commit=True)    
    
     
    

if __name__ == "__main__":
    doMain(EXCEL_FILE)
    print("Process finalized")