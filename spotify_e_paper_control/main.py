import os
from io import BytesIO
from PIL import Image, ImageDraw
import urllib.request
from TP_lib import gt1151
from TP_lib import epd2in13_V4
import logging
import threading
import time
import requests


logging.basicConfig(level=logging.DEBUG)


class Spotify:
    def __init__(self):
        logging.info("Spotify Control")

        self.is_playing = False
        self.state = None
        self.access_token = self.getAccessToken()
        self.jsonAuthBearerHeader = {"content-type": "application/json; charset=UTF-8",'Authorization':'Bearer {}'.format(self.access_token)}

        self.updatePlaybackState()

    def get(self, url: str, headers: dict):
        return requests.get(url, headers=headers).json()
    
    def post(self, url: str, headers: dict, data: str):
        if data:
            return requests.post(url, headers=headers, data=data).json()
        else:
            return requests.post(url, headers=headers).json()
    
    def put(self, url: str, headers: dict):
        return requests.put(url, headers=headers).json()

    def getAccessToken(self):
        headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
        data = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
            "client_secret": os.getenv("SPOTIFY_CLIENT_ID")
        }
        return self.post("https://accounts.spotify.com/api/token", headers, data)

    def playpause(self):
        if "is_playing" in self.state and self.state["is_playing"]:
            # if playing, pause
            self.put("https://api.spotify.com/v1/me/player/pause", self.jsonAuthBearerHeader)
            self.is_playing
        else:
            # if paused or doesn't exist, play
            self.put("https://api.spotify.com/v1/me/player/play", self.jsonAuthBearerHeader)

    def next_track(self):
        self.post("https://api.spotify.com/v1/me/player/next", self.jsonAuthBearerHeader)

    def previous_track(self):
        self.post("https://api.spotify.com/v1/me/player/previous", self.jsonAuthBearerHeader)

    def getCurrentTrack(self):
        return self.get("https://api.spotify.com/v1/me/player/currently-playing", self.jsonAuthBearerHeader)

    def updatePlaybackState(self):
        self.state = self.get("https://api.spotify.com/v1/me/player", self.jsonAuthBearerHeader)

        if "is_playing" in self.state:
            self.is_playing = self.state["is_playing"]
        else:
            self.is_playing = False

class App:
    def __init__(self):
        self.flag_t = 1
        self.i = self.j = self.k = self.ReFlag = self.SelfFlag = 0
        self.spotify = Spotify()

        logging.info("E-Paper Control")

        logging.info("loading UI assets")

        self.ui_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            "spotify_e_paper_control/ui",
        )
        self.play_button = Image.open(os.path.join(self.ui_dir, "play.png")).rotate(90)
        self.pause_button = Image.open(os.path.join(self.ui_dir, "pause.png")).rotate(
            90
        )
        self.previous_button = Image.open(
            os.path.join(self.ui_dir, "previous.png")
        ).rotate(90)
        self.next_button = Image.open(os.path.join(self.ui_dir, "previous.png")).rotate(
            270
        )  # reuse previous.png reversed 180 degrees as next button

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

    def get_spotify_thumbnail(self):
        """
        Convert remote JPEG to BMP.
        """

        track = self.spotify.getCurrentTrack()
        if "item" in track and "album" in track["item"] and "images" in track["item"]["album"] and len(track["item"]["album"]["images"]) > 0:
            url = track["item"]["album"]["images"][0]["url"]
        else:
            # if no track thumbnail, return empty white background
            return Image.new("RGBA", (122, 122), (255, 255, 255, 1))

        logging.info(f"Loading image from {url}")

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

        logging.info("Creating new UI")

        # create new view 122x250 with white background
        newimage = Image.new("RGBA", (122, 250), (255, 255, 255, 1))

        self.thumbnail = self.get_spotify_thumbnail()

        # add thumbnail, UI, etc.
        # x=0, y=0 == top left, when device is oriented like a rectangle with power cord at base / bottom left
        newimage.paste(self.thumbnail, (0, 64), self.thumbnail.convert("RGBA"))
        newimage.paste(
            self.previous_button, (31, 190), self.previous_button.convert("RGBA")
        )
        newimage.paste(self.next_button, (31, 0), self.next_button.convert("RGBA"))

        self.spotify.updatePlaybackState()

        if self.spotify.is_playing:
            # playing, so offer pause option
            newimage.paste(
                self.pause_button, (31, 94), self.pause_button.convert("RGBA")
            )  # place in middle of thumbnail
        else:
            # paused, so offer play option
            newimage.paste(
                self.play_button, (31, 94), self.play_button.convert("RGBA")
            )  # place in middle of thumbnail
            

        # export to BMP = strip alpha channel and convert to greyscale
        newimage = newimage.convert("RGB").convert("L")

        # apply new view to image
        self.image.paste(newimage, (0, 0))

    def main(self):
        try:
            self.image = Image.new(
                "RGB", (122, 250), (255, 255, 255)
            )  # initialise with blank BG, then paste each new view as needed
            self.thumbnail = self.get_spotify_thumbnail()

            # build first layer
            self.layer_ui()

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
                        if y <= 64:
                            self.spotify.next_track()
                        elif y > 64 and y < 186:
                            self.spotify.playpause()
                        elif y <= 186:
                            self.spotify.previous_track()

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
