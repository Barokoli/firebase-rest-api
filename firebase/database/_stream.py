
#   Copyright (c) 2022 Asif Arman Rahman
#   Licensed under MIT (https://github.com/AsifArmanRahman/firebase/blob/main/LICENSE)

# --------------------------------------------------------------------------------------


import json
import os
import time
import threading
import logging

from ._keep_auth_session import KeepAuthSession
from ._closable_sse_client import ClosableSSEClient
from .. import Auth


logger = logging.getLogger("Firebase")


class Stream:

	def __init__(self, url_builder, stream_handler, build_headers, stream_id, is_async, auth: Auth):
		self.build_headers = build_headers
		self.url = ""
		self.url_builder = url_builder
		self.stream_handler = stream_handler
		self.stream_id = stream_id
		self.sse = None
		self.thread = None
		self.auth = auth

		if is_async:
			self.start()
		else:
			self.start_stream()

	def make_session(self):
		"""
		Return a custom session object to be passed to the ClosableSSEClient.
		"""
		session = KeepAuthSession()

		return session

	def start(self, is_reauth=False):
		self.thread = threading.Thread(target=self.start_stream, args=(is_reauth,))
		self.thread.start()

		return self

	def pre_reauth(self):
		logger.info("Closing stream before reauth")
		self.close(True)

	def post_reauth(self):
		logger.info("Starting stream after reauth")
		self.start(True)

	def start_stream(self, is_reauth=False):
		if not is_reauth:
			self.auth.before_refresh_cbs.append(self.pre_reauth)
			self.auth.after_refresh_cbs.append(self.post_reauth)
		self.url = self.url_builder()
		self.sse = ClosableSSEClient(self.url, session=self.make_session(), build_headers=self.build_headers)

		for msg in self.sse:
			if msg:
				msg_data = json.loads(msg.data)
				msg_data["event"] = msg.event

				if self.stream_id:
					msg_data["stream_id"] = self.stream_id

				self.stream_handler(msg_data)

	def close(self, is_reauth=False):
		while not self.sse and not hasattr(self.sse, 'resp'):
			time.sleep(0.001)

		self.sse.running = False
		self.sse.close()
		self.thread.join()

		if not is_reauth:
			self.auth.before_refresh_cbs.remove(self.pre_reauth)
			self.auth.after_refresh_cbs.remove(self.post_reauth)

		logger.info(f"Closed Stream ({os.getpid()}).")

		return self
