import csv
from datetime import datetime,timedelta
import sys
import os
import subprocess
import string
import locale
############################
#Beginn Nutzereingabe

#Workflow:
#1. Erstelle im Verzeichnis 'input' ein Unterverzeichnis nach dem Beispielformat "2017_06".
#2. In diesem Unterverzeichnis erstelle fuer jedes Fahrzeug eine Datei im Format "aurCs108.txt"
#   mit Dateiendung ".txt" und einem Namen, der in der Abrechnugnsauflistugn als Fahrzeugkuerzel
#   verwendet werden kann.
#3. Aktualisiere gegebenfalls das Fahrerverzeichnis "fahrerverzeichnis.txt"
#4. Gib im nachfolgenden Bereich der Nutzereingabe das Jahr und den Monat der zu bearbeitenden Daten ein.
#5- Gib im nachfolgenden Bereich der Nutzereingabe das Erstelldatum der Abrechnung ein.
#6  Fuehre dieses Skript aus.

#Gebe das Jahr des zu bearbeitenden Monats ein
year = 2017
#Gebe den zu bearbeitenden Monat ein
month = 6
#Soll das Erstelldatum der Abrechnung automatisch erstellt werden?
automatischesDatum = True #True oder False

#Gebe das Erstelldatum der Abrechnung manuell ein. (Diese Eingabe wird nur genutzt, falls automatischesDatum = False)
settlementDate = '18. August 2017'

#Ende Nutzereingabe
############################
############################
#Beginn Eingaben eines sonderbaren Nutzers

#Gebe den Namen eines Verzeichnisses an, das die Fahrdaten der einzelnen Autos beinhaltet
# Die Dateinamen ohen Dateiendung in diesem Verzeichnis werden als Bezeichner der Autos in der Abrechnung verwendet.
inputDirectory = 'input/{}_{}'.format( str(year), str(month).zfill(2))
print('Das Eingabeverzeichnis lautet \n"{}"'.format(inputDirectory) )
#Gebe eine Dateiendung ein, die alle Dateien mit Fahrtinformationen im Inputverzeichnis tragen.
fileEnding = '.txt'
#Gebe den Namen des Ausgabeverzeichnisses an
outputDirectory = 'output/{}_{}'.format( str(year), str(month).zfill(2))
#Gebe den Namen einer Latex-Logdatei an, die im Ausgabeverzeichnis erstellt wird
fileNameLatexLog = 'latexLog.txt'
#Gebe den Namen des Fahrerverzeichnisses ein
fileNameDriverDirectory = 'fahrerverzeichnis.txt'
#Gebe den Namen der Latexvorlage ein
fileNameLatexTemplate = './templates/template4Python.tex'

#Erstelle das Erstelldatum der Abrechnung automatisch
if automatischesDatum:
    if os.name == 'posix':#We ware on Linux
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8') # use German locale;
        settlementDate = datetime.now().strftime("%-d. %B %Y")   # %-d >> 9 instead of %d >> 09
    elif os.name ==  'nt':#We are on Windows
        locale.setlocale(locale.LC_ALL, 'deu_deu')
        settlementDate = datetime.now().strftime("%#d. %B %Y")
    else:
        print("#########\n\nDas Betriebssystem ist weder Windows noch Linux\nDas Format des Erstelldatums kann nicht zuverlaessig automatish bestimmt werden.\n Bitte kontrolliere das Erstelldatum und mache eine manuelle EIngabe im Skript.")
        sys(exit)


#Ende Eingaben eines sonderbaren Nutzers
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
    distanceForRate1 = 139  #[km]
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

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#Ende Definition Funktionen
############################


############################
#Beginn Einlesen der Rohdaten

#Erstelle eine Liste von Dateinamen der Dateien, 
#   die sich im Inputverzeichnis befinden und eine bestimmte Endung aufweisen
#Erstelle eine Liste von Namen von Autos, der sich aus den Dateinamen ohne die bestimmte Endung ergibt
fileNames = []
carNames = []
for file in os.listdir(os.path.join(os.getcwd(), inputDirectory)):
    if file.endswith(fileEnding):
        #print(os.path.join(os.path.join(os.getcwd(), inputDirectory), file))
        fileNames.append(file)
        carNames.append(file.replace(fileEnding,''))



