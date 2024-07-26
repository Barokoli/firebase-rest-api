
#   Copyright (c) 2022 Asif Arman Rahman
#   Licensed under MIT (https://github.com/AsifArmanRahman/firebase/blob/main/LICENSE)

# changed 2024 Sebastian Witt

# --------------------------------------------------------------------------------------


from sseclient import SSEClient


class ClosableSSEClient(SSEClient):

	def __init__(self, *args, build_headers, **kwargs):
		self.build_headers = build_headers
		self.should_connect = True

		super(ClosableSSEClient, self).__init__(*args, **kwargs)

	def _connect(self):
		if self.should_connect:
			self.requests_kwargs['headers'].update(self.build_headers())
			super(ClosableSSEClient, self)._connect()
		else:
			raise StopIteration()

	def close(self):
		self.should_connect = False
		self.retry = 0
		self.resp.close()
