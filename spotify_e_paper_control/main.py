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

        logging.info("epd2in13_V4 Touch Demo")

        logging.info("loading UI assets")

        self.ui_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'spotify_e_paper_control/ui')
        self.play_button = Image.open(os.path.join(self.ui_dir, 'play.png'))
        self.pause_button = Image.open(os.path.join(self.ui_dir, 'pause.png'))
        self.previous_button = Image.open(os.path.join(self.ui_dir, 'previous.png'))    
        self.next_button = Image.open(os.path.join(self.ui_dir, 'previous.png')).rotate(180) # reuse previous.png reversed 180 degrees as next button

        logging.info("initialising")

        self.epd = epd2in13_V4.EPD()
        self.gt = gt1151.GT1151()
        self.GT_Dev = gt1151.GT_Development()
        self.GT_Old = gt1151.GT_Development()

        logging.info("initial clear")

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

    def get_spotify_thumbnail(self, url: str):
        """
        Convert remote JPEG to BMP.

        Parameters:
            url (str): URL to JPEG image to process.

        """

        # Load image from remote JPEG data, rotate 90 degrees and scale to 122x122 pixels
        return (
            Image.open(BytesIO(urllib.request.urlopen(url).read()))
            .rotate(90)
            .resize((122, 122))
        )

    def layer_ui(self):
        """
        Use PNG assets to create layered UI, then export to BMP for display.
        """

        # create new view 122x250 with white background
        newimage = Image.new("RGBA", (122, 250), (255, 255, 255, 1))

        # add thumbnail, UI, etc.
        # x=0, y=0 == top left, when device is oriented like a rectangle with power cord at base / bottom left
        newimage.paste(
            newimage, (0, 64)
        )
        newimage.paste(
            self.previous_button, (31, 190)
        )
        newimage.paste(
            self.next_button, (31, 60)
        )

        # export to BMP = strip alpha channel and convert to greyscale
        newimage = newimage.convert("RGB").convert("L")

        # apply new view to image
        self.image.paste(newimage, (0, 0))

    def main(self):
        try:
            self.image = Image.new(
                "RGB", (122, 250), (255, 255, 255)
            )  # initialise with blank BG, then paste each new view as needed
            self.thumbnail = self.bmp_from_jpeg_url(
                "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228"
            )

            # build first layer
            self.layer_ui()

            self.epd.displayPartBaseImage(self.epd.getbuffer(self.image))
            DrawImage = ImageDraw.Draw(self.image)
            self.epd.init(self.epd.PART_UPDATE)

            while 1:
                if self.i > 12 or self.ReFlag == 1:
                    if self.SelfFlag == 0:
                        self.epd.displayPartial(self.epd.getbuffer(self.image))
                    else:
                        self.epd.displayPartial_Wait(self.epd.getbuffer(self.image))
                    self.i = 0
                    self.k = 0
                    self.j += 1
                    self.ReFlag = 0
                    print("*** Draw Refresh ***\r\n")
                elif self.k > 50000 and self.i > 0:
                    self.epd.displayPartial(self.epd.getbuffer(self.image))
                    self.i = 0
                    self.k = 0
                    self.j += 1
                    print("*** Overtime Refresh ***\r\n")
                elif self.j > 50 or self.SelfFlag:
                    self.SelfFlag = 0
                    self.j = 0
                    self.epd.init(self.epd.FULL_UPDATE)
                    self.epd.displayPartBaseImage(self.epd.getbuffer(self.image))
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
