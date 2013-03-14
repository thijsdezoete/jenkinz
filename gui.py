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


class LoginWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__()
        self.parent = parent
        self.setWindowTitle('New subreddit to follow')
        self.buttonLayout = QtGui.QVBoxLayout()
        self.username = QtGui.QLineEdit("username")
        self.password = QtGui.QLineEdit()
        # Display password as password
        self.password.setEchoMode(QtGui.QLineEdit.Password)

        self.buttonBox = QtGui.QGroupBox("Credentials")

        self.buttonLayout.addWidget(self.username)
        self.buttonLayout.addWidget(self.password)
        self.buttonBox.setLayout(self.buttonLayout)

        self.confirm = QtGui.QPushButton("&Confirm")
        self.confirm.clicked.connect(self.submit_form)

        self.username.setFocus()
        self.username.selectAll()

        self.buttonLayout.addWidget(self.confirm)
        self.setLayout(self.buttonLayout)

    def submit_form(self):
        username = str(self.username.text())
        password = str(self.password.text())
        print 'Login information saved.'
        self.close()
        self.parent.set_session_details(username, password)


