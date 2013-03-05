from PyQt4 import QtGui
from PyQt4 import QtCore


class JenkinsConfigWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(JenkinsConfigWindow, self).__init__()
        self.parent = parent
        self.setWindowTitle('Jenkins setup')
        self.buttonLayout = QtGui.QVBoxLayout()
        self.url = QtGui.QLineEdit("Url")

        self.buttonLayout.addWidget(self.url)

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


class ChooseRedditWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ChooseRedditWindow, self).__init__()
        self.parent = parent
        self.setWindowTitle('New subreddit to follow')
        self.layout = QtGui.QGridLayout()

        self.setup_radio_buttons_sorting()
        self.setup_radiobuttons_click_action()

        self.confirm = QtGui.QPushButton("&Confirm")
        self.confirm.clicked.connect(self.submit_form)

        self.setup_edit_btn()
        self.layout.addWidget(QtGui.QLabel("What subreddit do you wish to be kept informed about?"), 0, 0, 1, 2)
        self.layout.addWidget(self.subreddit, 1, 0, 1, 2)

        self.links_only = QtGui.QCheckBox()
        self.layout.addWidget(QtGui.QLabel("Links only?"), 2, 0)
        self.layout.addWidget(self.links_only, 2, 1)

        # self.layout.addWidget(QtGui.QLabel("Which subcategory?"), 2, 0)
        self.layout.addWidget(self.buttonBox, 3, 0)
        self.layout.addWidget(self.click_buttonBox, 3, 1)

        self.layout.addWidget(self.confirm, 4, 0, 1, 2, QtCore.Qt.AlignCenter)

        self.setLayout(self.layout)
        self.subreddit.setFocus()
        self.subreddit.selectAll()

    def setup_edit_btn(self):
        self.subreddit = QtGui.QLineEdit("python")

        QtCore.QObject.connect(self.subreddit, QtCore.SIGNAL('returnPressed()'), self.submit_form)
        QtCore.QObject.connect(self, QtCore.SIGNAL('focusIn()'), self.subreddit.setFocus)

    def setup_radio_buttons_sorting(self):
        self.buttonBox = QtGui.QGroupBox("Subreddit type")
        self.buttonLayout = QtGui.QVBoxLayout()

        self.hot = QtGui.QRadioButton("Hot")
        self.hot.setChecked(True)
        self.new = QtGui.QRadioButton("New")
        self.ris = QtGui.QRadioButton("Rising")
        self.top = QtGui.QRadioButton("Top")

        self.buttons = [self.hot, self.new, self.ris, self.top]

        self.buttonLayout.addWidget(self.hot)
        self.buttonLayout.addWidget(self.new)
        self.buttonLayout.addWidget(self.ris)
        self.buttonLayout.addWidget(self.top)
        self.buttonBox.setLayout(self.buttonLayout)

    def setup_radiobuttons_click_action(self):
        self.click_buttonBox = QtGui.QGroupBox("Menu items link to")
        self.click_buttonLayout = QtGui.QVBoxLayout()

        self.link = QtGui.QRadioButton("Link")
        self.link.setChecked(True)
        self.thread = QtGui.QRadioButton("Thread")

        self.click_buttons = [self.link, self.thread]

        self.click_buttonLayout.addWidget(self.link)
        self.click_buttonLayout.addWidget(self.thread)
        self.click_buttonBox.setLayout(self.click_buttonLayout)

    def submit_form(self):
        # print 'Clickety-click!!!'
        sub = str(self.subreddit.text())
        # reddit_type = str(self.subreddit.text())
        # print 'Subreddit value: %s' % sub
        reddit_type = str([r.text() for r in self.buttons if r.isChecked()][0]).lower()
        # print 'Button checked: %s' % str(reddit_type)
        self.parent.add_subreddit(sub, reddit_type)
        # Close self
        self.close()
        # Renew entries in the menu
        self.parent.renew_entries()

        return
