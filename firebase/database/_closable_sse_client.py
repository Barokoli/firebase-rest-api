
#   Copyright (c) 2022 Asif Arman Rahman
#   Licensed under MIT (https://github.com/AsifArmanRahman/firebase/blob/main/LICENSE)

# changed 2024 Sebastian Witt

# --------------------------------------------------------------------------------------


import socket
import time

from ._custom_sse_client import SSEClient


class ClosableSSEClient(SSEClient):

	def __init__(self, *args, **kwargs):
		self.should_connect = True
		super(ClosableSSEClient, self).__init__(*args, **kwargs)

	def _connect(self):
		if self.should_connect:
			super(ClosableSSEClient, self)._connect()
		else:
			raise StopIteration()

	def close(self):
		self.should_connect = False
		self.retry = 0

		for r in range(0, 8):
			if self.resp is not None:
				break
			time.sleep(0.2)

		if self.resp is None:
			return

		# if hasattr(self.resp.raw, '_fp'):
		# 	self.resp.raw._fp.fp.raw._sock.shutdown(socket.SHUT_RDWR)
		# 	self.resp.raw._fp.fp.raw._sock.close()
		# else:
		self.resp.close()
