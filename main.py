import os
import pandas as pd
import json
from pymongo import MongoClient
from classes import *

# ENV
EXCEL_FILE = "metadatos.xlsx"
JSON_FILE = "metadatos.json"



def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:    
        _ = os.system('cls')

if __name__ == "__main__":
    clear_screen()
    
    # Abrir el objeto de excel y cargarlo en memoria
    excel_document = pd.read_excel(EXCEL_FILE)
    columns = excel_document.columns
    excel_data = pd.DataFrame(excel_document, columns = columns)

    # Crear un acumulador para los tipos de documentos (eliminar repetidos)
    tipo_document_acumulator = []
    json_acumulator = []
    for index, row in excel_data.iterrows():
        t_tipo_documento = row[TIPO_DOCUMENTO]
        if t_tipo_documento not in tipo_document_acumulator:
            tipo_document_acumulator.append(t_tipo_documento)
            t_d = Documento(t_tipo_documento, row[TIPO_OBJETO])
            json_acumulator.append(t_d)
            
    # Contenedor final de los objetos a serializar
    json_data = []
    for documento in json_acumulator:
        df = excel_data.query(f"{columns[TIPO_DOCUMENTO]} == '{documento.tipo_documento}'")
        print(f"Inspecting {documento.tipo_documento}")
        
        metadatos = []
        for index, row in df.iterrows():
            if not pd.isna(row[LLAVE]):
                #print(f"Atributo llave encontrado: {row[LLAVE]}")
                t_llave = row[LLAVE]
                t_orden = row[ORDEN] if not pd.isna(row[ORDEN]) else -1
                t_metadato = row[METADATO] if not pd.isna(row[METADATO]) else ""
                t_desc_campo = row[DESCRIPCION_CAMPO] if not pd.isna(row[DESCRIPCION_CAMPO]) else ""
                t_tipo_dato = row[TIPO_DATO] if not pd.isna(row[TIPO_DATO]) else ""
                t_longitud_dato = row[LONGITUD_DATO] if not pd.isna(row[LONGITUD_DATO]) else ""
                t_ayuda_busqueda = row[AYUDA_BUSQUEDA] if not pd.isna(row[AYUDA_BUSQUEDA]) else ""
                t_formato = row[FORMATO] if not pd.isna(row[FORMATO]) else ""
                t_metadato_autorizado = row[METADATO_AUTORIZADO] if not pd.isna(row[METADATO_AUTORIZADO]) else ""
                t_frente = row[FRENTE] if not pd.isna(row[FRENTE]) else ""
                t_desc_homologada = row[DESCRIPCION_HOMOLOGADA] if not pd.isna(row[DESCRIPCION_HOMOLOGADA]) else ""
                t_metadato_homologado = row[METADATO_HOMOLOGADO] if not pd.isna(row[METADATO_HOMOLOGADO]) else ""
                
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
                    "metadato_autorizado" : t_metadato_autorizado,
                    "frente" : t_frente,
                    "descripcion_homologada" : t_desc_homologada,
                    "metadato_homologado" : t_metadato_homologado
                    
                }
                metadatos.append(metadato)
            else:
                #print(f"Atributo NO LLAVE encontrado: {row[LLAVE]}")
                t_metadato = row[METADATO] if not pd.isna(row[METADATO]) else ""
                t_desc_campo = row[DESCRIPCION_CAMPO] if not pd.isna(row[DESCRIPCION_CAMPO]) else ""
                t_tipo_dato = row[TIPO_DATO] if not pd.isna(row[TIPO_DATO]) else ""
                t_longitud_dato = row[LONGITUD_DATO] if not pd.isna(row[LONGITUD_DATO]) else ""
                t_ayuda_busqueda = row[AYUDA_BUSQUEDA] if not pd.isna(row[AYUDA_BUSQUEDA]) else ""
                t_formato = row[FORMATO] if not pd.isna(row[FORMATO]) else ""
                t_metadato_autorizado = row[METADATO_AUTORIZADO] if not pd.isna(row[METADATO_AUTORIZADO]) else ""
                t_frente = row[FRENTE] if not pd.isna(row[FRENTE]) else ""
                t_desc_homologada = row[DESCRIPCION_HOMOLOGADA] if not pd.isna(row[DESCRIPCION_HOMOLOGADA]) else ""
                t_metadato_homologado = row[METADATO_HOMOLOGADO] if not pd.isna(row[METADATO_HOMOLOGADO]) else ""
                
                metadato = {
                    "llave" : False,
                    "campo" : t_metadato,
                    "metadato" : t_metadato,
                    "descripcion_campo" : t_desc_campo,
                    "tipo_dato" : t_tipo_dato,
                    "longitud_dato": t_longitud_dato,
                    "ayuda_busqueda" : t_ayuda_busqueda,
                    "formato" : t_formato,
                    "metadato_autorizado" : t_metadato_autorizado,
                    "frente" : t_frente,
                    "descripcion_homologada" : t_desc_homologada,
                    "metadato_homologado" : t_metadato_homologado
                    
                }
                metadatos.append(metadato)
                
        top_json = {
            "tipo_documento" : documento.tipo_documento,
            "tipo_objeto" : documento.tipo_objeto,
            "metadatos" : metadatos,
            "sistemas":[{ "sistema" : "SAP" }]
        }
        json_data.append(top_json)
    
    # Write the json object into the json file
    json_file = open(JSON_FILE, "w")
    json_file.writelines(json.dumps(json_data, ensure_ascii=False, indent = 4))
    json_file.close()           
        
    # Start mongoDB atlas connection

    CONNECTION_STRING = "INSERT_YOUR_CREDENTIALS_HERE"

    client = MongoClient(CONNECTION_STRING)
    driver = client["Metadatos"]
    collection = driver["metadatos"]
    
    # Delete the collection in the mongodb server
    collection.drop()

    # Write the new data
    collection.insert_many(json_data)

    print("Process finalized")