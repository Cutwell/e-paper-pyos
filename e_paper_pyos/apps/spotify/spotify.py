import logging
import os
import urllib.request
from io import BytesIO

import segno
import spotipy
from flask import Flask, request
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth

logging.basicConfig(level=logging.DEBUG)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_ID")


class Spotify:
    def __init__(self, ssl_dir):
        """
        Spotify e-paper app, for controlling playback (play/pause/skip/previous).
        """
        self.is_playing = False
        self.state = None

        self.auth_manager = SpotifyOAuth(open_browser=False)

        self.app = Flask(__name__)
        self.callbackRecievedAccessCode = None
        self.app.add_url_rule("/", "index", self.callBackRoute)
        self.ssl_dir = ssl_dir

        logging.info("loading UI assets")

        self.ui_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            "spotify/assets",
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
        self.thumbnail = self.get_album_thumbnail()

    def draw(self):
        """
        Return 122x250 bitmap image, rendering the current app state.
        """

        logging.info("Creating new UI")

        # create new view 122x250 with white background
        newimage = Image.new("RGBA", (122, 250), (255, 255, 255, 1))

        self.thumbnail = self.get_album_thumbnail()

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

        return newimage

    def get_album_thumbnail(self):
        """
        Convert remote JPEG to BMP.
        """

        track = self.getCurrentTrack()
        if (
            track
            and "item" in track
            and "album" in track["item"]
            and "images" in track["item"]["album"]
            and len(track["item"]["album"]["images"]) > 0
        ):
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

    def handleTap(self, x, y):
        """
        Handle touchscreen input, given (x, y) coordinates of tap, to update app state.
        """

        if y <= 64:
            self.next_track()
        elif y > 64 and y < 186:
            self.playpause()
        elif y <= 186:
            self.previous_track()

    def get_auth_qrcode(self):
        url = self.spotify.getAuthURL()

        out = BytesIO()
        segno.make(url, error="h").save(out, scale=1, kind="png")
        out.seek(0)  # important to let Pillow load the PNG

        return (
            Image.open(out)
            .convert("RGB")
            .rotate(90)
            .resize((122, 122), resample=Image.Resampling.LANCZOS)
        )

    def callBackRoute(self):
        code_param = request.args.get("code")

        if code_param:
            self.callbackRecievedAccessCode = code_param
            logging.info("Received access code.")

            # Gracefully shutdown the Flask app
            self.shutdownCallbackServer()

        return "You can close this page and return to your RPi device."

    def shutdownCallbackServer():
        # This function will stop the Flask app gracefully
        func = request.environ.get("werkzeug.server.shutdown")
        if func is None:
            raise RuntimeError("Not running with the Werkzeug Server")
        func()

    def getAuthURL(self):
        url = self.auth_manager.get_authorize_url()
        return url

    def listenForAuthCallback(self):
        self.app.run(
            host="0.0.0.0",
            port=8000,
            ssl_context=(
                os.path.join(self.ssl_dir, "cert.pem"),
                os.path.join(self.ssl_dir, "key.pem"),
            ),
        )
        return self.callbackRecievedAccessCode

    def getAccessToken(self, access_code):
        self.auth_manager.get_access_token(code=access_code)

    def initSpotifySession(self):
        # set open_browser=False to prevent Spotipy from attempting to open the default browser
        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)

        print(self.spotify.me())

    def playpause(self):
        if "is_playing" in self.state and self.state["is_playing"]:
            # if playing, pause
            response = None
            if response.status_code == 200:
                # if succeeded in flipping play/pause state, flip is_playing boolean
                self.is_playing = False
        else:
            # if paused or doesn't exist, play
            response = None
            if response.status_code == 200:
                # if succeeded in flipping play/pause state, flip is_playing boolean
                self.is_playing = True

    def next_track(self):
        pass

    def previous_track(self):
        pass

    def getCurrentTrack(self):
        return None

    def updatePlaybackState(self):
        self.state = None

        if "is_playing" in self.state:
            self.is_playing = self.state["is_playing"]
        else:
            self.is_playing = False


if __name__ == "__main__":
    logging.info("Testing Spotify()")

    # Minimal example workflow for getting auth token with headless/inputless device
    spotify = Spotify()
    url = spotify.getAuthURL()
    # display url to user somehow - QR code?
    print(url)
    auth_response = spotify.listenForAuthCallback()
    spotify.getAccessToken(auth_response)
    spotify.initSpotifySession()
