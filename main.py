import os
import pandas as pd
from datetime import datetime
import json
from pymongo import MongoClient
from classes import *

# ENV
EXCEL_FILE = "metadatos_3.xlsx"
JSON_FILE = "metadatos.json"
ERRORS_FILE = "metadatos_no_validos.json"
METADATOS_FILE = "catalogo_metadatos_homologados.json"
TIMESTAMP = f"{datetime.now().year}-{(datetime.now().month):02d}-{(datetime.now().day):02d}T{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}:{datetime.now().microsecond}Z"


def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:    
        _ = os.system('cls')

if __name__ == "__main__":
    clear_screen()
    
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)
        print(f"The {JSON_FILE} file has been deleted successfully")
    if os.path.exists(ERRORS_FILE):
        os.remove(ERRORS_FILE)
        print(f"The {ERRORS_FILE} file has been deleted successfully")
    if os.path.exists(METADATOS_FILE):
        os.remove(METADATOS_FILE)
        print(f"The {METADATOS_FILE} file has been deleted successfully")    
    # Abrir el objeto de excel y cargarlo en memoria
    excel_document = pd.read_excel(EXCEL_FILE)
    columns = excel_document.columns
    excel_data = pd.DataFrame(excel_document, columns = columns)

    # Crear un acumulador para los tipos de documentos (eliminar repetidos)
    tipo_document_acumulator = []
    json_acumulator = []
    for index, row in excel_data.iterrows():
        t_tipo_documento = row[TIPO_DOCUMENTO] if not pd.isna(row[TIPO_DOCUMENTO]) else M_SIN_TIPO_DOCUMENTO
        if t_tipo_documento not in tipo_document_acumulator:
            t_tipo_objeto = row[TIPO_OBJETO] if not pd.isna(row[TIPO_OBJETO]) else M_SIN_TIPO_OBJETO
            t_sistema = row[SISTEMA] if not pd.isna(row[SISTEMA]) else M_SIN_SISTEMA
            tipo_document_acumulator.append(t_tipo_documento)
            t_d = Documento(t_tipo_documento, t_tipo_objeto, t_sistema)
            json_acumulator.append(t_d)    
    
    # Contenedor final de los objetos a serializar
    json_data = []
    documentos_validos = []
    documentos_no_validos = []
    
    for documento in json_acumulator:
        df = excel_data.query(f"{columns[TIPO_DOCUMENTO]} == '{documento.tipo_documento}'")
        #print(f"Inspecting {documento.tipo_documento}")
        
        metadatos = []
        for index, row in df.iterrows():
            if not pd.isna(row[LLAVE]):
                #print(f"Atributo llave encontrado: {row[LLAVE]}")
                t_llave = row[LLAVE]
                t_orden = int(row[ORDEN]) if not pd.isna(row[ORDEN]) else M_NULL
                t_metadato = row[METADATO] if not pd.isna(row[METADATO]) else M_NULL
                t_desc_campo = row[DESCRIPCION_CAMPO] if not pd.isna(row[DESCRIPCION_CAMPO]) else M_NULL
                t_tipo_dato = row[TIPO_DATO] if not pd.isna(row[TIPO_DATO]) else M_NULL
                t_longitud_dato = int(row[LONGITUD_DATO]) if not pd.isna(row[LONGITUD_DATO]) else M_NULL
                t_ayuda_busqueda = row[AYUDA_BUSQUEDA] if not pd.isna(row[AYUDA_BUSQUEDA]) else M_NULL
                t_formato = row[FORMATO] if not pd.isna(row[FORMATO]) else M_NULL
                t_metadato_autorizado = row[METADATO_AUTORIZADO] if not pd.isna(row[METADATO_AUTORIZADO]) else M_NULL
                t_frente = row[FRENTE] if not pd.isna(row[FRENTE]) else M_NULL
                t_desc_homologada = row[DESCRIPCION_HOMOLOGADA] if not pd.isna(row[DESCRIPCION_HOMOLOGADA]) else M_NULL
                t_metadato_homologado = row[METADATO_HOMOLOGADO] if not pd.isna(row[METADATO_HOMOLOGADO]) else M_NULL
                
                metadato = {
                    "llave" : True,
                    "campo" : t_llave,
                    "orden" : t_orden,
                    "metadato" : t_metadato,
                    "descripcion_campo" : t_desc_campo,
                    "tipo_dato" : t_tipo_dato,
                    "longitud_dato": t_longitud_dato,
                    "ayuda_busqueda" : t_ayuda_busqueda,
                    "formato" : t_formato,
                    "metadato_autorizacion" : t_metadato_autorizado,
                    "frente" : t_frente,
                    "descripcion_homologada" : t_desc_homologada,
                    "metadato_homologado" : t_metadato_homologado
                    
                }
                metadatos.append(metadato)
            else:
                #print(f"Atributo NO LLAVE encontrado: {row[LLAVE]}")
                t_metadato = row[METADATO] if not pd.isna(row[METADATO]) else M_NULL
                t_desc_campo = row[DESCRIPCION_CAMPO] if not pd.isna(row[DESCRIPCION_CAMPO]) else M_NULL
                t_tipo_dato = row[TIPO_DATO] if not pd.isna(row[TIPO_DATO]) else M_NULL
                t_longitud_dato = int(row[LONGITUD_DATO]) if not pd.isna(row[LONGITUD_DATO]) else M_NULL
                t_ayuda_busqueda = row[AYUDA_BUSQUEDA] if not pd.isna(row[AYUDA_BUSQUEDA]) else M_NULL
                t_formato = row[FORMATO] if not pd.isna(row[FORMATO]) else M_NULL
                t_metadato_autorizado = row[METADATO_AUTORIZADO] if not pd.isna(row[METADATO_AUTORIZADO]) else M_NULL
                t_frente = row[FRENTE] if not pd.isna(row[FRENTE]) else M_NULL
                t_desc_homologada = row[DESCRIPCION_HOMOLOGADA] if not pd.isna(row[DESCRIPCION_HOMOLOGADA]) else M_NULL
                t_metadato_homologado = row[METADATO_HOMOLOGADO] if not pd.isna(row[METADATO_HOMOLOGADO]) else M_NULL
                
                metadato = {
                    "llave" : False,
                    "campo" : t_metadato,
                    "metadato" : t_metadato,
                    "descripcion_campo" : t_desc_campo,
                    "tipo_dato" : t_tipo_dato,
                    "longitud_dato": t_longitud_dato,
                    "ayuda_busqueda" : t_ayuda_busqueda,
                    "formato" : t_formato,
                    "metadato_autorizacion" : t_metadato_autorizado,
                    "frente" : t_frente,
                    "descripcion_homologada" : t_desc_homologada,
                    "metadato_homologado" : t_metadato_homologado
                    
                }
                metadatos.append(metadato)
        
        documento.metadatos = metadatos
        #documento.sistema = 
        documento.validate()
        if(documento.valid):
            documentos_validos.append(documento)
        else:
            documentos_no_validos.append(documento)
                
    # Formatear correctamente los documentos validos
    for d in documentos_validos:
        json_obj ={
            "tipo_documento" : d.tipo_documento,
            "tipo_objeto" : d.tipo_objeto,
            "metadatos" : d.metadatos,
            "sistemas":[{ "sistema" : d.sistema }]                
        }
        json_data.append(json_obj)
    
    # Crear el catálogo de metadatos de los documentos validos    
    catalogo_metadatos = genera_catalogo_metadatos(documentos_validos)
    catalogo_metadatos_file = open(METADATOS_FILE, "w")
    catalogo_metadatos_file.writelines(json.dumps(catalogo_metadatos, ensure_ascii=False, indent = 4).replace('"%DATE_PH%"', f'ISODate("{TIMESTAMP}")'))
    catalogo_metadatos_file.close()
    
    # Write the json object into the json file
    json_file = open(JSON_FILE, "w")
    json_file.writelines(json.dumps(json_data, ensure_ascii=False, indent = 4).replace('"null"','null'))
    json_file.close()           
        
    # Escribir los documentos que no fueron válidos
    
    errors_file = open(ERRORS_FILE, "w")
    errors_file.writelines(json.dumps(documentos_no_validos, ensure_ascii=False, indent=4, default=vars))
    errors_file.close()
    
    # Start mongoDB atlas connection

    CONNECTION_STRING = "INSERT_YOUR_CREDENTIALS_HERE"
    

    client = MongoClient(CONNECTION_STRING)
    driver = client["Metadatos"]
    collection = driver["metadatos"]
    
    # Delete the collection in the mongodb server
    collection.drop()

    # Write the new data
    collection.insert_many(json_data)

    print(f"Total de documentos del excel -> {len(json_acumulator)}")
    print(f"Total de documentos válidos -> {len(documentos_validos)}")
    print(f"Total de documentos NO válidos -> {len(documentos_no_validos)}")
    print("Process finalized")