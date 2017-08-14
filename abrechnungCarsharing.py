import csv
from datetime import datetime,timedelta
############################
#Beginn Nutzereingabe

#Gebe eine Liste von Jahren an, die auf einmal bearbeitet werden sollen
year = 2017
#Gebe eine Liste von Monaten an, die bearbeitet werden sollen
month = 6
#Gebe eine Liste von Autobezeichnungen an, die bearbeitet werden sollen
carNames = ['aurCs108']



#Ende Nutzereingabe
############################


############################
#Beginn Definition hilfreicher Funktionen

def calculateCost( distance , duration):
    #[distance] = km
    #[duration] = h
    rate_1 = 0.5   #[Euro / km]
    rate_2 = 0.25  #[Euro / km]
    distanceForRate1 = 140  #[km]
    highDuration = 24 #[h]
    highDurationDistance = 50 #[km]
    if(distance <= distanceForRate1):
        tmp = distance * rate_1
    else:
        tmp = distanceForRate1 * rate_1 + (distance - distanceForRate1) * rate_2
    if(highDuration <= duration):
        tmp = max( [tmp , highDurationDistance * rate_1] )
    return tmp


#Ende Definition hilfreicher Funktionen
############################

#Erstellle eine Liste von Dateinamen ausgehend von den Benutzereingaben
delimiterFileNames = '_'
fileNames = [str(year) + delimiterFileNames +str(month).zfill(2) + delimiterFileNames +carName+'.txt' for carName in carNames]



#Erstelle Dummy Eingabedateien
#with open(fileName, 'w+' ,newline='') as myFile:
#    myWriter = csv.writer(myFile, delimiter=';')
#    for i in range(1,10):
#        myWriter.writerow( ['Julian'] + [str(i)] + [str(i).zfill(2) + str(0).zfill(2)] + [str(i+20)] + [str(i)] + [str(i+10).zfill(2) + str(0).zfill(2)])


#Definiere Indices fuer verschiedene Datenbestandteile in den Eingabedateien
columns = {
'driverName'    :0,
'dateBegin' :1,
'timeBegin' :2,
'distance'  :3,
'dateEnd'   :4,
'timeEnd'   :5
}

#Lese Daten aus den Eingabedateien ein
inputData = []
for filename in fileNames:
    with open(filename,'r',newline='') as myFile:
        myReader = csv.reader(myFile, delimiter = ';')
        inputData.extend(list(myReader))

#Strip inputData d.h. entferne Leerzeichen und Zeilenspruenge aus den Strings
for index,data in enumerate(inputData):
    inputData[index] = [ x.strip() for x in data ]

#Wandle die Daten aus dem Eingabeformat um in ein einfach zu bearbeitendes Berechnungsformat um und berechne die Kosten jedes Eintrages
calculationData = []
for data in inputData:
    name = data[ columns['driverName'] ]
    begin = datetime.strptime( str(year)+str(month).zfill(2)+data[ columns['dateBegin'] ].zfill(2) + data[ columns['timeBegin'] ],'%Y%m%d%H%M' )
    end = datetime.strptime( str(year)+str(month).zfill(2)+data[ columns['dateEnd'] ].zfill(2) + data[ columns['timeEnd'] ],'%Y%m%d%H%M' )
    distance = int(data[ columns['distance'] ])
    cost = calculateCost( distance , ((end-begin).total_seconds()) / (60*60) )
    calculationData.append([name,begin,end,distance, cost])





#    for row in data:
#        print(row)
#        for element in columns:
#            print(element + '\t' + row[columns[element]].strip())


