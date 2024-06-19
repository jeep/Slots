from os import listdir
from os.path import isfile, join, getctime
from PIL import Image, ExifTags
from datetime import datetime

from threading import Thread

def get_time(path):
    with Image.open(path) as image:
        try:
            image_exif = image.getexif()
            exif = { ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes }
            date_obj = datetime.strptime(exif['DateTimeOriginal'], r'%Y:%m:%d %H:%M:%S').strftime(r'%Y%m%d%H%M%S')
            return date_obj
        except (KeyError, AttributeError):
            pass
        try:
            image_exif = image.getexif()
            date_obj = datetime.strptime(image_exif[306], r'%Y:%m:%d %H:%M:%S').strftime(r'%Y%m%d%H%M%S')
            return date_obj
        except (KeyError, AttributeError):
            date_obj = datetime.fromtimestamp(getctime(path)).strftime(r'%Y%m%d%H%M%S')
            return date_obj

def get_img_stuff(file, directory):
    file_path = join(directory, file)
    file_type = file_path[file_path.find('.'):].upper()
    if (file_type == '.HEIC' or file_type == '.JPEG' or file_type == '.JPG' or file_type == '.PNG') and isfile(file_path):
        data = [file_path, file_type, get_time(file_path)]
        return data
    else:
        pass



def multi_get_img_stuff(directory):
    files = listdir(directory)
    
    threads = []
    results = []
    
    def get_stuff_thread(file):
        result = get_img_stuff(file, directory)
        results.append(result)
    
    for file in files:
        thread = Thread(target=get_stuff_thread, args=(file,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return results




