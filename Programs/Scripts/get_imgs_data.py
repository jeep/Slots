
# imports file maipulations
from os import listdir
from os.path import isfile, join, getctime

# imports image access and meta-data access
from PIL import Image, ExifTags

# imports date and time manipulation
from datetime import datetime

# imports access to multiple threads
from threading import Thread

def get_time(path):
    # opens the image at the path
    with Image.open(path) as image:
        try:
            image_exif = image._getexif()
            exif = { ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes }
            date_obj = datetime.strptime(exif['DateTimeOriginal'], r'%Y:%m:%d %H:%M:%S').strftime(r'%Y%m%d%H%M%S')
            return date_obj
        except (KeyError, AttributeError):
            try:
                image_exif = image.getexif()
                date_obj = datetime.strptime(image_exif[306], r'%Y:%m:%d %H:%M:%S').strftime(r'%Y%m%d%H%M%S')
                return date_obj
            except KeyError:
                date_obj = datetime.fromtimestamp(getctime(path)).strftime(r'%Y%m%d%H%M%S')
                return date_obj

def get_img_data(file, directory):
    # gets the file path
    file_path = join(directory, file)
    # gets the file type
    file_type = file_path[file_path.find('.'):].upper()
    # if the file type is an accepted type and is a file
    if (file_type == '.HEIC' or file_type == '.JPEG' or file_type == '.JPG' or file_type == '.PNG') and isfile(file_path):
        # returns the list of image data
        return [file_path, file_type, get_time(file_path)]
    else:
        pass

def multi_get_img_data(directory):
    # gets all files in the directory
    files = listdir(directory)
    
    threads = []
    results = []
    
    def get_data_thread(file):
        # adds the result of get_img_data to the results list
        results.append(get_img_data(file, directory))
    
    for file in files:
        # creates a thread that calls get_data_thread with file as the argument
        # and it will kill itself if the program ends
        thread = Thread(target=get_data_thread, args=(file,), daemon=True)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        # joins the threads
        thread.join()
    
    # return the list of the results
    return results

def no_threading_get_img_data(directory):
    return tuple(get_img_data(file, directory) for file in listdir(directory))