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
from math import inf
assert config


"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# -----------------------------------------------------
#                       API
# -----------------------------------------------------

def newAnalyzer():
    analyzer = {'TaxiNum': None, 'TaxiPQ': None, 'ServicePQ': None, 'ServicePQ': None, 'PointsTree': None, 'AreaGraph': None}
    analyzer["TaxiNum"] = m.newMap(numelements=2000,
                                              maptype="PROBING",
                                              comparefunction=compareCompanies)
    analyzer['TaxiPQ'] = {'PQ': ipq.newIndexMinPQ(compareCompanies), 'Map': m.newMap(numelements=500, comparefunction=compareCompanies)}
    analyzer['ServicePQ'] = {'PQ': ipq.newIndexMinPQ(compareCompanies), 'Map': m.newMap(numelements=500, comparefunction=compareCompanies)}
    analyzer['PointsTree'] = om.newMap(omaptype='BST',comparefunction=compareDates)
    analyzer['AreaGraph'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=1000,
                                              comparefunction = compareAreas)
    return analyzer

# Funciones para agregar informacion al grafo

def addService(analyzer, service):
    company = service['company']
    taxi_id = service['taxi_id']
    service_id = service['trip_id']
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
        if not lt.isPresent(taxilist, taxi_id):
            lt.addLast(taxilist, taxi_id)
        m.put(analyzer['TaxiPQ']['Map'], company, taxilist)
        ipq.insert(analyzer['TaxiPQ']['PQ'], company, 1)
    else:
        taxilist = me.getValue(m.get(analyzer['TaxiPQ']['Map'], company))
        if not lt.isPresent(taxilist, company):
            if not lt.isPresent(taxilist, taxi_id):
                lt.addLast(taxilist, taxi_id)
            ipq.increaseKey(analyzer['TaxiPQ']['PQ'], company, lt.size(taxilist))
    
    if not ipq.contains(analyzer['ServicePQ']['PQ'], company):
        servicelist = lt.newList(datastructure='ARRAY_LIST', cmpfunction=compareCompanies2)
        lt.addLast(servicelist, service_id)
        m.put(analyzer['ServicePQ']['Map'], company, servicelist)
        ipq.insert(analyzer['ServicePQ']['PQ'], company, 1)
    else:
        servicelist = me.getValue(m.get(analyzer['ServicePQ']['Map'], company))
        if not lt.isPresent(servicelist, company):
            lt.addLast(servicelist, service_id)
            ipq.increaseKey(analyzer['ServicePQ']['PQ'], company, lt.size(servicelist))


    if not m.contains(analyzer["TaxiNum"],company):
        m.put(analyzer["TaxiNum"],company,{"Taxi":0})
    else:
        valor=me.getValue(m.get(analyzer["TaxiNum"],company)) 
        valor["Taxi"]+=1
    if money > 0 and distance > 0:
        uptadePointsTree(analyzer, date, taxi_id, money, distance)
    addServiceToGraph(analyzer, service)
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

def addServiceToGraph(analyzer, service):
    graph = analyzer['AreaGraph']
    originArea = service['pickup_community_area']
    destinationArea = service['dropoff_community_area']
    startTime = convertTime(str(service['trip_start_timestamp']))
    endTime = convertTime(str(service['trip_end_timestamp']))
    try:
        duration = float(service["trip_seconds"])
    except:
        duration = None
    if (originArea != destinationArea) and (startTime != None) and (endTime != None) and (duration != None) and (originArea != "") and (destinationArea != ""):
        originArea = str(int(float(originArea)))
        destinationArea = str(int(float(destinationArea)))
        originVertex = originArea + "-" + startTime
        destinationvertex = destinationArea + "-" + endTime
        if not gr.containsVertex(graph, originVertex):
            gr.insertVertex(graph, originVertex)
        if not gr.containsVertex(graph, destinationvertex):
            gr.insertVertex(graph, destinationvertex)
        addConnection(graph,  originVertex, destinationvertex, duration)

def addConnection(graph,  originVertex, destinationvertex, duration):
    edge = gr.getEdge(graph, originVertex, destinationvertex)
    if edge is None:
        weight = [duration, 1]
        gr.addEdge(graph, originVertex, destinationvertex, weight)
    else:
        edge['weight'][0] = (edge['weight'][0]*edge['weight'][1] + duration)/(edge['weight'][1] + 1)
        edge['weight'][1] += 1
    
# ==============================
# Funciones de consulta
# ==============================

def numVertex(graph):
    return gr.numVertices(graph)

def numEdges(graph):
    return gr.numEdges(graph)

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

