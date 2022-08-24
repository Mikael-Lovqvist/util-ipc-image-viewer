from PySide2.QtWidgets import QApplication, QMainWindow, QSizePolicy
from PySide2.QtGui import QImage, QPainter
from PySide2.QtCore import Qt
#bare bones - we should add multiple formats, scrolling and so forth

class viewer_window(QMainWindow):
	def __init__(self, title=None):
		self.image = None
		self.zoom = 1.0
		self.zoom_exp = 0
		self.antialiasing = False

		super().__init__(flags=Qt.Dialog)

		if title:
			self.setWindowTitle(title)

		self.setAutoFillBackground(True)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Plus:
			self.zoom_exp += .25
			self.zoom = 2.0 ** self.zoom_exp
			print(self.zoom)
			self.update()
		elif event.key() == Qt.Key_Minus:
			self.zoom_exp -= .25
			self.zoom = 2.0 ** self.zoom_exp
			print(self.zoom)
			self.update()
		elif event.key() == Qt.Key_A:
			self.antialiasing = not self.antialiasing
			self.update()

	def new_pil_image(self, image):

		width, height = image.size

		bytes_per_line = width * 3
		format = QImage.Format_RGB888
		self.image = QImage(image.tobytes(), width, height, bytes_per_line, format)
		self.update()

	def new_raw_image(self, width, height, bytes_per_line, data, format):
		self.image = QImage(data, width, height, bytes_per_line, format)
		self.update()

	def paintEvent(self, event):
		if self.image:
			painter = QPainter(self)
			#center
			geometry = self.geometry()
			iw, ih = self.image.width(), self.image.height()
			ww, wh = geometry.width(), geometry.height()

			#rzoom = 1.0 / self.zoom

			x, y = (ww - iw * self.zoom) * .5, (wh - ih * self.zoom) * .5
			painter.translate(x, y)
			painter.scale(self.zoom, self.zoom)
			painter.setRenderHint(painter.SmoothPixmapTransform, self.antialiasing)

			painter.drawImage(0, 0, self.image)



