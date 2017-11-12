#-*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'source'))
import core
from PyQt4 import QtCore, QtGui


inputDirectory = os.path.join( os.getcwd(), 'input' )
inputDirectories = [name for name in os.listdir(inputDirectory) if os.path.isdir(os.path.join(inputDirectory, name))]
inputDirectories.sort()



app = QtGui.QApplication(sys.argv)

class myApp(QtGui.QLabel):
    def __init__(self):
        #Set up widget for main window
        QtGui.QLabel.__init__(self)
        self.setMinimumSize( QtCore.QSize(400,400) )
        self.setWindowTitle('Carsharing')
        #Define layout of main window
        self.layout = QtGui.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.layout)
        #Set up listWidget to hold checkboxes and labels of input directories
        self.listW = QtGui.QListWidget()
        self.layout.addWidget(self.listW)
        #Populate listWidget
        for directory in inputDirectories:
            item = QtGui.QListWidgetItem(directory, self.listW)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.listW.addItem(item)
        #Set up Button to start processing
        self.button = QtGui.QPushButton('Erstelle Abrechnungen für die ausgewählten Monate')
        self.button.clicked.connect(self.runAbrechnungen)
        self.layout.addWidget(self.button)

    def getChecklist(self):
        '''Check all checkboxes and remember status'''
        checklist = []
        assert self.listW.count() == len(inputDirectories)
        for index in range(self.listW.count()):
            box = self.listW.item( index )
            checklist.append({'text':box.text(), 'QtCoreQtCheckedstatus': box.checkState()})
        return checklist

    def parseDirectoryName(self, directoryName):
        '''Parse directory name to year and month'''
        if ( (len(directoryName) == 7) and (all([myStr.isdigit() for index, myStr in enumerate(directoryName) if index !=4 ]))):
            year = int(directoryName[0:4])
            month = int(directoryName[5:])
        else:
            raise ValueError("Der Name eines Verzeichnisses im Ordner 'input' hat nicht das geforderte Format. Beispielformat fuer Januar 2017: '2017_01' ")
        return year, month

    def runAbrechnungen(self):
        '''Create settlement for each input directory which checkbox has been checked'''
        self.checklist= self.getChecklist()
        for checklistEntry in self.checklist:
            if checklistEntry['QtCoreQtCheckedstatus'] == QtCore.Qt.Checked:
                year, month = self.parseDirectoryName(checklistEntry['text'])
                core.processOneSingleMonth(year, month, automaticDate=True, settlementDate='emptySettlementDate')

    def run(self):
        self.show()
        app.exec_()

myApp().run()


