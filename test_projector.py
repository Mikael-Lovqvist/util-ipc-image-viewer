from PIL import Image, ImageDraw
import random
from library.testing import generate_random_images
from library.producers import raw_pillow_producer
from library import transport_managers
import threading
import sys

try:
	host = sys.argv[1]
	port = int(sys.argv[2])
except:
	host = '192.168.1.132'
	port = 6969






def create_test_image(width=1920, height=1080, inverted=False):

	if inverted:
		background = (255, 255, 255)
		features = (0, 0, 0)
	else:
		background = (0, 0, 0)
		features = (255, 255, 255)


	#Note - currently we only support RGB so we will use that here for now even though we only need grayscale
	image = Image.new('RGB', (width, height), color=background)

	draw = ImageDraw.Draw(image)

	spacing = 64

	for i in range(width // spacing):
		draw.line((i * spacing, 0, i * spacing, height), fill=features)

	for i in range(height // spacing):
		draw.line((0, i * spacing, width, i * spacing), fill=features)

	circles = 20

	for i in range(circles):
		r = (i+1) * spacing
		draw.arc((width * .5-r, height * .5-r, width * .5+r, height * .5+r), 0, 360, fill=features)


	return image




def variant2():	#This variant doesn't need to create an additional thread  and allows us to write a simple function to just send an image off
	transport = raw_pillow_producer(one_shot = True)
	transport.transport(create_test_image())
	transport_managers.tcp.connect((host, port), transport)


if __name__ == '__main__':
	variant2()

	# DISPLAY=:0 python viewer.py "tcp://0.0.0.0:6969?listen&reuse_address"

