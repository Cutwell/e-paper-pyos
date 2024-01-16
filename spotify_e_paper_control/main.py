import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import urllib.request
from TP_lib import gt1151
from TP_lib import epd2in13_V4
import logging
import threading
import time


logging.basicConfig(level=logging.DEBUG)


class App:
    def __init__(self):
        self.flag_t = 1
        self.i = self.j = self.k = self.ReFlag = self.SelfFlag = 0

        # self.fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
        # self.font15 = ImageFont.truetype(os.path.join(self.fontdir, 'Font.ttc'), 15)
        # self.font24 = ImageFont.truetype(os.path.join(self.fontdir, 'Font.ttc'), 24)

        logging.info("epd2in13_V4 Touch Demo")

        self.epd = epd2in13_V4.EPD()
        self.gt = gt1151.GT1151()
        self.GT_Dev = gt1151.GT_Development()
        self.GT_Old = gt1151.GT_Development()

        logging.info("init and Clear")

        self.epd.init(self.epd.FULL_UPDATE)
        self.gt.GT_Init()
        self.epd.Clear(0xFF)

        self.t = threading.Thread(target=self.pthread_irq)
        self.t.setDaemon(True)
        self.t.start()

    def pthread_irq(self):
        print("pthread running")
        while self.flag_t == 1:
            if self.gt.digital_read(self.gt.INT) == 0:
                self.GT_Dev.Touch = 1
            else:
                self.GT_Dev.Touch = 0
        print("thread:exit")

    def bmp_from_jpeg_url(self, url: str):
        """
        Convert remote JPEG to BMP.

        Parameters:
            url (str): URL to JPEG image to process.

        """

        # Load image from remote JPEG data, then remove alpha channels, convert to greyscale (make bitmap), rotate 90 degrees and scale to 122x122 pixels
        return (
            Image.open(BytesIO(urllib.request.urlopen(url).read()))
            .convert("RGB")
            .convert("L")
            .rotate(270)
            .resize((122, 122))
        )

    def main(self):
        try:
            image = Image.new("RGB", (122, 250), (255, 255, 255))
            newimage = self.bmp_from_jpeg_url(
                "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228"
            )
            image.paste(
                newimage, (0, 64)
            )  # position in center of screen (0,0 is top left when oriented like a rectangle with power at base)

            self.epd.displayPartBaseImage(self.epd.getbuffer(image))
            DrawImage = ImageDraw.Draw(image)
            self.epd.init(self.epd.PART_UPDATE)

            while 1:
                if self.i > 12 or self.ReFlag == 1:
                    if self.SelfFlag == 0:
                        self.epd.displayPartial(self.epd.getbuffer(image))
                    else:
                        self.epd.displayPartial_Wait(self.epd.getbuffer(image))
                    self.i = 0
                    self.k = 0
                    self.j += 1
                    self.ReFlag = 0
                    print("*** Draw Refresh ***\r\n")
                elif self.k > 50000 and self.i > 0:
                    self.epd.displayPartial(self.epd.getbuffer(image))
                    self.i = 0
                    self.k = 0
                    self.j += 1
                    print("*** Overtime Refresh ***\r\n")
                elif self.j > 50 or self.SelfFlag:
                    self.SelfFlag = 0
                    self.j = 0
                    self.epd.init(self.epd.FULL_UPDATE)
                    self.epd.displayPartBaseImage(self.epd.getbuffer(image))
                    self.epd.init(self.epd.PART_UPDATE)
                    print("--- Self Refresh ---\r\n")
                else:
                    self.k += 1

                # Read the touch input
                self.gt.GT_Scan(self.GT_Dev, self.GT_Old)
                if (
                    self.GT_Old.X[0] == self.GT_Dev.X[0]
                    and self.GT_Old.Y[0] == self.GT_Dev.Y[0]
                    and self.GT_Old.S[0] == self.GT_Dev.S[0]
                ):
                    continue

                if self.GT_Dev.TouchpointFlag:
                    self.i += 1
                    self.GT_Dev.TouchpointFlag = 0

        except IOError as e:
            logging.error(f"ERROR: {e}")

        except KeyboardInterrupt:
            logging.info("ctrl + c interrupt")
            self.flag_t = 0
            self.epd.sleep()
            time.sleep(2)
            self.t.join()

        finally:
            logging.info("clearing screen + exiting")
            self.epd.init(self.epd.FULL_UPDATE)
            self.gt.GT_Init()
            self.epd.Clear(0xFF)
            self.epd.Dev_exit()
            exit()


if __name__ == "__main__":
    app = App()
    app.main()
