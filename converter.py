import os
import re
import sys
import ffmpeg # https://github.com/kkroening/ffmpeg-python (pip install ffmpeg-python)
from pprint import pprint
from time import sleep

class Converter:
    def __init__(self):
        self.ffmpeg = 'C:/ffmpeg/bin/ffmpeg.exe'
        self.folder = ''
        self.outFolder = ''
        self.bitrateVideo = '5000k'
        self.bitrateAudio = '192k'
        self.convert = False
        self.skipVideo = False
        self.queries = []

        arguments = self.getArgumetsList()
        if not arguments:
            exit('did not find arguments')
        
        if 'folder' in arguments:
            self.folder = arguments['folder']
         
        if 'out_folder' in arguments:
            self.outFolder = arguments['out_folder']

        if 'convert' in arguments:
            self.convert = bool(arguments['convert'])
        
        if 'skip_video' in arguments:
            self.skipVideo = bool(arguments['skip_video'])

        if not self.folder:
            exit('did not find folder')
        if not self.outFolder:
            exit('did not find out_folder')

        self.run()

    def getArgumetsList(self):
        commands = ['folder', 'out_folder', 'convert', 'skip_video', 'skip_audio', 'skip_subtitles']
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

    def run(self):
        files = self.prepare_video()
        if not files:
            print('Не найдены файлы для конвертации')
            return

        queries = self.prepare_query(files)
        if not queries:
            print('Не удалось создать запросы для ffmpeg')
            return
        self.convert_video(queries)

    def prepare_video(self):
        videoFiles = {}
        counter = 0
        for root, dirs, files in os.walk(self.folder):
            if not files:
                continue

            for file in files:
                if not file.lower().endswith(('.mp4', 'mkv', 'avi', 'flv', 'mov', 'wmv', 'mpg', 'mpeg', 'm4v', '3gp', '3g2', 'm2ts', 'mts', 'ts', 'webm')):
                    continue

                filepath = os.path.join(root, file)
                info = self.get_video_info(filepath)
                
                if info is None:
                    print(str(counter) + 'Не удалось получить данные из ' + filepath)
                    continue

                videoFiles[counter] = {}
                videoFiles[counter]['path'] = filepath
                videoFiles[counter]['info'] = info
                counter += 1
        return videoFiles

    def get_video_info(self, file):
        videoInfo = {}
        data = ffmpeg.probe(file)
        if not data['streams']:
            return None

        flag = False
        itemNum = 0
        videoInfo['audioTracks'] = {}
        videoInfo['subtitles'] = {}
        for item in data['streams']:
            if item['codec_type'] == 'video':
                videoInfo['mapVideo'] = itemNum
                videoInfo['width'] = item['coded_width']
                videoInfo['height'] = item['coded_height']
                videoInfo['codecVideo'] = item['codec_name']

                # todo - find other bitrate options 
                if self.has_key(['tags', 'BPS-eng'], item):
                    videoInfo['bitrateVideo'] = item['tags']['BPS-eng']
                flag = True

            if item['codec_type'] == 'audio':
                videoInfo['audioTracks'][itemNum] = {}
                videoInfo['audioTracks'][itemNum]['mapAudio'] = itemNum
                videoInfo['audioTracks'][itemNum]['codecAudio'] = item['codec_name']

                if 'codec_time_base' in item:
                    videoInfo['audioTracks'][itemNum]['frequency '] = re.sub(r'1\/', r"", item['codec_time_base'])

                if self.has_key(['tags', 'BPS-eng'], item):
                    videoInfo['audioTracks'][itemNum]['bitrate'] = item['tags']['BPS-eng']
                if self.has_key(['tags', 'BPS'], item):
                    videoInfo['audioTracks'][itemNum]['bitrate'] = item['tags']['BPS']
                if 'bit_rate' in item:
                    videoInfo['audioTracks'][itemNum]['bitrate'] = item['bit_rate']

                if self.has_key(['tags', 'language'], item):
                    videoInfo['audioTracks'][itemNum]['language'] = item['tags']['language']

                if self.has_key(['tags', 'title'], item):
                    videoInfo['audioTracks'][itemNum]['language'] = item['tags']['title']

            if item['codec_type'] == 'subtitle':
                videoInfo['subtitles'][itemNum] = {}
                videoInfo['subtitles'][itemNum]['mapSubtitle'] = itemNum
                videoInfo['subtitles'][itemNum]['codecSubtitle'] = item['codec_name']
                if self.has_key(['tags', 'language'], item):
                    videoInfo['subtitles'][itemNum]['language'] = item['tags']['language']
                if self.has_key(['tags', 'title'], item):
                    videoInfo['subtitles'][itemNum]['language'] = item['tags']['title']

            itemNum += 1

        if not videoInfo['audioTracks']: # todo - doesn't need for mute video
            print('Не найдены аудиодорожки в ' + file)
            return {}
        if flag == False:
            return {}
        return videoInfo

    def prepare_query(self, files) -> dict:
        queries = []
        mainFields = ['path', 'info']
        if not files:
            return {}
        
        for file in files.values():
            flag = True
            for field in mainFields:
                if field not in file:
                    flag = False
            if not flag:
                continue

            path = '"' + file['path'] + '"'
            startQuery = self.ffmpeg + ' -y -i ' + path
            
            name, ext = os.path.splitext(path)
            name = self.prepareName(name)# todo - don't forget to change extens
            outName = os.path.join(os.path.dirname(self.outFolder), os.path.basename(name))

            if self.skipVideo == False:
                self.prepare_video_query(file, name, outName, startQuery)

            query = self.prepare_query_get_audio(file, name)

            query = self.prepare_query_get_subtitles(file, name)
            if not query:
                continue
            queries.append(query)
        
        return queries

    def prepareName(self, name):
        name = name.replace(' ', '')
        name = name.replace('\"\'', '')
        return name

    def prepare_video_query(self, file, name, outName, startQuery) -> str:
        if self.has_key(['info', 'bitrateVideo'], file):
            self.bitrateVideo = str(file['info']['bitrateVideo'])

        queryPass = self.setQueryPass1(file, startQuery)
        
        audio = self.getAudio(file)
        if not audio:
            print('Не удалось получить аудио дорожку для ' + name)
            return
        
        self.queries.append(queryPass)

        outName = outName + '.mp4'
        query = ''
        query = startQuery + ' -map 0:0'
        query = query + ' -map 0:' + audio['map'] + ' -c:v:0 libx264 -b:v ' + self.bitrateVideo + ' -pass 2 -c:a:' + audio['map'] + ' aac -b:a ' + audio['bitrate'] + ' -movflags +faststart ' + outName
        self.queries.append(query)
        # ffmpeg -y -i "C:\\phytonProjects\\phytonEducation\\useful\\video\\su.s05e01e02.mkv" -c:v libx264 -b:v 5948k -pass 1 -an -f mp4  NULL
        # ffmpeg -y -i "C:\\phytonProjects\\phytonEducation\\useful\\video\\su.s05e01e02.mkv" -map 0:0 -map 0:1 -c:v:0 libx264 -b:v 5948k -pass 2 -c:a:1 aac -b:a 192k -movflags +faststart output.mp4


    def setQueryPass1(self, startQuery) -> str:
        # codec = file['info']['codecVideo']
        # todo - maybe we can add other codecs
        codec = 'libx264'
        query = startQuery + ' -c:v ' + codec + ' -b:v ' + self.bitrateVideo + ' -pass 1 -an -f mp4 ' + self.outFolder + ' NULL' # NULL

        return query

    def getAudio(self, file, lang = 'rus') -> dict:
        audio = {}
        for audioTrack in file['info']['audioTracks'].values():
            language = ''
            if 'language' in audioTrack:
                language = audioTrack['language']

            mapAudio = audioTrack['mapAudio']
            if 'bitrate' in audioTrack:
                audio['bitrate'] = str(audioTrack['bitrate'])
            else:
                audio['bitrate'] = self.bitrateAudio
            audio['map'] = str(mapAudio)

            if language == lang:
                break

        sleep(100)
        return audio


    def prepare_query_get_audio(self, file, name, outName, startQuery) -> str:
            query = ''

            audio = self.getAudio(file, 'eng')
            if audio:
                name = outName + 'xENG.aac'
                query = startQuery + ' -map 0:' + audio['map'] + ' -c:a copy ' + name
                self.queries.append(query)

            audio = self.getAudio(file, 'rus')
            if audio:
                name = outName + 'xRUS.aac'
                query = startQuery + ' -map 0:' + audio['map'] + ' -c:a copy ' + name
                self.queries.append(query)

            # todo - add good query
            # query = self.ffmpeg + ' -map 0:' + audio['map'] + ' -i ' + path + ' -vn -ar ' + audio['frequency'] + ' -c:a:' + audio['map'] + '  aac -b:a ' + audio['bitrate'] + ' -f aac ' + outName
            return query


    def convert_video(self, queries):
        for query in queries:
            try:
                print(query)
                print('')
                if self.convert == False:
                    continue
                os.system(query)
            except:
                print("Упс! Не удается конвертировать файл: " + query)

    def has_key(self, keys, dict):
        answer = False
        if keys[0] in dict:
            if not keys[1:]:
                return True
            answer = self.has_key(keys[1:], dict[keys[0]])
        return answer


    def prepare_query_get_subtitles(self, file, name) -> str:
        query = ''

        path = '"' + file['path'] + '"'
        query = self.ffmpeg + ' -y -i ' + path

        newName = name + '.srt'
        outName = os.path.join(os.path.dirname(self.outFolder), os.path.basename(newName))

        map = ''
        for subtitleTrack in file['info']['subtitles'].values():
            if 'language' not in subtitleTrack:
                continue

            language = subtitleTrack['language'].lower()
            if language.find('eng') == -1: #todo add other languages
                continue
            mapSubtitle = subtitleTrack['mapSubtitle']
            map = str(mapSubtitle)

        if not map:
            return ''

        query = self.ffmpeg + ' -i ' + path + ' -map 0:' + map + ' -c:s:' + map + ' srt ' + outName
            
        return query
