import csv
from datetime import datetime,timedelta
import sys
############################
#Beginn Nutzereingabe

#Gebe das Jahr des zu bearbeitenden Monats ein
year = 2017
#Gebe den zu bearbeitenden Monat ein
month = 6
#Gebe eine Liste von Autobezeichnungen an, die bearbeitet werden sollen
carNames = ['aurCs108']
#Gebe den Namen des Fahrerverzeichnisses ein
fileNameDriverDirectory = '2017_06_fahrer.txt'

#Ende Nutzereingabe
############################


############################
#Beginn Definition Funktionen

def calculateCost( distance , duration):
    #[distance] = km
    #[duration] = h
    #Es gibt zwei Kilometerpreise. rate_1 gilt bis zu einer Fahrtstrecke von distanceForRate1, danach gilt rate_2
    rate_1 = 0.5   #[Euro / km]
    rate_2 = 0.25  #[Euro / km]
    distanceForRate1 = 140  #[km]
    #Ab einer Zeitdauer von highDuration gibt es einen Mindestpreis, der sich aus einer Mindeststrecke highDurationDistance berechnet.
    highDuration = 24 #[h]
    highDurationDistance = 50 #[km]
    if(distance <= distanceForRate1):
        tmp = distance * rate_1
    else:
        tmp = distanceForRate1 * rate_1 + (distance - distanceForRate1) * rate_2
    if(highDuration <= duration):
        tmp = max( [tmp , highDurationDistance * rate_1] )
    return tmp


def calculateDuration( year, month, dateBeginStrZfilled2Numbers, timeBeginStrT4Numbers ):
    return datetime.strptime( str(year)+str(month).zfill(2)+ dateBeginStrZfilled2Numbers + timeBeginStrT4Numbers,'%Y%m%d%H%M' )

#Ende Definition Funktionen
############################


############################
#Beginn Einlesen der Rohdaten

#Erstellle eine Liste von Dateinamen ausgehend von den Benutzereingaben
delimiterFileNames = '_'
fileNames = [str(year) + delimiterFileNames +str(month).zfill(2) + delimiterFileNames +carName+'.txt' for carName in carNames]

#Definiere Indices fuer verschiedene Datenbestandteile in den Eingabedateien
columns = {
'driverName'    :0,
'dateBegin' :1,
'timeBegin' :2,
'distance'  :3,
'dateEnd'   :4,
'timeEnd'   :5,
'carName'   :6
}

#Lese Daten aus den Eingabedateien ein
inputData = []
for index,filename in enumerate(fileNames):
    with open(filename,'r',newline='') as myFile:
        next(myFile)    #Skip Header
        myReader = csv.reader(myFile, delimiter = ';')
        #Strip input, d.h. entferne Leerzeichen und Zeilenspruenge aus den Strings
        for data in myReader:
            inputData.append( [x.strip() for x in data] )
            inputData[-1].append(carNames[index])   #Fuege den Aktuellen Fahrzeugnamen zu jedem Eintrag in inputData hinzu

#Definiere Indices fuer verschiedene Datenbestandteile in dem Fahrerverzeichnis
columnsDriver = {
'driverName'    :0,
'forename'      :1,
'lastname'      :2,
'street'        :3,
'street number' :4,
'postcode'      :5,
'town'          :6
}

#Lese das Fahrerverzeichnis ein
driverData = []
with open(fileNameDriverDirectory,'r',newline = '') as myFile:
    next(myFile)    #Skip Header
    myReader = csv.reader(myFile,delimiter = ';')
    #Strip input, d.h. entferne Leerzeichen und Zeilenspruenge aus den Strings
    for data in myReader:
        driverData.append( [x.strip() for x in data] )

#Ende Einlesen der Rohdaten
############################

############################
#Beginn Bearbeitung der Daten

#Wandle die Daten aus dem Eingabeformat um in ein Ausgabeformat mit berechneter Dauer und berechneten Kosten
calcData = []
beginStringFormat = ''
for data in inputData:
    name = data[ columns['driverName'] ]
    begin = calculateDuration( year = year, month = month, dateBeginStrZfilled2Numbers = data[ columns['dateBegin'] ].zfill(2), timeBeginStrT4Numbers = data[ columns['timeBegin'] ])
    end = calculateDuration( year = year, month = month, dateBeginStrZfilled2Numbers = data[ columns['dateEnd'] ].zfill(2), timeBeginStrT4Numbers = data[ columns['timeEnd'] ])
    carName = data[ columns['carName']  ]
    duration =  ((end-begin).total_seconds()) / (60*60) #Dauer in Stunden
    distance = int(data[ columns['distance'] ])
    cost = calculateCost( distance , duration )
    
    calcData.append([name, begin, carName, duration, distance, cost])

#Ordne die einzelnen Fahrteintraege den Fahrern zu

#Sortiere calcData nach Fahrer und dann nach Startzeitpunkten
calcData.sort(key = lambda x: (x[0] , x[1] ) )

#Ersetze den Eintrag begin (datetime object) mit einem String
for data in calcData:
    data[1] = data[1].strftime('%d %m %Y')
uniqueDrivers = set( map(lambda x:x[0], calcData) )

#Erstelle eine Ausgabeliste, die fuer jeden Fahrer eine Liste der Eintraege in enthaelt. Diese Liste der Eintraege ist schon geordnet
outData = []
for driver in uniqueDrivers:
    outData.append( [ x for x in calcData if x[0] == driver ] )

#Ende Bearbeitung der Daten
############################

############################
#Beginn Erstellung der Ausgabedateien



#    for row in data:
#        print(row)
#        for element in columns:
#            print(element + '\t' + row[columns[element]].strip())



#Erstelle Dummy Eingabedateien
#with open(fileName, 'w+' ,newline='') as myFile:
#    myWriter = csv.writer(myFile, delimiter=';')
#    for i in range(1,10):
#        myWriter.writerow( ['Julian'] + [str(i)] + [str(i).zfill(2) + str(0).zfill(2)] + [str(i+20)] + [str(i)] + [str(i+10).zfill(2) + str(0).zfill(2)])



