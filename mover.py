import re
import os
import shutil
from time import sleep
import series_finder

class FileManager():
    def __init__(self, folder, dest):
         self.folder = folder
         self.dest = dest
         self.names = []
         self.walkFiles(folder)
    
    def walkFiles(self, folder):
        os.chdir(folder)
        curentDir = os.getcwd()
        for root, dirs, files in os.walk(curentDir):
            if not files:
                continue
            for file in files:
                currentFile = os.path.join(root, file)
                self.Rename(currentFile, root)
                # self.RenameBySeriesList(currentFile, root)

    def RenameBySeriesList(self, file, root):
        series = [
            '01 серия The Remote | пульт',
            '02 серия The Colossus',
            '03 серия The Knights',
            '04 серия The Fridge',
            '05 серия The Flower',
            '06 серия The Banana',
            '07 серия The Phone',
            '08 серия The Job',
            '09 серия Halloween',
            '10 серия The Treasure',
            '11 серия The Apology',
            '12 серия The Words',
            '13 серия The Skull',
            '14 серия The Bet',
            '15 серия Christmas',
            '16 серия The Watch',
            '17 серия The Bumpkin',
            '18 серия The Flakers',
            '19 серия The Authority',
            '20 серия The Virus',
            '21 серия The Pony',
            '22 серия The Hero',
            '23 серия The Dream',
            '24 серия The Sidekick',
            '25 серия The Photo',
            '26 серия The Tag',
            '27 серия The Storm',
            '28 серия The Lesson',
            '29 серия The Game',
            '30 серия The Limit',
            '31 серия The Voice',
            '32 серия The Promise',
            '33 серия The Castle',
            '34 серия The Boombox',
            '35 серия The Tape',
            '36 серия The Sweaters',
            '37 серия The Internet',
            '38 серия The Plan',
            '39 серия The World',
            '40 серия The Finale',
        ]
        for serie in series:
            matches = re.search(r'(\d+)\s+серия\s+(.+)', serie, re.IGNORECASE)
            if not matches:
                continue
            serieName = matches[2].lower()
            serieName = serieName.replace(' ', '')

            currentNameFile = os.path.basename(file)
            currentNameFile = currentNameFile.lower()
            if currentNameFile.find(serieName) != -1:
                newName = re.sub(r'S02E(\d+)', 'S02E' + matches[1], file)
                print('Renamed:', file, 'to', newName)
                shutil.move(file, newName)
                break

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
            

    def moveFile(self, file, dest):
        shutil.move(file, dest)
        print('Moved:', file)