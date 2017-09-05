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
            + entry['date'] + delimiterLatexTable \
            + entry['carName'].upper() + delimiterLatexTable \
            + '{:.2f}'.format( entry['duration'] )+ delimiterLatexTable \
            + '{:.2f}'.format( entry['distance'] )+ delimiterLatexTable \
            + '{:.2f}'.format( entry['cost'] )
        if(index != lastIndex):
            tmpStr = tmpStr + endLineLatexTable + '\n'
    return tmpStr

#Ende Definition Funktionen
############################


############################
#Beginn Einlesen der Rohdaten

#Erstellle eine Liste von Dateinamen ausgehend von den Benutzereingaben
delimiterFileNames = '_'
fileNames = [str(year) + delimiterFileNames +str(month).zfill(2) + delimiterFileNames +carName+'.txt' for carName in carNames]

#Definiere Keys fuer verschiedene Datenbestandteile in den Eingabedateien
keysInputData = ['driverName','dateBegin','timeBegin','distance','dateEnd','timeEnd']
#Lese Daten aus den Eingabedateien ein
inputData = []
for index,filename in enumerate(fileNames):
    with open(os.path.join(dataDirectory,filename),'r', newline='') as myFile:
        next(myFile)    #Skip Header
        myReader = csv.DictReader(myFile, keysInputData, delimiter = ',')
        #Strip input, d.h. entferne Leerzeichen und Zeilenspruenge aus den Strings
        for data in myReader:
            if data:    #only append driverData if data is not empty list
                inputData.append( { key : value.strip() for key,value in data.items() } )
                inputData[-1]['carName'] = carNames[index]   #Fuege den Aktuellen Fahrzeugnamen zu jedem Eintrag in inputData hinzu


#Definiere Keys fuer verschiedene Datenbestandteile in dem Fahrerverzeichnis
keysDriver = ['driverName', 'firstName','lastName','street','streetNumber','postcode','city']
#Lese das Fahrerverzeichnis ein
driverData = {}
with open(fileNameDriverDirectory,'r',newline = '') as myFile:
    next(myFile)    #Skip Header
    myReader = csv.DictReader(myFile,keysDriver,delimiter = ',')
    #Strip input, d.h. entferne Leerzeichen und Zeilenspruenge aus den Strings
    for data in myReader:
        if data:    #only append data to driverData if data is not empty list
            driverData[data['driverName']] = { key : value.strip() for key,value in data.items()}


#Ende Einlesen der Rohdaten
############################

############################
#Beginn Bearbeitung der Daten

#Wandle die Daten aus dem Eingabeformat um in ein Ausgabeformat mit berechneter Dauer und berechneten Kosten
calcData = []
beginStringFormat = ''
for data in inputData:
    name = data[ 'driverName' ]
    begin = calculateDate( year = year, month = month, dateStrZfilled2Numbers = data[ 'dateBegin' ].zfill(2), timeStr4Numbers = data[ 'timeBegin' ])
    end = calculateDate( year = year, month = month, dateStrZfilled2Numbers = data[ 'dateEnd' ].zfill(2), timeStr4Numbers = data[ 'timeEnd' ])
    carName = data[ 'carName' ]
    duration =  ((end-begin).total_seconds()) / (60*60) #Dauer in Stunden
    distance = int(data[ 'distance' ])
    cost = calculateCost( distance , duration )
    
    calcData.append({'driverName' :name, 'date':begin, 'carName':carName, 'duration':duration, 'distance':distance, 'cost':cost})
#Ordne die einzelnen Fahrteintraege den Fahrern zu

#Sortiere calcData nach Fahrer und dann nach Startzeitpunkten
calcData.sort(key = lambda x: (x['driverName'] , x['date'] ) )

#Ersetze den Eintrag begin (datetime object) mit einem String
for data in calcData:
    data['date'] = data['date'].strftime('%d %m %Y')

#Erstelle eine Liste der im betrachteten Monat aktiven Fahrer ausgehend von den Fahrdaten
uniqueDrivers = list(set( map(lambda x:x['driverName'], calcData) ))
uniqueDrivers.sort()

#Erstelle eine Ausgabeliste, die fuer jeden Fahrer eine Liste der Eintraege enthaelt. 
#Diese Liste der Eintraege ist schon geordnet
outData = {}
for driver in uniqueDrivers:
    outData[driver] =  [ x for x in calcData if x['driverName'] == driver ]

#Summiere die Kosten jedes Fahrers
toTemplateSums = {}
for driver in uniqueDrivers:
    tmp = 0
    for data in outData[driver]:
        tmp = tmp + data['cost']    #cost is last entry
    toTemplateSums[driver] = tmp

#Erstelle ein Dictinonary von Dictionaries um Platzhalter in der Vorlage zu ersetzen
toTemplate = {}
for driver in uniqueDrivers:
    tmp = {}
    tmp['settlementDate'] = settlementDate
    tmp['month']    =   (gerMonthNames(month))
    tmp['year']     =   str(year)
    tmp['sum']      =   str(toTemplateSums[driver])
    tmp['firstName']=   driverData[driver]['firstName']
    tmp['lastName'] =   driverData[driver]['lastName']
    tmp['street'] =   driverData[driver]['street']
    tmp['streetNumber'] =   driverData[driver]['streetNumber']
    tmp['postcode'] =   driverData[driver]['postcode']
    tmp['city'] =   driverData[driver]['city']
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




