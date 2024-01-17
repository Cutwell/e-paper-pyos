import logging
import os
import spotipy
from flask import Flask, request
import threading
import time

from spotipy.oauth2 import SpotifyOAuth

logging.basicConfig(level=logging.DEBUG)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_ID")


class Spotify:
	def __init__(self):
		self.is_playing = False
		self.state = None

		self.auth_manager = SpotifyOAuth(open_browser=False)

		self.app = Flask(__name__)
		self.first_request_url = None
		self.app.add_url_rule('/', 'index', self.callBackRoute)
		

	def callBackRoute(self):
		if not self.first_request_url:
			self.first_request_url = request.url
			print(f"Received first request for: {self.first_request_url}")

		return "You can close this page and return to your RPi device."

	def callbackServer(self):
		self.app.run(host="0.0.0.0", port=8000)

	def getAuthURL(self):
		url = self.auth_manager.get_authorize_url()
		return url
	
	def listenForAuthCallback(self):
		# Start the server in a separate thread
		server_thread = threading.Thread(target=self.callbackServer)
		server_thread.start()

		# Wait for the first request
		while not self.first_request_url:
			time.sleep(1)

		# Get the first request URL
		print(f"First request URL: {self.first_request_url}")

		# Stop the server
		server_thread.join()

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
