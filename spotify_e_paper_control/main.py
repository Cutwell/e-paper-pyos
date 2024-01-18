import logging
import threading
import time
from PIL import Image, ImageDraw
from spotify_e_paper_control.apps.spotify.spotify import Spotify
from TP_lib import epd2in13_V4, gt1151

logging.basicConfig(level=logging.DEBUG)


class App:
    def __init__(self):
        self.flag_t = 1
        self.i = self.j = self.k = self.ReFlag = self.SelfFlag = self.Page = 0
        self.spotify = Spotify()

        logging.info("E-Paper Control")

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

    def draw(self):
        """
        Get next view from current app, and apply to e-paper image.
        """

        newimage = self.spotify.draw() # call current app .draw() method

        # apply new view to image
        self.image.paste(newimage, (0, 0))

    def main(self):
        try:
            self.image = Image.new(
                "RGB", (122, 250), (255, 255, 255)
            )  # initialise with blank BG, then paste each new view as needed

            # build first layer
            self.draw()

            logging.info("Drawing first view")
            self.epd.displayPartBaseImage(self.epd.getbuffer(self.image))
            self.DrawImage = ImageDraw.Draw(self.image)
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

                    x, y = self.GT_Dev.X[0], self.GT_Dev.Y[0]

                    if self.ReFlag == 0:
                        self.spotify.handleTap(x, y)

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
