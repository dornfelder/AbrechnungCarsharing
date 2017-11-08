import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'source'))
import core

############################
#Beginn Nutzereingabe

#Workflow:
#1. Erstelle im Verzeichnis 'input' ein Unterverzeichnis nach dem Beispielformat "2017_06".
#2. In diesem Unterverzeichnis erstelle fuer jedes Fahrzeug eine Datei im Format "aurCs108.txt"
#   mit Dateiendung ".txt" und einem Namen, der in der Abrechnugnsauflistugn als Fahrzeugkuerzel
#   verwendet werden kann.
#   Tage des Monats vor dem Abrechnungsmonat können mit fuehrendem Zeichen 'v' eingegeben werden. Bspl.: 'v31'
#   Tage des Monats nach dem Abrechnungsmonat können mit fuehrendem Zeichen 'n' eingegeben werden. Bspl.: 'n01' oder 'n1'
#3. Aktualisiere gegebenfalls das Fahrerverzeichnis "fahrerverzeichnis.txt"
#4. Gib im nachfolgenden Bereich der Nutzereingabe das Jahr und den Monat der zu bearbeitenden Daten ein.
#5- Gib im nachfolgenden Bereich der Nutzereingabe bei Bedarf das Erstelldatum der Abrechnung ein.
#6  Fuehre dieses Skript aus.

#Gebe das Jahr des zu bearbeitenden Monats ein
year = 2000
#Gebe den zu bearbeitenden Monat ein
month = 1
#Soll das Erstelldatum der Abrechnung automatisch erstellt werden?
automaticDate = True #True oder False

#Gebe das Erstelldatum der Abrechnung manuell ein. (Diese Eingabe wird nur genutzt, falls atomaticDate = False)
settlementDate = '18. August 2017'

#Ende Nutzereingabe
############################
############################
#Start Ausfuehrung

#Bearbeite den ausgwaehlten Monat
core.processOneSingleMonth(year, month, automaticDate, settlementDate)

#Warte auf Nutzereingabe um Kommandofenster zu schliessen
input("\nDruecke ENTER um dieses Fenster zu schliessen.")

#Ende Ausfuehrung
############################



