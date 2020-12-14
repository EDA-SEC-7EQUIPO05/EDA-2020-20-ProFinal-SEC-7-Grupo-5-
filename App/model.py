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
import datetime
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.ADT import list as lt
from DISClib.ADT import indexminpq as ipq
from DISClib.ADT import orderedmap as om
from DISClib.ADT import minpq as pq
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
    analyzer = {'TaxiNum': None, 'TaxiPQ': None, 'ServicePQ': None, 'PointsTree': None}
    analyzer["TaxiNum"] = m.newMap(numelements=2000,
                                              maptype="PROBING",
                                              comparefunction=compareCompanies)
    analyzer['TaxiPQ'] = {'PQ': ipq.newIndexMinPQ(compareCompanies), 'Map': m.newMap(numelements=500, comparefunction=compareCompanies)}
    analyzer['PointsTree'] = om.newMap(omaptype='BST',comparefunction=compareDates)
    return analyzer

# Funciones para agregar informacion al grafo

def addService(analyzer, service):
    company = service['company']
    taxi_id = service['taxi_id']
    if service['trip_total'] is not '':
        money = float(service['trip_total'])
    else:
        money = 0
    if service['trip_miles'] is not '':
        distance = float(service['trip_miles'])
    else:
        distance = 0
    date = getDate(service['trip_start_timestamp'])
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
    if money > 0 and distance > 0:
        uptadePointsTree(analyzer, date, taxi_id, money, distance)
    
    return analyzer

def uptadePointsTree(analyzer, date, taxi_id, money, distance):
    tree = analyzer['PointsTree']
    esta = om.contains(tree, date)
    if esta:
        dateEntry = om.get(tree, date)
        dateValue = me.getValue(dateEntry)
        if m.contains(dateValue['TaxiMap'], taxi_id):
            taxiEntry = m.get(dateValue['TaxiMap'], taxi_id)
            taxiValue = me.getValue(taxiEntry)
            updateTaxiPoints(taxiValue, money, distance)
        else:
            taxiValue = newTaxiEntry(taxi_id)
            updateTaxiPoints(taxiValue, money, distance)
            m.put(dateValue['TaxiMap'], taxi_id, taxiValue)
    else:
        dateValue = newDateEntry(date)
        taxiValue = newTaxiEntry(taxi_id)
        updateTaxiPoints(taxiValue, money, distance)
        m.put(dateValue['TaxiMap'], taxi_id, taxiValue)
        om.put(tree, date, dateValue)
    return analyzer

def updateTaxiPoints(taxiEntry, money, distance):
    old_services = taxiEntry['services']
    old_money = taxiEntry['money']
    old_distance = taxiEntry['distance']
    new_services = old_services + 1
    new_money = old_money + money
    new_distance = old_distance + distance
    new_points = (new_distance/new_money)*new_services
    taxiEntry['points'] = new_points

def newTaxiEntry(taxi_id):
    Entry = {'id': taxi_id, 'points': 0, 'services': 0, 'money': 0, 'distance': 0}
    return Entry

def newDateEntry(date):
    Entry = {'date': date, 'TaxiMap': None}
    Entry['TaxiMap'] = m.newMap(numelements=75000, comparefunction=compareTaxiId)
    return Entry

# ==============================
# Funciones de consulta
# ==============================

def companiesByTaxis(analyzer, num):
    maxPQ = analyzer['TaxiPQ']['PQ'].copy()
    PQ_map = analyzer['TaxiPQ']['Map']
    cont = 0
    companies = lt.newList()
    while cont < num:
        comp = ipq.delMin(maxPQ)
        index = lt.size(me.getValue(m.get(PQ_map, comp)))
        entry = {'company': comp, 'taxis': index}
        lt.addLast(companies, entry)
        cont += 1
    return companies