#Definiere Keys fuer verschiedene Datenbestandteile in den Eingabedateien
keysInputData = ['driverName','dateBegin','timeBegin','distance','dateEnd','timeEnd']
#Lese Daten aus den Eingabedateien ein
nbrEntriesInputData = []
inputData = []
for index,filename in enumerate(fileNames):
    with open(os.path.join(inputDirectory,filename),'r', newline='') as myFile:
        next(myFile)    #Skip Header
        myReader = csv.DictReader(myFile, keysInputData, delimiter = ',')
        myCount = 0
        for data in myReader:
            if data:    #only append driverData if data is not empty list
                #Strip input, d.h. entferne Leerzeichen und Zeilenspruenge aus den Strings
                inputData.append( { key : value.strip() for key,value in data.items() } )
                inputData[-1]['carName'] = carNames[index]   #Fuege den Aktuellen Fahrzeugnamen zu jedem Eintrag in inputData hinzu
                myCount += 1
        nbrEntriesInputData.append(myCount)

print('und enthaelt folgende Eingabedateien (Anzahl der Eintraege pro Datei)')
for index, name in enumerate(fileNames):
    print('\t'+name+'\t'+'('+str(nbrEntriesInputData[index])+')')

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
    ###Ausgabe
    calcData.append({'driverName' :name, 'date':begin, 'carName':carName, 'duration':duration, 'distance':distance, 'cost':cost})
#Ordne die einzelnen Fahrteintraege den Fahrern zu

#Sortiere calcData nach Fahrer und dann nach Startzeitpunkten
calcData.sort(key = lambda x: (x['driverName'] , x['date'] ) )

#Ersetze den Eintrag begin (datetime object) mit einem String
for data in calcData:
    data['date'] = data['date'].strftime('%d.%m.%Y')

#Erstelle eine Liste der im betrachteten Monat aktiven Fahrer ausgehend von den Fahrdaten
uniqueDrivers = list(set( map(lambda x:x['driverName'], calcData) ))
uniqueDrivers.sort()
print('Folgende Fahrer sind im betrachteten Zeitraum aktiv:')
for driver in uniqueDrivers:
    print('\t'+driver)

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
        tmp = tmp + data['cost']
    toTemplateSums[driver] = tmp

#Erstelle ein Dictinonary von Dictionaries um Platzhalter in der Vorlage zu ersetzen
toTemplate = {}
for driver in uniqueDrivers:
    tmp = {}
    tmp['settlementDate'] = settlementDate
    tmp['month']    =   (gerMonthNames(month))
    tmp['year']     =   str(year)
    tmp['sum']      =   '{:.2f}'.format(toTemplateSums[driver])
    tmp['firstName']=   driverData[driver]['firstName']
    tmp['lastName'] =   driverData[driver]['lastName']
    tmp['street'] =   driverData[driver]['street']
    tmp['streetNumber'] =   driverData[driver]['streetNumber']
    tmp['postcode'] =   driverData[driver]['postcode']
    tmp['city'] =   driverData[driver]['city']
    tmp['table'] = formatOutData( outData[driver] )
    #table data has to be added.
    toTemplate[driver] = tmp

#Lese die Vorlage template4Python in eine Variable
with open(fileNameLatexTemplate,'r', newline='') as myFile:
    templateStr = myFile.read()

#Erstelle ein Python String Template Objekt mti gewuenschtem Trennzeichen
class latexTemplate(string.Template):
    delimiter = "##"
toFileLatex = latexTemplate(templateStr)

#Erstelle das Ausgabeverzeichnis
outDir = os.path.join( os.getcwd(), outputDirectory )
if not os.path.exists(outDir):
    os.makedirs(outDir)

#Erstelle eine Liste von endungen unnoetiger Dateien
uselessFilesEndings = ['.tex','.aux','.log']

print('Erstelle PDF fuer Fahrer:')
#Erstelle die Ausgabedateien (pdf)
#Oeffne eine Logdatei fuer die Ausgabe der Latexbefehle
with open(os.path.join( os.getcwd(),fileNameLatexLog), 'w') as latexLogFile:
    for driver in uniqueDrivers:
        print('\t'+driver)
        fileName = os.path.join(os.getcwd(), outDir ,'{}.tex'.format( driver ) )
        with open( fileName , 'w' ,newline = '\n') as myFile:
            myFile.write(toFileLatex.substitute(**toTemplate[driver]))
        with cd( os.path.join(os.getcwd(), outDir) ):
            cmd = ['pdflatex', '-interaction', 'nonstopmode', fileName]
            proc = subprocess.Popen(cmd, stdout=latexLogFile)
            out = proc.communicate()
            for ending in uselessFilesEndings:
                os.unlink('{}{}'.format(driver,ending))




