from producers import raw_pillow_producer
from consumers import log_consumer
from testing import generate_random_images
import transport_managers
import threading
import signal, os, time





class random_image_source(threading.Thread):
	def __init__(self, transport):
		super().__init__()
		self.transport = transport

	def run(self):
		for image in generate_random_images(10):	#We will generate 10 images
			self.transport.transport(image)





def signal_handler(signum, frame):
	print('Timeout - terminating test')
	os.kill(os.getpid(), signal.SIGTERM)


def test_fifo():

	production_transport = raw_pillow_producer()
	log_transport = log_consumer()

	def fifo_sender():
		transport_managers.fifo.connect('local_fifo', production_transport)

	def fifo_receiver():
		transport_managers.fifo.connect('local_fifo', log_transport)

	threading.Thread(target=fifo_sender).start()
	threading.Thread(target=fifo_receiver).start()
	random_image_source(production_transport).run()

	time.sleep(0.2)
	production_transport.dispatch_sentinel()

	assert len(log_transport.log) == 10




def test_unix():

	production_transport = raw_pillow_producer()
	log_transport = log_consumer()

	def unix_sender():
		transport_managers.unix.connect('local_unix', production_transport)

	def unix_receiver():
		transport_managers.unix.connect('local_unix', log_transport, listen=True, delete_existing=True)

	threading.Thread(target=unix_receiver).start()
	time.sleep(0.2)	#we must start these in order

	threading.Thread(target=unix_sender).start()

	random_image_source(production_transport).run()

	time.sleep(0.3)
	production_transport.dispatch_sentinel()

	assert len(log_transport.log) == 10





def test_tcp():

	production_transport = raw_pillow_producer()
	log_transport = log_consumer()

	def tcp_sender():
		transport_managers.tcp.connect(('localhost', 8001), production_transport)

	def tcp_receiver():
		transport_managers.tcp.connect(('localhost', 8001), log_transport, listen=True, reuse_address=True)

	threading.Thread(target=tcp_receiver).start()
	time.sleep(0.2)	#we must start these in order

	threading.Thread(target=tcp_sender).start()

	random_image_source(production_transport).run()

	time.sleep(0.3)
	production_transport.dispatch_sentinel()

	assert len(log_transport.log) == 10







signal.signal(signal.SIGALRM, signal_handler)

signal.alarm(1)
print('Testing FIFO')
test_fifo()

print('Testing AF_UNIX/STREAM')
signal.alarm(1)
test_unix()

print('Testing AF_INET/STREAM (tcp)')
signal.alarm(1)
test_unix()

print('Tests done - joining threads')

#Join all threads that is not the main thread
for t in threading.enumerate():
	if t is threading.main_thread():
		continue
	print(t)
	t.join()

print('done')
signal.alarm(0)