def totalTaxis(analyzer):
    cont=0
    lista=[]
    lista2=[]
    valores=m.valueSet(analyzer["TaxiNum"])
    iterator_valores= it.newIterator(valores)
    while it.hasNext(iterator_valores):
        elemento=it.next(iterator_valores)
        lista.append(elemento)

    for i in lista:
        valor=i
        for k in valor:
            numeros=valor[k]
            lista2.append(numeros)

    for z in lista2:
        cont+=z

    return cont

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

def parteB(analyzer, num, date, mindate, maxdate, cond):
    tree = analyzer['PointsTree']
    if cond:
        taxis = getMaxPointsinDate(tree, date, num)
        return taxis
    else:
        taxis = getMaxPointsinDateRange(tree, mindate, maxdate, num)
        return taxis

# ==============================
# Funciones Helper
# ==============================


def getDate(timedate):
    taxitripdatetime = datetime.datetime.strptime(timedate, '%Y-%m-%dT%H:%M:%S.%f')
    return taxitripdatetime.date()

def getMaxPointsinDate(tree, date, num):
    dateEntry = om.get(tree, date)
    if dateEntry is not None:
        minPQ = pq.newMinPQ(comparePoints)
        dateValue = me.getValue(dateEntry)
        taxiMap = dateValue['TaxiMap']
        taxiList = m.keySet(taxiMap)
        taxiIterator = it.newIterator(taxiList)
        while it.hasNext(taxiIterator):
            elem = it.next(taxiIterator)
            taxiValue = me.getValue(m.get(taxiMap, elem))
            taxipoints = taxiValue['points']
            pq.insert(minPQ, (elem, taxipoints))
        cont = 0
        taxis = lt.newList()
        while cont < num:
            taxi = pq.delMin(minPQ)
            lt.addLast(taxis, taxi)
            cont +=1
        return taxis
    else:
        return None

def getMaxPointsinDateRange(tree, mindate, maxdate, num):
    taxiPoints = m.newMap(numelements=75000, comparefunction=compareTaxiId)
    taxiPointsPQ = pq.newMinPQ(comparePoints)
    dateRange = om.values(tree, mindate, maxdate)
    dateIterator = it.newIterator(dateRange)
    while it.hasNext(dateIterator):
        elem = it.next(dateIterator)
        taxiMap = elem['TaxiMap']
        taxiIterator = it.newIterator(m.keySet(taxiMap))
        while it.hasNext(taxiIterator):
            eleme = it.next(taxiIterator)
            if m.contains(taxiPoints, eleme):
                entry = me.getValue(m.get(taxiMap, eleme))
                add_points = entry['points']
                other_entry = me.getValue(m.get(taxiPoints, eleme))
                other_entry['points'] += add_points
            else:
                entry = me.getValue(m.get(taxiMap, eleme))
                add_points = entry['points']
                other_entry = {'taxi_id': eleme, 'points': add_points}
                m.put(taxiPoints, eleme, other_entry)
    keyPoints = m.keySet(taxiPoints)
    keyIterator = it.newIterator(keyPoints)
    while it.hasNext(keyIterator):
        el = it.next(keyIterator)
        points = me.getValue(m.get(taxiPoints, el))['points']
        pq.insert(taxiPointsPQ, (el, points))
    cont = 0
    taxiList = lt.newList()
    while cont < num:
        tax = pq.delMin(taxiPointsPQ)
        lt.addLast(taxiList, tax)
        cont += 1
    return taxiList

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


def compareTaxiId(id1, id2):
    idEntry = me.getKey(id2)
    if id1 == idEntry:
        return 0
    elif id1 > idEntry:
        return 1
    else:
        return -1

def comparePoints(point1, point2):
    if point1[1] == point2[1]:
        return 0
    if point1[1] > point2[1]:
        return -1
    else:
        return 1

def compareDates(date_1, date_2):
    if date_1 == date_2:
        return 0
    elif date_1 > date_2:
        return 1
    else:
        return -1