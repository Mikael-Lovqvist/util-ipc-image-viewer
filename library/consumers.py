from .protocols import  binary_protocol_0_1_consumer
from .viewer_widget import QImage

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


#This is used for testing
class log_consumer(binary_protocol_0_1_consumer):
	def __init__(self):
		self.log = list()

	def dispatch_frame(self, frame_info, frame):
		self.log.append(frame_info)