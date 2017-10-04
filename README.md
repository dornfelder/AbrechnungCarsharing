# AbrechnungCarsharing
## How to use AbrechnungCarsharing:

### Linux:  
  - Install Latex  
    - sudo apt-get install texlive texlive-lang-german texlive-doc-de texlive-latex-extra   
  - Install Python3  
    - sudo apt-get install python3   
  - Clone this directory  
  - Navigate to the cloned directory  
  - Make changes using a texteditor:  
     - Create new input in directory "input"  
       - For each car, create a file with similar formatting as aurCs108.txt 
     - Expand fahrerverzeichnis to cover all drivernames existing in input-data
     - Choose which is to be processed by manipulating the input section of startAbrechnung.py
     - Adjust the template template4Python.tex
       - Name of Car Sharing Verein ...
  - Execute the script in interactive mode OR without interactive mode
    - python3 -i startAbrechnung.py
      OR
    - python3 startAbrechnung.py
    
### Windows:
   - Install Latex
     - Download and install Miktex 2.9.6361 or newer and allow automatic installation of additional packages
   - Install Python3
     - Install miniconda 3.
     - Install iPython-Terminal
       - Start anaconda-command-line and type
         - conda install ipython
   - Install Notepad++ if no appropriate texteditor with syntaxhighlighting is available
   - Clone this directory
   - Start iPython and navigate to the cloned directory using "ls" and "cd" in combination with "tab"-completeion [press "tabulator"]
   - Make changes using a texteditor
     - Create new input in directory "input"
       - For each car, create file with similar formatting as aurCs108.txt  
     - Expand fahrerverzeichnis to cover all drivernames existing in input-data
     - Choose which month is to be processed by manipulating the input section of startAbrechnung.py
     - Adjust the template template4Python.tex
       - Name of Car Sharing Verein ...
   - Execute the script from iPython terminal by typing
     - %run startAbrechnung.py
