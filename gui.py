from PyQt4 import QtGui
from PyQt4 import QtCore


class JenkinsConfigWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(JenkinsConfigWindow, self).__init__()
        self.parent = parent
        self.setWindowTitle('Jenkins setup')
        self.buttonLayout = QtGui.QVBoxLayout()
        self.url = QtGui.QLineEdit(self.parent.url)
        refresh_rate_text = str(self.parent.refresh_rate)
        self.refresh_rate = QtGui.QLineEdit(refresh_rate_text)
        QtCore.QObject.connect(self.url, QtCore.SIGNAL('returnPressed()'), self.submit_form)

        self.buttonLayout.addWidget(QtGui.QLabel('Jenkins url'))
        self.buttonLayout.addWidget(self.url)

        self.buttonLayout.addWidget(QtGui.QLabel('Refresh rate(seconds)'))
        self.buttonLayout.addWidget(self.refresh_rate)

        self.confirm = QtGui.QPushButton("&Confirm")
        self.confirm.clicked.connect(self.submit_form)

        self.url.setFocus()
        self.url.selectAll()

        self.buttonLayout.addWidget(self.confirm)
        self.setLayout(self.buttonLayout)

    def submit_form(self):
        url = str(self.url.text())
        self.close()
        self.parent.set_url(url)
        self.parent.set_refresh_rate(self.refresh_rate.text())
        self.parent.refresh_now()

