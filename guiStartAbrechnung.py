#-*- coding: utf-8 -*-

import os
inputDirectory = os.path.join( os.getcwd(), 'input' )
inputDirectories = [name for name in os.listdir(inputDirectory) if os.path.isdir(os.path.join(inputDirectory, name))]




#import sys
#from PyQt4 import QtGui


#def main():
#    
#    app = QtGui.QApplication(sys.argv)

#    w = QtGui.QWidget()
#    w.resize(250, 150)
#    w.move(300, 300)
#    w.setWindowTitle('Simple')
#    w.show()
#    
#    sys.exit(app.exec_())


#if __name__ == '__main__':
#    main()




##import sys
##from PyQt4 import QtGui


##class Example(QtGui.QWidget):
##    
##    def __init__(self):
##        super(Example, self).__init__()
##        
##        self.initUI()
##        
##    def initUI(self):               
##        
##        self.resize(250, 150)
##        #self.center()
##        
##        self.setWindowTitle('Center')    
##        self.show()
##        
##    def center(self):
##        
##        qr = self.frameGeometry()
##        cp = QtGui.QDesktopWidget().availableGeometry().center()
##        qr.moveCenter(cp)
##        self.move(qr.topLeft())
##        
##        
##def main():
##    
##    app = QtGui.QApplication(sys.argv)
##    ex = Example()
##    sys.exit(app.exec_())


##if __name__ == '__main__':
##    main()    





#import sys
#from PyQt4 import QtGui
#import os


#class Example(QtGui.QMainWindow):
#    
#    def __init__(self):
#        super(Example, self).__init__()
#        
#        self.initUI()
#        
#        
#    def initUI(self):               
#        
#        textEdit = QtGui.QTextEdit()
#        self.setCentralWidget(textEdit)

#        exitAction = QtGui.QAction(QtGui.QIcon(os.path.join('source', 'pics','exit.png')), 'Exit', self)
#        exitAction.setShortcut('Ctrl+Q')
#        exitAction.setStatusTip('Exit application')
#        exitAction.triggered.connect(self.close)

#        self.statusBar()

#        menubar = self.menuBar()
#        fileMenu = menubar.addMenu('&File')
#        fileMenu.addAction(exitAction)

#        toolbar = self.addToolBar('Exit')
#        toolbar.addAction(exitAction)
#        
#        self.setGeometry(300, 300, 350, 250)
#        self.setWindowTitle('Main window')    
#        self.show()
#        
#        
#def main():
#    
#    app = QtGui.QApplication(sys.argv)
#    ex = Example()
#    sys.exit(app.exec_())


#if __name__ == '__main__':
#    main() 