# folder = 'D:\\cartoon\\gumball\\5season\\input\\'
# outFolder = 'D:\\cartoon\\gumball\\5season\\output\\'
Converter = Converter()

if __name__ == '__main__':
    pass

'''
        двухполосный видео в mp4 : убрал ( -vtag xvid ) - возможно не будет работать на тв 
        Вроде лучший вариант для использования:
        ffmpeg -y -i "C:\\phytonProjects\\phytonEducation\\useful\\su.s05e01e02.mkv" -c:v libx264 -b:v 5948k -pass 1 -an -f mp4  NULL 

        ffmpeg -y -i "C:\\phytonProjects\\phytonEducation\\useful\\su.s05e01e02.mkv" -c:v libx264 -b:v 5948k -pass 2 -c:a aac -b:a 192k -movflags +faststart output.mp4


        без потери качества todo: проверить AAC для аудио и x264 для видео 
        подойдет для скорости
        ffmpeg -i "C:\\phytonProjects\\phytonEducation\\useful\\su.s05e01e02.mkv" -vcodec copy -acodec copy -movflags +faststart output.mp4

        Копия видео + конвертация аудио в web поддержку: проверить AAC and h264
        ffmpeg -i "C:\\phytonProjects\\phytonEducation\\useful\\video\\su.s05e01e02.mkv" -vcodec copy -acodec aac -movflags +faststart output.mp4

        Использование разных дорожек:
        ffmpeg -i "C:\\phytonProjects\\phytonEducation\\useful\\video\\su.s05e01e02.mkv" -map 0:0 -map 0:1 -c:v:0 copy -c:a:1 aac -b:a 320k -movflags +faststart output.mp4
        ffmpeg -i "C:\\phytonProjects\\phytonEducation\\useful\\video\\su.s05e01e02.mkv" -map 0:0 -map 0:1 -map 0:2 -c:v:0 copy -c:a:1 aac -b:a 320k -c:a:2 aac -b:a 92k -movflags +faststart output.mp4

        ffmpeg -y -i "C:\\phytonProjects\\phytonEducation\\useful\\video\\su.s05e01e02.mkv" -c:v libx264 -b:v 5948k -pass 1 -an -f mp4  NULL 
        ffmpeg -y -i "C:\\phytonProjects\\phytonEducation\\useful\\video\\su.s05e01e02.mkv" -map 0:0 -map 0:1 -c:v:0 libx264 -b:v 5948k -pass 2 -c:a:1 aac -b:a 192k -movflags +faststart output.mp4
'''
