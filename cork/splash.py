import threading
import platform
import os
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QProgressBar
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from math import floor
from cork import __file__

class QtCommunicator(QObject):
    progress_signal = pyqtSignal(int)
    type_signal = pyqtSignal(bool)
    text_signal = pyqtSignal(str)
    close_signal = pyqtSignal(bool)

class QtSplash(QWidget):
    def __init__(self, icon):
        self.should_close = False

        super().__init__()
        self.resize(380, 240)
        self.setFixedSize(400, 240)

        self.closeEvent = self.close_event
        self.setWindowTitle("Cork")
        self.setWindowIcon(self.get_icon("cork"))

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        icon_label = QLabel()
        pixmap = self.get_icon(icon).pixmap(134, 134)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(icon_label)

        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setContentsMargins(0, 5, 0, 5)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)
        
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.communicator = QtCommunicator()

        self.communicator.progress_signal.connect(self.set_progress)
        self.communicator.type_signal.connect(self.set_progress_mode)
        self.communicator.text_signal.connect(self.set_text)
        self.communicator.close_signal.connect(self.set_close)
    
    def close_event(self, event):
        if self.should_close == True:
            event.accept()
        else:
            event.ignore()

    def set_text(self, text):
        self.label.setText(text)
    
    def set_progress(self, progress):
        self.progress_bar.setValue(progress)
    
    def set_progress_mode(self, mode):
        if mode == True:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)
    
    def set_close(self, boolean):
        if boolean == True:
            self.close()
    
    def get_icon(self, icon_name):
        if platform.system() == "Linux":
            return QIcon.fromTheme(icon_name)
        else:
            return QIcon(os.path.join(os.path.dirname(__file__), "resources", icon_name, ".svg"))


class CorkSplash():
    def __init__(self):
        self.window = None
        self.is_showing = False
    
    def show(self, icon):
        self.is_showing = True

        def qt_function():
            self.app = QApplication([])

            self.window = QtSplash(icon)
            self.window.show()
            self.app.exec()
        
        self.qt_thread = threading.Thread(target=qt_function, daemon=True)
        self.qt_thread.start()
    
    def set_text(self, text):
        if self.window is None:
            return

        self.window.communicator.text_signal.emit(text)
    
    def set_progress(self, progress):
        if self.window is None:
            return

        self.window.communicator.progress_signal.emit(floor(progress * 100))
    
    def set_progress_mode(self, mode):
        if self.window is None:
            return

        self.window.communicator.type_signal.emit(mode)
    
    def close(self):
        self.is_showing = False

        self.window.should_close = True
        self.window.communicator.close_signal.emit(True)