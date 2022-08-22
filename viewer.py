from protocols import binary_protocol_0_1_producer, binary_protocol_0_1_consumer
from testing import generate_random_images
from urllib.parse import urlparse
from viewer_widget import QApplication, viewer_window, QImage
import queue, threading, socket
import transport_managers
import time


class raw_pillow_producer(binary_protocol_0_1_producer):
	def __init__(self):
		self.pending = queue.Queue(1)
		self.dispatch_frame = self.pending.put
		self.produce_frame = self.pending.get

	def transport(self, image):

		frame_info = self.frame_info()
		if image.mode == 'RGB':
			frame_info.pixel_format = 1 	#TODO - define enums
			frame_info.pixel_stride = 3
		else:
			raise NotImplementedError(image.mode)

		#Basic properties
		frame_info.width, frame_info.height = image.size
		frame_info.frame_format = 1	 #TODO - define enums

		#Calculate strides
		frame_info.row_stride = frame_info.pixel_stride * frame_info.width

		#We don't bother with TS for now
		frame_info.ts_epoch = 0
		frame_info.ts_epoch_ns = 0

		frame = image.tobytes()
		frame_info.frame_size = len(frame)

		self.dispatch_frame((frame_info, frame))



class raw_image_consumer(binary_protocol_0_1_consumer):
	def __init__(self, viewer_widget):
		self.viewer_widget = viewer_widget

	def dispatch_frame(self, frame_info, frame):
		if frame_info.pixel_format == 1: 	#TODO - use enum

			assert frame_info.pixel_stride == 3	#Currently we just pass everything along to qt
				# from here so we only support the particular stride.
				# We may add more support for other ones in the future but it would of course be
				# better to not send any per pixel padding and solve it on the sending end.
				# this would be useful in this end in case we are connecting with an application
				# that we don't want to modify for some obscure reason we have not thought of yet

			#new_raw_image(self, width, height, bytes_per_line, data, format)
			self.viewer_widget.new_raw_image(frame_info.width, frame_info.height, frame_info.row_stride, frame, QImage.Format_RGB888)

			#TODO - we may later want to format any timestamp and put in the viewer so we should send that too but for now we ignore it

		else:
			raise NotImplementedError()




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

