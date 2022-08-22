from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy
from PySide2.QtGui import QImage, QPainter
from PySide2.QtCore import Qt
import testing, threading
#bare bones - we should add multiple formats, scrolling and so forth

class image_window(QMainWindow):
	def __init__(self, title=None):
		self.image = None

		super().__init__(flags=Qt.Dialog)

		if title:
			self.setWindowTitle(title)

		self.setAutoFillBackground(True)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

	def new_image(self, image):

		width, height = image.size

		bytes_per_line = width * 3
		format = QImage.Format_RGB888
		self.image = QImage(image.tobytes(), width, height, bytes_per_line, format)
		self.update()

	def paintEvent(self, event):
		if self.image:
			painter = QPainter(self)
			#center
			geometry = self.geometry()
			iw, ih = self.image.width(), self.image.height()
			ww, wh = geometry.width(), geometry.height()

			x, y = (ww - iw) * .5, (wh - ih) * .5
			painter.drawImage(x, y, self.image)





app = QApplication()
mw = image_window('Image Viewer')


mw.setStyleSheet('''
	QMainWindow {
		background-color: #222;
	}
''')

mw.show()

threading.Thread(target=testing.show_images, args=(mw, 1.0)).start()

exit(app.exec_())