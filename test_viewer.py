from viewer_widget import QApplication, viewer_window
import testing
import threading



app = QApplication()
mw = viewer_window('Image Viewer')


mw.setStyleSheet('''
	QMainWindow {
		background-color: #222;
	}
''')

mw.show()

threading.Thread(target=testing.show_images, args=(mw, 1.0)).start()

exit(app.exec_())