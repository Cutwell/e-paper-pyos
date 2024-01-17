import logging
import os
import segno
import spotipy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import time

from spotipy.oauth2 import SpotifyOAuth

logging.basicConfig(level=logging.DEBUG)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_ID")


class RequestHandler(BaseHTTPRequestHandler):
    first_request = None

    def do_GET(self):
        if not self.first_request:
            self.first_request = self.path
            print(f"Received first request for: {self.first_request}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hello, world!")


class Spotify:
	def __init__(self):
		self.is_playing = False
		self.state = None

		self.auth_manager = SpotifyOAuth(open_browser=False)

	def getAuthURL(self):
		url = self.auth_manager.get_authorize_url()
		return url
	
	def listenForAuthCallback(self):
		# Start the server in a separate thread
		server_thread = threading.Thread(target=self.callbackServer)
		server_thread.start()

		# Wait for the first request
		while not RequestHandler.first_request:
			time.sleep(1)

		# Get the first request URL
		first_request_url = RequestHandler.first_request
		print(f"First request URL: {first_request_url}")

		# Stop the server
		server_thread.join()

		# Return parsed auth response
		return self.auth_manager.parse_auth_response_url(first_request_url)

	def callbackServer(self):
		server_address = ('', 8000)  # You can change the port if needed
		httpd = ThreadingHTTPServer(server_address, RequestHandler)

		print("Server started. Listening on port 8000.")
		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			pass

		httpd.server_close()
		print("Server stopped.")

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