def companiesByServices(analyzer, num):
    maxPQ = analyzer['ServicePQ']['PQ'].copy()
    PQ_map = analyzer['ServicePQ']['Map']
    cont = 0
    companies = lt.newList()
    while cont < num:
        comp = ipq.delMin(maxPQ)
        index = lt.size(me.getValue(m.get(PQ_map, comp)))
        entry = {'company': comp, 'servicios': index}
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

def parteC(analyzer, communityAreaOrigin, communityAreaDestination, rangeTime):
    answer = {"bestTime": "No identificada", "route": None, "duration": inf}
    graph = analyzer['AreaGraph']
    rangeTime2 = rangeTime.split("-")
    ls = aboutQuarterHour(rangeTime2[0])
    totalq = allQuartersInRange(rangeTime)
    totalq.append(ls)
    endVertexes = []
    vertexes = gr.vertices(graph)
    iterator = it.newIterator(vertexes)
    while it.hasNext(iterator):
        vertex2 = it.next(iterator)
        vertex2 = vertex2.split("-")
        if communityAreaDestination == vertex2[0]:
            endVertexes.append("-".join(vertex2))
    for i in totalq:
        initialVertex = communityAreaOrigin + "-" + i
        if gr.containsVertex(graph, initialVertex):
            print("A")
            search = djk.Dijkstra(graph, initialVertex)
            print("B")
            for k in endVertexes:
                if djk.hasPathTo(search, k):
                    duration = str(djk.distTo(search, k))
                    route = djk.pathTo(search, k)
                    if float(duration) < float(answer["duration"]):
                        answer["duration"] = duration
                        answer["route"] = route
                        answer["bestTime"] = i
    return answer

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

def convertTime(time):
    a = False
    time = list(time)
    k = 0
    for i in time:
        k += 1
        if i == "T":
            a = True
            break
    if a:
        time = time[k:-1]
    else:
        return None
    time = "".join(time)
    time = time.split(":")
    del time[-1]
    time = ":".join(time)
    return time

def aboutQuarterHour(time):
    time = time.split(":")
    hours = int(time[0])
    minutes = int(time[1])
    a = minutes//15
    b = a + 1
    lq = a*15
    rq = b*15
    ld = abs(minutes - lq)
    rd = abs(minutes - rq)
    if ld > rd:
        minutes = rq
    else:
        minutes = lq
    if minutes == 60:
        hours += 1
        minutes = 0
        if hours == 24:
            hours = 0
            time[0] = str(hours) + "0"
            time[1] = str(minutes) + "0"
        elif hours < 10:
            time[0] = "0" + str(hours)
            time[1] = str(minutes) + "0"
        else:
            time[0] = str(hours)
            time[1] = str(minutes) + "0"
    else:
        if hours < 10:
            if minutes < 10:
                time[0] = "0" + str(hours)
                time[1] = "0" + str(minutes)
            else:
                time[0] = "0" + str(hours)
                time[1] = str(minutes)
        else:
            if minutes < 10:
                time[0] = str(hours)
                time[1] = "0" + str(minutes)
            else:
                time[0] = str(hours)
                time[1] = str(minutes)
    return ":".join(time)

def allQuartersInRange(rangeTime):
    totalq = []
    rangeTime = rangeTime.split("-")
    leftA = aboutQuarterHour(rangeTime[0])
    rightA = aboutQuarterHour(rangeTime[1])
    left_limit = leftA.split(":")
    right_limit = rightA.split(":")
    hoursl = int(left_limit[0])
    hoursr = int(right_limit[0])
    minutesl = int(left_limit[1])
    minutesr = int(right_limit[1])
    minutesBetween = abs((hoursr*60 + minutesr) - (hoursl*60 + minutesl))
    num_quarters = minutesBetween//15
    hours = hoursl
    minutes = minutesl
    for i in range(1, num_quarters + 1):
        quarter = None
        minutes = minutes + 15
        if minutes == 60:
            hours += 1
            minutes = 0
        if hours < 10:
            if minutes < 10:
                quarter = "0" + str(hours) + ":" + "0" + str(minutes)
            else:
                quarter = "0" + str(hours) + ":" + str(minutes)
        else:
            if minutes < 10:
                quarter = str(hours) + ":" + "0" + str(minutes)
            else:
                quarter = str(hours) + ":" + str(minutes)
        totalq.append(quarter)
    return totalq

        

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

def compareAreas(area, keyvalueArea):
    """
    Compara dos compañias (mapa)
    """
    compkey = keyvalueArea['key']
    if (area == compkey):
        return 0
    elif (area > compkey):
        return 1
    else:
        return -1