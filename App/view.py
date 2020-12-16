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


import sys
import config
from App import controller
from DISClib.ADT import stack
from DISClib.DataStructures import listiterator as it
import timeit
assert config

"""
La vista se encarga de la interacción con el usuario.
Presenta el menu de opciones  y  por cada seleccion
hace la solicitud al controlador para ejecutar la
operación seleccionada.
"""

# ___________________________________________________
#  Variables
# ___________________________________________________

smallfile = 'taxi-trips-wrvz-psew-subset-small.csv'
mediumfile = 'taxi-trips-wrvz-psew-subset-medium.csv'

# ___________________________________________________
#  Menu principal
# ___________________________________________________

def printMenu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("1- Inicializar Analizador")
    print("2- Cargar información de Taxis de Chicago")
    print("3- Parte A")
    print("4- Parte B")
    print("5- Parte C")
    print("0- Salir")
    print("*******************************************")

def optionTwo1():
    controller.loadData(cont, smallfile)

def optionThree():
    parte1=controller.totalTaxis(cont)
    print("Se tienen: "+str(parte1)+" "+"Taxis en total")
    parte2=controller.totalCompanies(cont)
    print("Se tienen: "+str(parte2)+" "+"empresas en total")
    num = int(input("¿Cuántas compañías se revisarán (top taxis)? \n"))
    num2 = int(input("¿Cuántas compañías se revisarán (top servicios)? \n"))
    info = controller.companiesByTaxis(cont, num)
    infoIterator = it.newIterator(info)
    print('Compañia:\tNúmero de taxis afiliado:\n')
    while it.hasNext(infoIterator):
        elem = it.next(infoIterator)
        print(elem['company'], '\t', elem['taxis'])
    
    info2 = controller.companiesByServices(cont, num2)
    infoIterator2 = it.newIterator(info2)
    print('Compañia:\tNúmero de servicios afiliado:\n')
    while it.hasNext(infoIterator2):
        elem = it.next(infoIterator2)
        print(elem['company'], '\t', elem['servicios'])

def optionFour():
    cond = None
    while cond != '1' and cond != '2':
        cond = input('¿Desea conocer los taxis con más puntos en una fecha o en un rango de fechas?\n1. Una fecha.\n2. Rango de fechas.\n')
    if cond == '1':
        cond = True
        fecha = input('¿Cuál fecha desea consultar?\n')
        num = int(input('¿Cuántos taxis desea conocer?\n'))
        info = controller.parteB(cont, num, cond, fecha=fecha)
    else:
        cond = False
        fechamin = input('¿Cuál es la fecha menor del rango?\n')
        fechamax = input('¿Cuál es la fecha mayor del rango?\n')
        num = int(input('¿Cuántos taxis desea conocer?\n'))
        info = controller.parteB(cont, num, cond, mindate=fechamin, maxdate=fechamax)
    if info is not None:
        infoIterator = it.newIterator(info)
        print('Taxi Id\t\t\t\t\t\t\t\t\t\t\t\t\tPuntaje')
        while it.hasNext(infoIterator):
            elem = it.next(infoIterator)
            print(elem[0], '|', elem[1])
    else:
        print('No hay información disponible')

def optionFive():
    answer = controller.parteC(cont, communityAreaOrigin, communityAreaDestination, rangeTime)
    duration = str(answer["duration"])
    route = answer["route"]
    time = answer["bestTime"]
    print("A) La mejor hora para salir desde el community area " + communityAreaOrigin + ", es: " + time)
    print("B) La ruta es: ")
    if route != None:
        iterator = it.newIterator(route)
        while it.hasNext(iterator):
            vertex = it.next(iterator)
            vertex = vertex["vertexA"] + " --> " + vertex["vertexB"]
            print(" " + station)
    else:
        print("No existe un recorrido")
    print("C) El tiempo del recorrido es: " + duration + " segundos")

while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n>')

    if int(inputs[0]) == 1:
        print("\nInicializando....")
        # cont es el controlador que se usará de acá en adelante
        cont = controller.init()
    
    elif int(inputs[0]) == 2:
        executiontime = timeit.timeit(optionTwo1, number=1)
        graph = cont['AreaGraph']
        print("El número de vértices del grafo de community areas es de: " + str(controller.numVertex(graph)))
        print("El número de arcos del grafo de community areas es de: " + str(controller.numEdges(graph)))
        print("Tiempo de ejecución: " + str(executiontime) + " segundos")
    
    elif int(inputs[0]) == 3:
        executiontime = timeit.timeit(optionThree, number=1)
        print("Tiempo de ejecución: " + str(executiontime) + " segundos")

    elif int(inputs[0]) == 4:
        executiontime = timeit.timeit(optionFour, number=1)
        print("Tiempo de ejecución: " + str(executiontime) + " segundos")

    elif int(inputs[0]) == 5:
        communityAreaOrigin = str(input("Ingrese una community area de partida (número entero): "))
        communityAreaDestination = str(input("Ingrese una community area de llegada (número entero): "))
        rangeTime = input("Ingrese un rango de horas de la forma HH:MM-HH:MM, de otra manera saldrá error: ")
        executiontime = timeit.timeit(optionFive, number=1)
        print("Tiempo de ejecución: " + str(executiontime) + " segundos")
        
    else:
        sys.exit(0)
sys.exit(0)

"""
Menu principal
"""