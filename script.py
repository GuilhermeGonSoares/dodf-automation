import json
import pyodbc
from datetime import datetime

db_params_sqlserver = {
    "Driver": "{SQL Server}",
    "Server": "localhost",
    "Database": "dodf",
    "UID": "sa",
    "PWD": "#aa102020"
}

with open('./dodf.json', 'r', encoding='utf-8') as arquivo:
    dados_json = json.load(arquivo)['json']['INFO']


try:
    connection_sqlserver = pyodbc.connect(**db_params_sqlserver)
    cursor = connection_sqlserver.cursor()
    connection_sqlserver.autocommit = False

    for secao in dados_json.keys():
        numero_secao = secao.split(' ')[1]
        for departamento in dados_json[secao].keys():
            for coMateria in dados_json[secao][departamento]['documentos'].keys():
                materia = dados_json[secao][departamento]['documentos'][coMateria]
                query = """
                INSERT INTO dodfPublicacao (coMateria, coDemandante, secao, titulo, preambulo, tipo, situacao, regraSituacao, layout, nuOrdem, texto, carga)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = (materia['coMateria'], materia['coDemandante'], numero_secao, materia['titulo'], materia['preambulo'], materia['tipo'], materia['situacao'], materia['regraSituacao'], materia['layout'], materia['nuOrdem'], materia['texto'], '2023-08-17 08:00')
                cursor.execute(query, values)
    cursor.commit()
except pyodbc.Error as e:
    print("Erro ao conectar ao SQL Server:", e)
