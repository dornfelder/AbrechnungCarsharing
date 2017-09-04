import csv
from datetime import datetime,timedelta
import sys
import os
import subprocess
import string
############################
#Beginn Nutzereingabe

#Gebe das Jahr des zu bearbeitenden Monats ein
year = 2017
#Gebe den zu bearbeitenden Monat ein
month = 6
#Gebe den Namen des Ausgabeverzeichnisses an
outputDirectory = './output'
#Gebe den Namen eines Verzeichnisses an, das die Fahrdaten der einzelnen Autos beinhaltet
dataDirectory = './input'
#Gebe eine Liste von Autobezeichnungen an, die bearbeitet werden sollen
carNames = ['aurCs108']
#Gebe den Namen des Fahrerverzeichnisses ein
fileNameDriverDirectory = 'fahrerverzeichnis.txt'
#Gebe den Namen der Latexvorlage ein
fileNameLatexTemplate = './templates/template4Python.tex'


#Gebe das Erstelldatum der Abrechnung ein
settlementDate = '18 August 2017'

#Ende Nutzereingabe
############################


############################
#Beginn Definition Funktionen

def calculateCost( distance , duration):
    #[distance] = km
    #[duration] = h
    #Es gibt zwei Kilometerpreise. rate_1 gilt bis zu einer Fahrtstrecke 
    #von distanceForRate1, danach gilt rate_2
    rate_1 = 0.5   #[Euro / km]
    rate_2 = 0.25  #[Euro / km]
    distanceForRate1 = 150  #[km]
    #Ab einer Zeitdauer von highDuration gibt es einen Mindestpreis, 
    #der sich aus einer Mindeststrecke highDurationDistance berechnet.
    highDuration = 24 #[h]
    highDurationDistance = 50 #[km]
    if(distance <= distanceForRate1):
        tmp = distance * rate_1
    else:
        tmp = distanceForRate1 * rate_1 + (distance - distanceForRate1) * rate_2
    if(highDuration <= duration):
        tmp = max( [tmp , highDurationDistance * rate_1] )
    return tmp


def calculateDate( year, month, dateStrZfilled2Numbers, timeStr4Numbers ):
    #Gueltge Uhrzeiten sind im Bereich 0000 bis 2359
    #Falls die Uhrzeit 2400 betraegt, ist der passende Tag zu inkrementieren und die Uhrzeit ist auf 2359 zu setzen
    if timeStr4Numbers == '2400':
        tmp = datetime.strptime( str(year)+str(month).zfill(2)+ dateStrZfilled2Numbers + '0000','%Y%m%d%H%M' )+timedelta(days = 1)
    else:
        tmp = datetime.strptime( str(year)+str(month).zfill(2)+ dateStrZfilled2Numbers + timeStr4Numbers,'%Y%m%d%H%M' )
    return tmp 

def gerMonthNames(integerMonth):
    #Gebe den deutschen Monatsbezeichner als String zurueck
    #Erstelle eine Liste der deutschen Monatsbezeichner, da die lokalen Datumsangaben der Bibliothek Datetime Platformabhaengig sind.
    gerMonthsNamesList = ['Januar', 'Februar', 'März' ,'April', 'Mai','Juni','Juli','August','September','Oktober','November','Dezember']
    if (1 <= integerMonth) & (integerMonth <=12):
        tmp = gerMonthsNamesList[integerMonth-1]
    else:
        sys.exit('Der Parameter zu gerMonthNames ist kein Integer im Bereich 1 bis 12')
    return tmp

def formatOutData(tripList):
    delimiterLatexTable = '&'
    endLineLatexTable = r'\\\hline'
    tmpStr = ''
    lastIndex = len(tripList)-1
    for index,entry in enumerate(tripList):
        tmpStr = tmpStr \
            + entry[columnsCalcData['date']] + delimiterLatexTable \
            + entry[columnsCalcData['carName']].upper() + delimiterLatexTable \
            + '{:.2f}'.format( entry[columnsCalcData['duration']] )+ delimiterLatexTable \
            + '{:.2f}'.format( entry[columnsCalcData['distance']] )+ delimiterLatexTable \
            + '{:.2f}'.format( entry[columnsCalcData['cost']] )
        if(index != lastIndex):
            tmpStr = tmpStr + endLineLatexTable + '\n'
    return tmpStr
#columnsCalcData = {
#'driverName'    :0,
#'date'          :1,
#'carName'       :2,
#'duration'      :3,
#'distance'      :4,
#'cost'          :5
#}

#Ende Definition Funktionen
############################


############################
#Beginn Einlesen der Rohdaten

#Erstellle eine Liste von Dateinamen ausgehend von den Benutzereingaben
delimiterFileNames = '_'
fileNames = [str(year) + delimiterFileNames +str(month).zfill(2) + delimiterFileNames +carName+'.txt' for carName in carNames]

#Definiere Indices fuer verschiedene Datenbestandteile in den Eingabedateien
#!#ImprovementNote:inputData should be organiszed as dictionary and reused when toTemplate is created.
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
    with open(os.path.join(dataDirectory,filename),'r', newline='') as myFile:
        next(myFile)    #Skip Header
        myReader = csv.reader(myFile, delimiter = ';')
        #Strip input, d.h. entferne Leerzeichen und Zeilenspruenge aus den Strings
        for data in myReader:
            inputData.append( [x.strip() for x in data] )
            inputData[-1].append(carNames[index])   #Fuege den Aktuellen Fahrzeugnamen zu jedem Eintrag in inputData hinzu

