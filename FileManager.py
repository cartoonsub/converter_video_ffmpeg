import re
import os
import sys
import shutil
import seriesFinder
from time import sleep
from pprint import pprint

class FileManager():
    def __init__(self):
         self.names = []
         self.folder = ''
         self.dest = ''
         self.url = ''
         self.test = False
         self.setArguments()

    # todo пересмотреть создание переменных из списка ?
    def setArguments(self):
        arguments = self.getArgumetsList()
        if not arguments:
            exit('did not find arguments')

        if 'test' in arguments:
            self.test = bool(arguments['test'])

        if 'folder' in arguments:
            self.folder = arguments['folder']
            self.RenameFiles()
         
        if 'dest' in arguments:
            self.dest = arguments['dest']

        if 'url' in arguments:
            self.url = arguments['url']
            self.renameFilesBySeries()

    def getArgumetsList(self):
        commands = set(['folder', 'dest', 'url', 'test'])
        arguments = {}
        args = sys.argv
        if not args:
            return

        for i in range(len(args)):
            if i == 0:
                continue
            item = args[i].split('=')
            if len(item) < 2:
                continue
            if item[0] not in commands:
                continue
            
            arguments[item[0]] = item[1]
        
        return arguments


    def renameFilesBySeries(self):
        if not self.folder:
            return
        
        files = self.getFiles(self.folder)
        seriesList = seriesFinder.getSeriesList(self.url)
        if not seriesList:
            print('Error: seriesList is empty')
            return
        
        pprint(seriesList)

        for file in files:
            currentNameFile = os.path.basename(file)
            currentNameFile = currentNameFile.lower()
            numberSerie = self.getNumberSerie(seriesList, currentNameFile)
            if not numberSerie:
                print('не найден номер серии для файла:', file)
                continue

            newName = re.sub(r'S(\d{1,2})E(\d+)', r'S\1E' + numberSerie, file)
            print('Renamed:', file, 'to', newName)
            if self.test == False:
                shutil.move(file, newName)


    def getNumberSerie(self, seriesList, currentNameFile):
        # todo rewrite, if there will be more variants of names
        numberSerie = ''
        for serie in seriesList:
            number = str(serie['number']).zfill(2)
            name = serie['name'].lower().replace(' ', '')
            if currentNameFile.find(name) != -1:
                numberSerie = number
                break

            name = serie['secondName'].lower().replace(' ', '')
            if currentNameFile.find(name) != -1:
                numberSerie = number
                break

            name = serie['fullName'].lower().replace(' ', '')
            if currentNameFile.find(name) != -1:
                numberSerie = number
                break

        return numberSerie

    def getFiles(self, folder) -> list:
        filesList = []
        os.chdir(folder)
        curentDir = os.getcwd()
        for root, dirs, files in os.walk(curentDir):
            if not files:
                continue
            for file in files:
                currentFile = os.path.join(root, file)
                filesList.append(currentFile)
        return filesList

    def RenameFiles(self):
        files = self.getFiles(self.folder)
        for file in files:
            self.Rename(file)

    def Rename(self, file):
        matches = re.search(r'(?P<season>\d)[x-]+(?P<serie>\d+)[-\s]*TheAmazingWorldofGumball[+\s]*\[(?P<name>[\w.]+)\].+?(?P<end>\.\w+)$', file, re.IGNORECASE)
        matches = re.search(r'S(?P<season>\d{1,2})E(?P<serie>\d{1,2})\s*(?P<name>[\w.\s]+).*?(?P<end>\.\w{3})$', file, re.IGNORECASE)
        if not matches:
            print('Not found:', file, end='\n\r \n\r')
            return

        type = 'DUB'
        type = 'SUB'
        if matches['end'] == '.aac':
            type = 'ORIGINAL'

        name = matches['name']
        name = name.replace(' ', '')
        name = name.replace('.', '')

        newName = 'S0' + matches['season'] + 'E' + matches['serie'] + type + 'x1080x' + name + matches['end']
        if matches[2] in self.names:
            newName = 'S0' + matches['season'] + 'E' + matches['serie'] + type + 'x1080x' + name + matches['end']
        newFile = os.path.join(self.folder, newName)
        self.names.append(matches['serie'])
        print('Renamed:', file, 'to', newFile, end='\n\r \n\r')
        if self.test == True:
            return

        shutil.move(file, newFile)


if __name__ == '__main__':
    # folder = r'D:\cartoon\gumball\3season'
    # dest = r'D:\cartoon\gumball\3season'
    Fm = FileManager()
