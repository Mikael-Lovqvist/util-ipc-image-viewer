from library.testing import generate_random_images
from library.producers import raw_pillow_producer
from library import transport_managers
import threading
import sys

try:
	host = sys.argv[1]
	port = int(sys.argv[2])
except:
	host = 'localhost'
	port = 8001


def variant1():

	transport = raw_pillow_producer()


	def run_sender():
		transport_managers.tcp.connect((host, port), transport)

	threading.Thread(target=run_sender).start()
	[image] = generate_random_images(1)
	transport.transport(image)
	transport.dispatch_sentinel()





def variant2():	#This variant doesn't need to create an additional thread  and allows us to write a simple function to just send an image off
	transport = raw_pillow_producer(one_shot = True)
	[image] = generate_random_images(1)
	transport.transport(image)
	#transport_managers.tcp.connect(('localhost', 8001), transport)
	transport_managers.tcp.connect((host, port), transport)

variant2()
