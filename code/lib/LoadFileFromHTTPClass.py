import configparser
import urllib.request
from multiprocessing import Process, Event
from PIL import Image
from shutil import copyfile
import time
import os


class LoadFileFromHttp:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./config/config.ini')

        self.TimeoutLoadImage = 30                  # default Timeout = 30s
        if config.has_option('Imagesource', 'TimeoutLoadImage'):
            self.TimeoutLoadImage = int(config['Imagesource']['TimeoutLoadImage'])

        self.URLImageSource = ''
        if config.has_option('Imagesource', 'URLImageSource'):
            self.URLImageSource = config['Imagesource']['URLImageSource']

        self.MinImageSize = 10000
        if config.has_option('Imagesource', 'MinImageSize'):
            self.MinImageSize = int(config['Imagesource']['MinImageSize'])

        self.log_Image = ''
        if config.has_option('Imagesource', 'LogImageLocation'):
            self.log_Image = config['Imagesource']['LogImageLocation']

        self.LogOnlyFalsePictures = False
        if config.has_option('Imagesource', 'LogOnlyFalsePictures'):
            self.LogOnlyFalsePictures = bool(config['Imagesource']['LogOnlyFalsePictures'])

        self.CheckAndLoadDefaultConfig()

        self.LastImageSafed = ''

    def CheckAndLoadDefaultConfig(self):
        defaultdir = "./config_default/"
        targetdir = './config/'
        if len(self.log_Image) > 0:
            if not os.path.exists(self.log_Image):
                zerlegt = self.log_Image.split('/')
                pfad = zerlegt[0]
                for i in range(1, len(zerlegt)):
                    pfad = pfad + '/' + zerlegt[i]
                    if not os.path.exists(pfad):
                        os.makedirs(pfad)

    def ReadURL(self, event, url, target):
        urllib.request.urlretrieve(url, target)
        event.set()

    def LoadImageFromURL(self, url, target):
        self.LastImageSafed = ''
        if url == '':
            url = self.URLImageSource
        event = Event()
        action_process = Process(target=self.ReadURL, args=(event, url, target))
        action_process.start()
        action_process.join(timeout=self.TimeoutLoadImage)
        action_process.terminate()
#        action_process.close()

        logtime = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        if event.is_set():
            self.saveLogImage(target, logtime)
            if self.VerifyImage(target) == True:
                image_size = os.stat(target).st_size
                if image_size > self.MinImageSize:
                    result = ''
                else:
                    result = 'Error - Imagefile too small. Size ' + str(image_size) + ', min size is ' + str(self.MinImageSize)+ '. Source: ' + str(url)
            else:
                result = 'Error - Imagefile is corrupted - Source: ' + str(url)
        else:
            result = 'Error - Problem during HTTP-request - URL: ' + str(url)
        return (result, logtime)

    def PostProcessLogImageProcedure(self, everythingsuccessfull):
        if (len(self.log_Image) > 0) and self.LogOnlyFalsePictures and (len(self.LastImageSafed) > 0) and everythingsuccessfull:
            os.remove(self.LastImageSafed)
            self.LastImageSafed = ''

    def VerifyImage(self, img_file):
        try:
            v_image = Image.open(img_file)
            v_image.verify()
            return True
        except OSError:
            return False

    def saveLogImage(self, img_file, logtime):
        if len(self.log_Image) > 0:
            speichername = self.log_Image + '/SourceImage_' + logtime + '.jpg'
            copyfile(img_file, speichername)
            self.LastImageSafed = speichername

    def saveImage(self, target):
        logtime = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        self.saveLogImage(target, logtime)
        if self.VerifyImage(target) == True:
            image_size = os.stat(target).st_size
            if image_size > self.MinImageSize:
                result = ''
            else:
                result = 'Error - Imagefile too small. Size ' + str(image_size) + ', min size is ' + str(self.MinImageSize)+ '. Source: ' + str(url)
        else:
            result = 'Error - Imagefile is corrupted - Source: ' + str(url)
        return (result, logtime)
