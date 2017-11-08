import csv
from datetime import datetime,timedelta
import sys
import os
import subprocess
import string
import locale

def processOneSingleMonth(year, month, automaticDate, settlementDate):

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
    #Gebe den Namen der Latexvorlage fuer die Gesamtauflistung ein
    fileNameLatexTemplateGesamtauflistung = './templates/template4PythonGesamtauflistung.tex'

    #Erstelle das Erstelldatum der Abrechnung automatisch
    if automaticDate:
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
        if dateStrZfilled2Numbers[0] == 'v':
            month = month - 1
            if month == 0:
                month = 12
                year = year -1
            dateStrZfilled2Numbers = dateStrZfilled2Numbers[1:].zfill(2)
        elif dateStrZfilled2Numbers[0] == 'n':
            month = month + 1
            if month  == 13:
                month = 1
                year = year +1
            dateStrZfilled2Numbers = dateStrZfilled2Numbers[1:].zfill(2)
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

    def formatGesamtauflistung(outData, toTemplateSums, uniqueDrivers):
        #Maximale Anzahl Zeilen pro Seite der Gesamtauflistung
        maxRow = 31
        #Zaehler der Anzahl der Zeilen der aktuellen Seite
        rowCount = 0
        #Trennzeichen zwischen zwei Spalten der Latextabelle
        delimiterLatexTable = '&'
        #Trennzeichen zwischen zwei Zeilen innerhalb des Tabellenbereiches eines Fahrers
        endLineLatexTable1 = r'\\\cline{2-9}'
        #Trennzeichen zwischen zwei Zeilen vor der Summenangabe eines Fahrers
        endLineLatexTable2 = r'\\\hhline{|-|-|-|-|-|=|=|=|=|}'
        #Trennzeichen am Ende einer Latextabelle
        endLineLatexTable3 = r'\\\hline'
        #Beginn einer Tabelle in Latex
        tableBegin = r'\begin{table}'+'\n'+ r'\centering'+'\n'+ r'\begin{tabular}{ | c | r | r | r | r | c | r | r | r |}\hline'+'\n'+r'Fahrer & Fahrzeug & Datum Beginn & Datum Ende & Beginn & Ende  & Dauer [h]& Distanz [km]& Kosten [\euro{}]\\ \hline'+'\n'
        #Ende eienr Tabelle in Latex
        tableEnd = r'\end{tabular}'+'\n'+ r'\end{table} '+'\n'
        #Latexbefehl um eine neue Zeile anzufangen
        newPage = r'\newpage'+'\n'
        ############ Starte
        tmpStr = tableBegin
        for driver in uniqueDrivers:
            lenData = len(outData[driver])
            durationSum = 0
            distanceSum = 0
            for index,entry in enumerate( outData[driver] ):
                tableEndedRightNow = False  #Wenn dieser Programmteil ausgefuehrt wird, war die letzte Zeile nicht die allerletzte Zeile
                durationSum = durationSum + entry['duration']
                distanceSum = distanceSum + entry['distance']
                #Schreibe den Namen des Fahrers, dessen Eintraege jetzt aufgezaehlt werden
                if index == 0:
                    tmpStr = tmpStr \
                        + driver
                #Schreibe eine Zeile
                tmpStr = tmpStr + delimiterLatexTable \
                    + entry['carName'].upper() + delimiterLatexTable \
                    + entry['begin'].strftime('%d.%m.%Y') + delimiterLatexTable \
                    + entry['end'].strftime('%d.%m.%Y') + delimiterLatexTable \
                    + entry['begin'].strftime('%H:%M') + delimiterLatexTable \
                    + entry['end'].strftime('%H:%M') + delimiterLatexTable \
                    + '{:.2f}'.format( entry['duration'] )+ delimiterLatexTable \
                    + '{:.2f}'.format( entry['distance'] )+ delimiterLatexTable \
                    + '{:.2f}'.format( entry['cost'] )
                #Beende die aktuelle Zeile als mittige Zeile
                if index != lenData-1 :
                        tmpStr = tmpStr + endLineLatexTable1 + '\n'
                        rowCount = rowCount + 1
                #Beende die aktuelle Zeile als letzte Zeile eines Fahreres und gebe Summen an
                else:
                    tmpStr = tmpStr + endLineLatexTable2 + '\n' \
                        + '\\multicolumn{5}{|c|}{}' + delimiterLatexTable \
                        + 'Summen:' + delimiterLatexTable \
                        + '{:.2f}'.format( durationSum ) + delimiterLatexTable \
                        + '{:.2f}'.format( distanceSum ) + delimiterLatexTable \
                        + '{:.2f}'.format( toTemplateSums[driver] ) + endLineLatexTable3 + '\n'
                    rowCount = rowCount + 2
                #Falls die aktuelle Tabelle laenger ist als die zulaessige Zeilenanzahl, beende die aktuelle Tabelle, beginne eine neue Seite und beginne eine neue Tabelle
                if maxRow <= rowCount:
                    tmpStr = tmpStr + tableEnd + newPage + tableBegin
                    rowCount = 0
                    tableEndedRightNow = True
        if not tableEndedRightNow:
            tmpStr = tmpStr + tableEnd
        return tmpStr

    def formatOutData(tripList, toTemplateSum):
        #Schalter für eine Fallunterscheidung "der/den nächsten Seite/n"
        multiplePagesBool = False
        #Maximale Anzahl Zeilen pro Seite der Gesamtauflistung
        maxRow = 40
        #Zaehler der Anzahl der Zeilen der aktuellen Seite
        rowCount = 0
        #Trennzeichen zwischen zwei Spalten der Latextabelle
        delimiterLatexTable = '&'
        #Trennzeichen am Ende einer Latextabelle
        endLineLatexTable = r'\\\hline'
        #Beginn einer Tabelle in Latex
        tableBegin = r'\newpage'+'\n' \
            + r'\begin{tabular}{ | c | c | r | r | r | }'+'\n' \
            + r'\hline'+'\n' \
            + r'Datum & Fahrzeug & Dauer [h] & Distanz [km]& Kosten [\euro{}]\\ \hline' + '\n'
        #Ende einer Tabelle in Latex ohne Summation
        tableEndMid = r'\end{tabular}' + '\n'
        #Ende einer Tabelle in Latex mit Summation
        tableEndFinal = r'\\\hhline{|-|-|-|=|=|}'+'\n' \
            + r'\multicolumn{4}{|r|}{\bf{Summe:}} &\bf{'+ '{:.2f}'.format(toTemplateSum) + r'}\\\hline'+ '\n' \
            + r'\end{tabular}'
        tmpStr = tableBegin
        lastIndex = len(tripList)-1
        for index,entry in enumerate(tripList):
            rowCount = rowCount + 1
            #Falls die aktuelle Tabelle laenger ist als die zulaessige Zeilenanzahl, beende die aktuelle Tabelle,
            #beginne eine neue Seite und beginne eine neue Tabelle
            if maxRow <= rowCount:
                tmpStr = tmpStr + tableEndMid + tableBegin
                rowCount = 0
                multiplePagesBool = True
            #Schreibe eine Zeile
            tmpStr = tmpStr \
                + entry['begin'].strftime('%d.%m.%Y') + delimiterLatexTable \
                + entry['carName'].upper() + delimiterLatexTable \
                + '{:.2f}'.format( entry['duration'] )+ delimiterLatexTable \
                + '{:.2f}'.format( entry['distance'] )+ delimiterLatexTable \
                + '{:.2f}'.format( entry['cost'] )
            #Beende die aktuelle Zeile als mittige Zeile
            if(index != lastIndex):
                tmpStr = tmpStr + endLineLatexTable + '\n'
            #Beende die aktuelle Zeile als letzte Zeile des Fahreres und gebe Summen an
            else:
                tmpStr = tmpStr + tableEndFinal
        return tmpStr, multiplePagesBool

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
        calcData.append({'driverName' :name, 'begin':begin, 'end':end, 'carName':carName, 'duration':duration, 'distance':distance, 'cost':cost})
    #Ordne die einzelnen Fahrteintraege den Fahrern zu

    #Sortiere calcData nach Fahrer und dann nach Startzeitpunkten
    calcData.sort(key = lambda x: (x['driverName'] , x['begin'] ) )

    #Erstelle eine Liste der im betrachteten Monat aktiven Fahrer ausgehend von den Fahrdaten
    uniqueDrivers = list(set( map(lambda x:x['driverName'], calcData) ))
    uniqueDrivers.sort()
    print('Folgende Fahrer sind im betrachteten Zeitraum aktiv:')
    for driver in uniqueDrivers:
        print('\t'+driver)

    #Ueberpruefe fuer jeden aktiven Fahrer, ob es einen passenden Eintrag im Fahrerverzeichnis gibt.
    allDriverInDriverData = True
    driverNotInDriverData = []
    for driver in uniqueDrivers:
        if not driver in driverData:
            allDriverInDriverData = False
            driverNotInDriverData.append(driver)
    if allDriverInDriverData:
        print('Alle aktiven Fahrer werden im Fahrerverzeichnis gefunden.')
    else:
        print('xxxxxxxxxxxxxxx\nFolgende Fahrer koennen nicht im Fahrerverzeichnis gefunden werden:')
        for driver in driverNotInDriverData:
            print('\t{}'.format(driver))
        print('\n\n\nDas Programm wird abgebrochen.\n\n\n')
        sys.exit()

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

    ######################################
    #Bereite Latex vor

    #Erstelle das Ausgabeverzeichnis
    outDir = os.path.join( os.getcwd(), outputDirectory )
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    #Erstelle eine Liste von endungen unnoetiger Dateien
    uselessFilesEndings = ['.tex','.aux','.log']

    ######################################
    #Erstelle eine Auflistung aller Fahrten
    #Erstelle ein Dictinonary von Dictionaries um Platzhalter in der Vorlage zu ersetzen
    toTemplate = {'table': formatGesamtauflistung(outData, toTemplateSums, uniqueDrivers)}

    #Lese die Vorlage in eine Variable
    with open(fileNameLatexTemplateGesamtauflistung,'r', newline='') as myFile:
        templateStr = myFile.read()

    #Erstelle ein Python String Template Objekt mit gewuenschtem Trennzeichen
    class latexTemplate(string.Template):
        delimiter = "##"
    toFileLatex = latexTemplate(templateStr)

    print('Erstelle PDF Gesamtauflistung')
    #Erstelle die Ausgabedateien (pdf)
    fileNameSummary = 'Gesamtauflistung'
    #Oeffne eine Logdatei fuer die Ausgabe der Latexbefehle
    with open(os.path.join( os.getcwd(),fileNameLatexLog), 'w') as latexLogFile:
        fileName = os.path.join(os.getcwd(), outDir ,'{}_{}_{}.tex'.format( str(year), str(month).zfill(2), fileNameSummary ) )
        with open( fileName , 'w' ,newline = '\n') as myFile:
            myFile.write(toFileLatex.substitute(**toTemplate))
        with cd( os.path.join(os.getcwd(), outDir) ):
            cmd = ['pdflatex', '-interaction', 'nonstopmode', fileName]
            for i in range(2):  #Um die Gesamtanzahl der Seiten in Latex fuer den Befehl \pageref{LastPage} verfuegbar zu machen, muss Latex zweimal aufgerufen werden.
                proc = subprocess.Popen(cmd, stdout=latexLogFile)
                out = proc.communicate()
            for ending in uselessFilesEndings:
                os.unlink(os.path.splitext(fileName)[0] + ending)

    ######################################
    #Erstelle die Abrechnungen der einzelnen Fahrer
    #Erstelle ein Dictinonary von Dictionaries um Platzhalter in der Vorlage zu ersetzen
    toTemplate = {}
    for driver in uniqueDrivers:
        tmp = {}
        tmp['settlementDate'] = settlementDate
        tmp['month']    =   (gerMonthNames(month))
        tmp['year']     =   str(year)
        #tmp['sum']      =   '{:.2f}'.format(toTemplateSums[driver])
        tmp['firstName']=   driverData[driver]['firstName']
        tmp['lastName'] =   driverData[driver]['lastName']
        tmp['street'] =   driverData[driver]['street']
        tmp['streetNumber'] =   driverData[driver]['streetNumber']
        tmp['postcode'] =   driverData[driver]['postcode']
        tmp['city'] =   driverData[driver]['city']
        tmp['table'],tmp['multiplePagesBool']  = formatOutData( outData[driver] , toTemplateSums[driver])
        #Fallunterscheidung "der/den nächsten Seite/n"
        if tmp['multiplePagesBool'] :
            tmp['pages'] = 'den n\"achsten Seiten'
        else:
            tmp['pages'] = 'der n\"achsten Seite'
        #table data has to be added.
        toTemplate[driver] = tmp

    #Lese die Vorlage template4Python in eine Variable
    with open(fileNameLatexTemplate,'r', newline='') as myFile:
        templateStr = myFile.read()

    #Erstelle ein Python String Template Objekt mti gewuenschtem Trennzeichen
    class latexTemplate(string.Template):
        delimiter = "##"
    toFileLatex = latexTemplate(templateStr)

    print('Erstelle PDF fuer Fahrer:')
    #Erstelle die Ausgabedateien (pdf)
    #Oeffne eine Logdatei fuer die Ausgabe der Latexbefehle
    with open(os.path.join( os.getcwd(),fileNameLatexLog), 'a') as latexLogFile:
        for driver in uniqueDrivers:
            print('\t'+driver)
            fileName = os.path.join(os.getcwd(), outDir ,'{}_{}_{}.tex'.format( str(year), str(month).zfill(2), driver ) )
            with open( fileName , 'w' ,newline = '\n') as myFile:
                myFile.write(toFileLatex.substitute(**toTemplate[driver]))
            with cd( os.path.join(os.getcwd(), outDir) ):
                cmd = ['pdflatex', '-interaction', 'nonstopmode', fileName]
                for i in range(2):  #Um die Gesamtanzahl der Seiten in Latex fuer den Befehl \pageref{LastPage} verfuegbar zu machen, muss Latex zweimal aufgerufen werden.
                    proc = subprocess.Popen(cmd, stdout=latexLogFile)
                    out = proc.communicate()
                for ending in uselessFilesEndings:
                    os.unlink(os.path.splitext(fileName)[0] + ending)

