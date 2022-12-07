import re
import os
import shutil
from pprint import pprint
from time import sleep
import seriesFinder
import argparse
import sys

class FileManager():
    def __init__(self):
         self.names = []
         self.folder = ''
         self.dest = ''
         self.url = ''

         arguments = self.getArgumets()
         if not arguments:
            exit('did not find arguments')
         print(arguments)

    def getArgumets(self):
        commands = ['folder', 'dest', 'url'] #сделать уникальным список todo
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
        
        pprint(arguments)
        if len(arguments) != len(commands):
            return {}
        return arguments

    def renameFilesBySeries(self):
        files = self.getFiles(self.folder)
        seriesList = seriesFinder.getSeriesList('https://cartoonsub.com/serials/amazingworldofgumball/S03')
        if not seriesList:
            print('Error: seriesList is empty')
            return
        
        for file in files:
            currentNameFile = os.path.basename(file)
            currentNameFile = currentNameFile.lower()
            
            for serie in seriesList:
                nameSerie = serie['name'].lower().replace(' ', '')
                if currentNameFile.find(nameSerie) == -1:
                    continue

                numberSerie = str(serie['number']).zfill(2)
                newName = re.sub(r'S03E(\d+)', 'S02E' + numberSerie, file)
                print('Renamed:', file, 'to', newName)
                # shutil.move(file, newName)
                break


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


    def Rename(self, file, root):
        matches = re.search(r'x(\d{1,2})-(\d{1,2}).+?\[(\w+)].+?(\.\w+)$', file, re.IGNORECASE)
        matches = re.search(r'S02E(\d+)-(\d+)\[(\w+)\].+?(\.\w+)$', file, re.IGNORECASE)
        matches = re.search(r'(\d)x(\d+)-(\d+)TheAmazingWorldofGumball\[(\w+)\].+?(\.\w+)$', file, re.IGNORECASE)
        if not matches:
            return

        type = 'DUB'
        if matches[5] == '.aac':
            type = 'ORIGINAL'
        newName = 'S0' + matches[1] + 'E' + matches[2] + 'DUBx1080x' + matches[4] + matches[5]
        if matches[2] in self.names:
            newName = 'S0' + matches[1] + 'E' + matches[3] + type + 'x1080x' + matches[4] + matches[5]
        newFile = os.path.join(root, newName)
        self.names.append(matches[2])
        print('Renamed:', file, 'to', newFile)
        shutil.move(file, newFile)

if __name__ == '__main__':
    folder = r'D:\cartoon\gumball\3season'
    dest = r'D:\cartoon\gumball\3season'
    Fm = FileManager()
    # Fm.renameFilesBySeries()
