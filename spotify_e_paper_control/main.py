import os
from StringIO import StringIO
from PIL import Image,ImageDraw,ImageFont
import urllib
from TP_lib import gt1151
from TP_lib import epd2in13_V4
import logging
import threading
import time


logging.basicConfig(level=logging.DEBUG)

class App:
    def __init__(self):
        self.flag_t = 1
        
        self.fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')

        self.font15 = ImageFont.truetype(os.path.join(self.fontdir, 'Font.ttc'), 15)
        self.font24 = ImageFont.truetype(os.path.join(self.fontdir, 'Font.ttc'), 24)

        logging.info("epd2in13_V4 Touch Demo")
    
        self.epd = epd2in13_V4.EPD()
        self.gt = gt1151.GT1151()
        self.GT_Dev = gt1151.GT_Development()
        self.GT_Old = gt1151.GT_Development()
        
        logging.info("init and Clear")
        
        self.epd.init(self.epd.FULL_UPDATE)
        self.gt.GT_Init()
        self.epd.Clear(0xFF)

        t = threading.Thread(target = self.pthread_irq)
        t.setDaemon(True)
        t.start()

    def pthread_irq(self):
        print("pthread running")
        while self.flag_t == 1 :
            if(self.gt.digital_read(self.gt.INT) == 0) :
                self.GT_Dev.Touch = 1
            else :
                self.GT_Dev.Touch = 0
        print("thread:exit")

    def bmp_from_jpeg_url(self, url: str):
        """
        Convert remote JPEG to BMP.
        
        Parameters:
            url (str): URL to JPEG image to process.
        
        """
        
        # Load image from remote JPEG data, then convert to bitmap and
        return Image.open(StringIO(urllib.urlopen(url).read())).tobitmap()

    def main(self):
        # test
        try:
            image = self.bmp_from_jpeg_url("https://i.scdn.co/image/ab67616d00004851f56b861c3ca4dd44a3072c60")
            self.epd.displayPartBaseImage(self.epd.getbuffer(image))
            DrawImage = ImageDraw.Draw(image)
            self.epd.init(self.epd.PART_UPDATE)

        except IOError as e:
            logging.info(e)
            
        except KeyboardInterrupt:    
            logging.info("ctrl + c:")
            self.flag_t = 0
            self.epd.sleep()
            time.sleep(2)
            self.t.join()
            self.epd.Dev_exit()
            exit()

if __name__ == "__main__":
    main()