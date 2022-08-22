from testing import generate_random_images
#from urllib.parse import urlparse
from viewer_widget import QApplication, viewer_window, QImage
import queue, threading, socket

import time

from producers import raw_pillow_producer
from consumers import raw_image_consumer





app = QApplication()
mw = viewer_window('Image Viewer')

mw.setStyleSheet('''
	QMainWindow {
		background-color: #222;
	}
''')


test_image_source = raw_pillow_producer()
test_image_viewer = raw_image_consumer(mw)


ingress, egress = socket.socketpair()


def ingress_thread():
	test_image_source.produce_into_stream(ingress.makefile('wb'))


def egress_thread():
	test_image_viewer.consume_from_stream(egress.makefile('rb'))


def gen_images_thread():

	for image in generate_random_images():
		test_image_source.transport(image)
		time.sleep(0.2)



mw.show()

threading.Thread(target=ingress_thread).start()
threading.Thread(target=egress_thread).start()
threading.Thread(target=gen_images_thread).start()


exit(app.exec_())


