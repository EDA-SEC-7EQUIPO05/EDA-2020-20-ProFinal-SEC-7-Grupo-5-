"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """

import config as cf
from App import model
import datetime
import csv

"""
El controlador se encarga de mediar entre la vista y el modelo.
Existen algunas operaciones en las que se necesita invocar
el modelo varias veces o integrar varias de las respuestas
del modelo en una sola respuesta.  Esta responsabilidad
recae sobre el controlador.
"""

# ___________________________________________________
#  Inicializacion del catalogo
# ___________________________________________________

def init():
    """
    Llama la funcion de inicializacion del modelo.
    """
    analyzer = model.newAnalyzer()
    return analyzer

# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________

def loadData(analyzer, taxifile):
    """
    Carga los datos de los archivos CSV en el modelo
    """
    taxifile = cf.data_dir + taxifile
    input_file = csv.DictReader(open(taxifile, encoding="utf-8"), delimiter=",")
    for service in input_file:
        model.addService(analyzer, service)
    return analyzer

# ___________________________________________________
#  Funciones para consultas
# ___________________________________________________

def companiesByTaxis(analyzer, num):
    return model.companiesByTaxis(analyzer, num)

def totalTaxis(analyzer):
    return model.totalTaxis(analyzer)

def totalCompanies (analyzer):
    return model.totalCompanies(analyzer)

def parteB(analyzer, num, cond, fecha=None, mindate=None, maxdate=None):
    if fecha is not None:
        fecha = datetime.datetime.strptime(fecha, '%Y-%m-%d')
        formatdate = fecha.date()
    else:
        formatdate = None
    if mindate is not None:
        mindate = datetime.datetime.strptime(mindate, '%Y-%m-%d')
        formatmindate = mindate.date()
    else:
        formatmindate = None
    if maxdate is not None:
        maxdate = datetime.datetime.strptime(maxdate, '%Y-%m-%d')
        formatmaxdate = maxdate.date()
    else:
        formatmaxdate = None
    return model.parteB(analyzer, num, formatdate, formatmindate, formatmaxdate, cond)

def numVertex(graph):
    return model.numVertex(graph)

def numEdges(graph):
    return model.numEdges(graph)

def parteC(analyzer, communityAreaOrigin, communityAreaDestination, rangeTime):
    return model.parteC(analyzer, communityAreaOrigin, communityAreaDestination, rangeTime)

