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
import config
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.ADT import indexminpq as ipq
from DISClib.DataStructures import listiterator as it
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
assert config

"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# -----------------------------------------------------
#                       API
# -----------------------------------------------------

def newAnalyzer():
    analyzer = {'TaxiNum': None, 'TaxiPQ': None, 'ServicePQ': None}
    analyzer["TaxiNum"] = m.newMap(numelements=2000,
                                              maptype="PROBING",
                                              comparefunction=compareCompanies)
    analyzer['TaxiPQ'] = {'PQ': ipq.newIndexMinPQ(compareCompanies), 'Map': m.newMap(numelements=500, comparefunction=compareCompanies)}
    return analyzer

# Funciones para agregar informacion al grafo

def addService(analyzer, service):
    company = service['company']
    taxi_id = service['taxi_id']
    if company == '':
        company = 'Independent Owner'
    if not ipq.contains(analyzer['TaxiPQ']['PQ'], company):
        taxilist = lt.newList(datastructure='ARRAY_LIST', cmpfunction=compareCompanies2)
        lt.addLast(taxilist, taxi_id)
        m.put(analyzer['TaxiPQ']['Map'], company, taxilist)
        ipq.insert(analyzer['TaxiPQ']['PQ'], company, 1)
    else:
        taxilist = me.getValue(m.get(analyzer['TaxiPQ']['Map'], company))
        if not lt.isPresent(taxilist, company):
            lt.addLast(taxilist, taxi_id)
            ipq.increaseKey(analyzer['TaxiPQ']['PQ'], company, lt.size(taxilist))
    if not m.contains(analyzer["TaxiNum"],company):
        m.put(analyzer["TaxiNum"],company,{"Taxi":0})
    else:
        valor=me.getValue(m.get(analyzer["TaxiNum"],company)) 
        valor["Taxi"]+=1
    
    return analyzer

# ==============================
# Funciones de consulta
# ==============================

def companiesByTaxis(analyzer, num):
    maxPQ = analyzer['TaxiPQ']['PQ']
    PQ_map = analyzer['TaxiPQ']['Map']
    cont = 0
    companies = lt.newList()
    while cont < num:
        comp = ipq.min(maxPQ)
        ipq.delMin(maxPQ)
        index = lt.size(me.getValue(m.get(PQ_map, comp)))
        entry = {'company': comp, 'taxis': index}
        lt.addLast(companies, entry)
        cont += 1
    return companies

def totalTaxis(analyzer):
    cont=0
    lista=[]
    valores=m.valueSet(analyzer["TaxiNum"])
    iterator_valores= it.newIterator(valores)
    while it.hasNext(iterator_valores):
        elemento=it.next(iterator_valores)
        lista.append(elemento)

    return lista

def totalCompanies(analyzer):
    cont=0
    lista=[]
    llaves=m.keySet(analyzer["TaxiNum"])
    iterator_llaves= it.newIterator(llaves)
    while it.hasNext(iterator_llaves):
        elemento=it.next(iterator_llaves)
        lista.append(elemento)

    for i in lista:
        cont+=1

    return cont

# ==============================
# Funciones Helper
# ==============================

# ==============================
# Funciones de Comparacion
# ==============================

def compareCompanies(comp, keyvaluecomp):
    """
    Compara dos compañias (mapa)
    """
    compkey = keyvaluecomp['key']
    if (comp == compkey):
        return 0
    elif (comp > compkey):
        return 1
    else:
        return -1


def compareCompanies2(comp1, comp2):
    """
    Compara dos compañias (lista)
    """
    if (comp1 == comp2):
        return 0
    elif (comp1 > comp2):
        return 1
    else:
        return -1