#Definiere Indices fuer verschiedene Datenbestandteile in dem Fahrerverzeichnis
#!#ImprovementNote:driverData should be organiszed as dictionary and reused when toTemplate is created.
columnsDriver = {
'driverName'    :0,
'lastName'      :1,
'firstName'     :2,
'street'        :3,
'streetNumber'  :4,
'postcode'      :5,
'city'          :6
}

#Lese das Fahrerverzeichnis ein
driverData = {}
with open(fileNameDriverDirectory,'r',newline = '') as myFile:
    next(myFile)    #Skip Header
    myReader = csv.reader(myFile,delimiter = ';')
    #Strip input, d.h. entferne Leerzeichen und Zeilenspruenge aus den Strings
    for data in myReader:
        driverData[data[0]] = [x.strip() for x in data]

#Ende Einlesen der Rohdaten
############################

############################
#Beginn Bearbeitung der Daten

#Wandle die Daten aus dem Eingabeformat um in ein Ausgabeformat mit berechneter Dauer und berechneten Kosten
#!#ImprovementNote:Design calcData as Dictionary
calcData = []
beginStringFormat = ''
for data in inputData:
    name = data[ columns['driverName'] ]
    begin = calculateDate( year = year, month = month, dateStrZfilled2Numbers = data[ columns['dateBegin'] ].zfill(2), timeStr4Numbers = data[ columns['timeBegin'] ])
    end = calculateDate( year = year, month = month, dateStrZfilled2Numbers = data[ columns['dateEnd'] ].zfill(2), timeStr4Numbers = data[ columns['timeEnd'] ])
    carName = data[ columns['carName']  ]
    duration =  ((end-begin).total_seconds()) / (60*60) #Dauer in Stunden
    distance = int(data[ columns['distance'] ])
    cost = calculateCost( distance , duration )
    
    calcData.append([name, begin, carName, duration, distance, cost])   #cost is last entry
columnsCalcData = {
'driverName'    :0,
'date'          :1,
'carName'       :2,
'duration'      :3,
'distance'      :4,
'cost'          :5
}
#Ordne die einzelnen Fahrteintraege den Fahrern zu

#Sortiere calcData nach Fahrer und dann nach Startzeitpunkten
#!#ImprovementNote:Adjust to use dictionary
calcData.sort(key = lambda x: (x[0] , x[1] ) )

#Ersetze den Eintrag begin (datetime object) mit einem String
#!#ImprovementNote: entry 'date' of calcData as string straight away from the beginning
for data in calcData:
    data[1] = data[1].strftime('%d %m %Y')

#Erstelle eine Liste der im betrachteten Monat aktiven Fahrer ausgehend von den Fahrdaten
#!#ImprovementNote:Adjust to use dictionary
uniqueDrivers = list(set( map(lambda x:x[0], calcData) ))
uniqueDrivers.sort()

#Erstelle eine Ausgabeliste, die fuer jeden Fahrer eine Liste der Eintraege enthaelt. 
#Diese Liste der Eintraege ist schon geordnet
#!#ImprovementNote:Adjust to use dictionary
outData = {}
for driver in uniqueDrivers:
    outData[driver] =  [ x for x in calcData if x[0] == driver ]

#Summiere die Kosten jedes Fahrers
#!#ImprovementNote:Adjust to use dictionary
toTemplateSums = {}
for driver in uniqueDrivers:
    tmp = 0
    for data in outData[driver]:
        tmp = tmp + data[-1]    #cost is last entry
    toTemplateSums[driver] = tmp

#Erstelle ein Dictinonary von Dictionaries um Platzhalter in der Vorlage zu ersetzen
toTemplate = {}
for driver in uniqueDrivers:
    tmp = {}
    tmp['settlementDate'] = settlementDate
    tmp['month']    =   (gerMonthNames(month))
    tmp['year']     =   str(year)
    tmp['sum']      =   str(toTemplateSums[driver])
    tmp['firstName']=   driverData[driver][columnsDriver['firstName']]
    tmp['lastName'] =   driverData[driver][columnsDriver['lastName']]
    tmp['street'] =   driverData[driver][columnsDriver['street']]
    tmp['streetNumber'] =   driverData[driver][columnsDriver['streetNumber']]
    tmp['postcode'] =   driverData[driver][columnsDriver['postcode']]
    tmp['city'] =   driverData[driver][columnsDriver['city']]
    tmp['table'] = formatOutData( outData[driver] )
    #table data has to be added.
    toTemplate[driver] = tmp

#Read template4Python into variable
with open(fileNameLatexTemplate,'r', newline='') as myFile:
    templateStr = myFile.read()

class latexTemplate(string.Template):
    delimiter = "##"

toFileLatex = latexTemplate(templateStr)

#print(toFileLatex.substitute(**toTemplate['Alex']) )
dirName = os.path.join(outputDirectory, '{}_{}'.format( str(year),str(month).zfill(2)) )
if not os.path.exists(dirName):
    os.makedirs(dirName)

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

uselessFilesEndings = ['.tex','.aux','.log']
for driver in uniqueDrivers:
    fileName = os.path.join(os.getcwd(), dirName ,'{}.tex'.format( driver ) )
    with open( fileName , 'w' ,newline = '\n') as myFile:
        myFile.write(toFileLatex.substitute(**toTemplate[driver]))
    with cd( os.path.join(os.getcwd(), dirName) ):
        cmd = ['pdflatex', '-interaction', 'nonstopmode', fileName]
        proc = subprocess.Popen(cmd)
        proc.communicate()
        for ending in uselessFilesEndings:
            os.unlink('{}{}'.format(driver,ending))




