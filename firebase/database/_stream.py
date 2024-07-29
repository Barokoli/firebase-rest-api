
#   Copyright (c) 2022 Asif Arman Rahman
#   Licensed under MIT (https://github.com/AsifArmanRahman/firebase/blob/main/LICENSE)

# --------------------------------------------------------------------------------------


import json
import time
import threading

from ._keep_auth_session import KeepAuthSession
from requests_sse import EventSource


class Stream:

	def __init__(self, url, stream_handler, build_headers, stream_id, is_async):
		self.build_headers = build_headers
		self.url = url
		self.stream_handler = stream_handler
		self.stream_id = stream_id
		self.sse = None
		self.thread = None

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

	def start(self):
		self.thread = threading.Thread(target=self.start_stream)
		self.thread.start()

		return self

	def start_stream(self):
		with EventSource(self.url, session=self.make_session(), headers=self.build_headers()) as self.sse:
			for msg in self.sse:
				print(f"Stream Receive: \n{msg.origin}[{msg.type}]:\n{msg.data}")
				msg_data = json.loads(msg.data)
				if msg_data is not None:
					msg_data["event"] = msg.type
					if self.stream_id:
						msg_data["stream_id"] = self.stream_id
					self.stream_handler(msg_data)

		# self.sse = ClosableSSEClient(self.url, session=self.make_session(), build_headers=self.build_headers)
		#
		# for msg in self.sse:
		# 	if msg:
		# 		msg_data = json.loads(msg.data)
		# 		if msg_data is None:
		# 			print("Stream Closed!")
		# 			break  # stream closed
		# 		msg_data["event"] = msg.event
		#
		# 		if self.stream_id:
		# 			msg_data["stream_id"] = self.stream_id
		#
		# 		self.stream_handler(msg_data)

	def close(self):
		# while not self.sse and not hasattr(self.sse, 'resp'):
		# 	time.sleep(0.001)

		# self.sse.running = False
		self.sse.close()
		self.thread.join()

		return self
