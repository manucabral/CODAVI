from urllib.request import urlopen
from datetime import datetime
import pandas as pd
import mysql.connector
import zipfile
import shutil
import os

FECHA_ACTUAL = datetime.now().date().isoformat()
URL_DATASET = 'https://sisa.msal.gov.ar/datos/descargas/covid-19/files/'
VACUNACION_ARCHIVO = 'datos_nomivac_covid19'
CASOS_ARCHIVO = 'Covid19Casos'

def existeArchivo(nombreArchivo):
    return os.path.isfile('./' + nombreArchivo + '.csv')

def descargarArchivo(nombreArchivo):

    comprimido = nombreArchivo + '.zip'
    csv = nombreArchivo + '.csv'

    print('Iniciando descarga del archivo', comprimido)
    with urlopen(URL_DATASET + comprimido) as respuesta, open(comprimido, 'wb') as salida:

        print('Copiando', comprimido, 'en el directorio..')
        shutil.copyfileobj(respuesta, salida)

        print('Extrayendo', csv, 'del archivo comprimido..')
        with zipfile.ZipFile(comprimido) as archivoComprimido:
            archivoComprimido.extract(csv)

    print('Eliminado', comprimido, 'del directorio..')
    os.remove(comprimido)

    return print('Archivo', csv, 'descargado correctamente en el directorio.')

def actualizarDatosGenero():
    masculinos = [0, 0]
    femeninos = [0, 0]

    try:
        data = pd.read_csv('datos_nomivac_covid19.csv', usecols=[
                           'orden_dosis', 'sexo'], skipinitialspace=True)
    except Exception as Error:
        return Error

    for i in range(2):
        femeninos[i] = data.query(
            f'orden_dosis == {i+1} and sexo == "F"').sexo.count()
        masculinos[i] = data.query(
            f'orden_dosis == {i+1} and sexo == "M"').sexo.count()

    cnx = mysql.connector.connect(
        host="unknown",
        port=3306,
        user="unknown",
        password="unknown",
        db="unknown"
    )
    cursor = cnx.cursor()

    for i in range(2):
        query = (
            f"INSERT INTO `unknown`.`generos` (`masculino`, `femenino`, `dosis`, `fecha`) VALUES ({masculinos[i]}, '{femeninos[i]}', '{i+1}', '{FECHA_ACTUAL}');")
        cursor.execute(query)
    
    cursor.close()
    cnx.commit()
    cnx.close()
    return "Datos de generos actualizados correctamente"

if __name__ == "__main__":

    try:
        if not existeArchivo(VACUNACION_ARCHIVO):
            descargarArchivo(VACUNACION_ARCHIVO)
        else:
            print('Archivo encontrado:', VACUNACION_ARCHIVO)

        if not existeArchivo(CASOS_ARCHIVO):
            descargarArchivo(CASOS_ARCHIVO)
        else:
            print('Archivo encontrado:', CASOS_ARCHIVO)

    except ValueError:
        print('Ocurrio un error al descargar los archivos: ', ValueError)

    actualizarDatosGenero()