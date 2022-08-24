from .protocols import binary_protocol_0_1_producer
import queue


#This is more of a transporter than producer - we should potentially do some refactoring to name things better
class raw_pillow_producer(binary_protocol_0_1_producer):
	def __init__(self, one_shot=False):
		self.one_shot = one_shot
		if one_shot:
			self.pending = queue.Queue(2)	#This is so that we may queue up the sentinel right away
		else:
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

		if self.one_shot:
			self.dispatch_sentinel()

