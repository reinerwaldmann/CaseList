__author__ = 'vasilev_is'
#собирает все файлы mp3 определённого исполнителя и складывает в нужную папочку


foldename_music='D:\music'

artist_name='Cascada'

foldername_dest = foldename_music+'\\'+artist_name


from os import makedirs, listdir
from os.path import isfile, join, isdir

import mutagen
from mutagen.id3 import ID3
import shutil


onlyfiles = [ f for f in listdir(foldename_music) if isfile(join(foldename_music,f)) ]
#print (onlyfiles)






def for_folder (foldername, artist):
    #allstuff = [f for f in listdir(foldername) ]
    for f in listdir(foldername):
        if isfile(join(foldername,f)):
            nice_func_for_file(join(foldername,f), artist)
        if isdir(join(foldername,f)):
            for_folder(join(foldername,f), artist)



def nice_func_for_file (fpath, artist):
    global foldername_dest

    try:
        art = ID3(fpath)['TPE1']


        if artist in art:
            print (fpath)
            name = ID3(fpath)['TIT2'] if ID3(fpath)['TIT2'] else ID3(fpath)['TIT1']


            good_name = '{0}-{1}.mp3'.format(artist,name)
            print (good_name)

            shutil.move(fpath, join(foldername_dest,good_name))



    except mutagen.id3._util.ID3NoHeaderError:
        #print ('no tag')
        pass
    except KeyError:
        #print ('no author')
        pass
    except:
        pass

for_folder(foldename_music, artist_name)

exit(0)

authors_list=[]


def for_folder_generic (foldername, func, *args):
    #allstuff = [f for f in listdir(foldername) ]
    for f in listdir(foldername):
        if isfile(join(foldername,f)):
            func(join(foldername,f), args)
        if isdir(join(foldername,f)):
            for_folder(join(foldername,f), func, *args)

def extract_authors_func (fpath, *args):
    global  authors_list
    try:
        art = str(ID3(fpath)['TPE1'])
        authors_list.append(art)
    except:
        pass


futura_music = 'D:\\futura_music'



for_folder_generic(foldename_music, extract_authors_func)
print (sorted(set(authors_list)))

for iii in sorted(set(authors_list)):
    makedirs(join(futura_music, iii))





#  в будущем - всю коллекцию разложить по папочкам с названиями исполнителей
#  мало того - названия файлов привести к единому стандарту - имя исполнителя - название песни

