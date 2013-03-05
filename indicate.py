import sys
import os
from PyQt4 import QtCore
from PyQt4 import QtGui
import requests
from urlparse import urlparse


# if 'linux' in platform:
#     import appindicator
# elif 'darwin' in platform:
#     import test


class Favicon(object):
    def __init__(self):
        self.storage_cache = os.path.abspath(os.path.dirname(__file__) + '/img_cache')
        # print 'storage cache:'
        # print self.storage_cache
        self.icons = {}
        self.icon_pm = {}

    def _get_direct(self, url, name=None):
        if not name:
            raise
        icon = requests.get(url)

        return icon.content

    def _get_local(self, name):
        try:
            if self.icons[name]:
                return self.icons[name]
        except KeyError:
            return None

    def _get_remote(self, name):
        url = urlparse(name).path
        # print url
        # url = name

        # if 'http://' in url:
        #     url = url[6:]
        # print 'Get favicon from %s' % url
        icon_url = "http://www.google.com/s2/favicons?domain="

        #icon_url = "http://g.etfv.co/"
        icon = requests.get(icon_url + url)
        # print icon_url + url
        # print icon.headers

        icon_file = self.storage_cache + '/favicon-%s.ico' % name

        return icon.content

    def get_image_url(self, url, name=None):
        icon = self._get_direct(url, name)
        dataBuffer = QtCore.QByteArray(icon)
        pm = QtGui.QPixmap(32, 32)
        pm.loadFromData(dataBuffer)
        self.icon_pm[name] = pm
        # print self.icon_pm[name].getSize()
        self.icons[name] = QtGui.QIcon(self.icon_pm[name])
        return name

    def get(self, name):
        icon = self._get_local(name)
        if not icon:
            icon = self._get_remote(name)

            dataBuffer = QtCore.QByteArray(icon)
            pm = QtGui.QPixmap(32, 32)
            pm.loadFromData(dataBuffer)
            self._icon_pixmap = pm
            if not pm:
                print '---- NO PIXMAP!!!!! ----'
            self.icons[name] = QtGui.QIcon(pm)

        return name

    def put(self, name):
        pass


class SetupTrayWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SetupTrayWindow, self).__init__()
        self.url = QtGui.QLineEdit("www.last.fm")
        self.parent = parent
        self.url.selectAll()
        QtCore.QObject.connect(self.url, QtCore.SIGNAL('returnPressed()'), self.get_favicon)
        QtCore.QObject.connect(self, QtCore.SIGNAL('focusIn()'), self.url.setFocus)
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(QtGui.QLabel("Url for the url"), 0, 0)
        self.layout.addWidget(self.url, 1, 1)
        self.setLayout(self.layout)
        self.url.setFocus()
        self.setWindowTitle('Setup New Tray Icon')

    def read_icon_into_qicon(self, icon_file):
        dataBuffer = QtCore.QByteArray(icon_file)
        #new_icon = QtGui.QImage(dataBuffer)
        pm = QtGui.QPixmap(32, 32)
        pm.loadFromData(dataBuffer)
        self._icon_pixmap = pm
        self.icon = QtGui.QIcon(pm)

        return self.icon

    def get_favicon(self):
        url = str(self.url.text())
        _file = os.path.abspath(os.path.dirname(__file__))
        print _file
        icon_file = 'favicon-%s.ico' % url
        files = os.listdir(_file)

        if not icon_file in files:
            print 'File not in local-cache'
            icon = self.download_favicon()
        else:
            _loc = _file + '/' + files[files.index(icon_file)]
            print _loc
            icon_data = open(_loc, 'rb').read()
            icon = self.read_icon_into_qicon(icon_data)

        self.parent.add_icon(icon, url)
        lbl = QtGui.QLabel("placeholder")

        lbl.setPixmap(self._icon_pixmap)
        self.layout.addWidget(
            lbl, 1, 0
        )

        self.parent.add_icon_to_menu(url, 'Change tray to this image', lambda: self.hello(url))

    def hello(self, icon_name):
        print 'Hello world!'
        self.parent.set_top_icon(icon_name)

    def download_favicon(self):
        import requests
        url = str(self.url.text())

        if not 'http' in url:
            url = 'http://' + url
        print 'Get favicon from %s' % url
        #icon_url = "http://www.google.com/s2/favicons?domain="

        icon_url = "http://g.etfv.co/"
        icon = requests.get(icon_url + url)

        _file = os.path.abspath(os.path.dirname(__file__))
        icon_file = _file + '/favicon-%s.ico' % str(self.url.text())
        with open(icon_file, 'wb') as new_icon:
            print 'Writing to file %s' % (icon_file)
            new_icon.write(icon.content)

        return self.read_icon_into_qicon(icon.content)

    def get_icon(self):
        return self.icon


class Indicatr(object):
    def __init__(self):
        self.app = QtGui.QApplication([])
        self.app.setApplicationName("TrAyPI")
        # Don't quit if a window get closed, remember, we're a tray-icon application!
        self.app.setQuitOnLastWindowClosed(False)
        self.top_icon = QtGui.QSystemTrayIcon()
        self.menu = QtGui.QMenu()
        # Add quit btn straight away
        self.add_quit_btn()

        self.icons = {}
        self.new_tray = SetupTrayWindow(parent=self)
        self.favicon = Favicon()

    def add_icon(self, file, name='filename'):
            pass

    def reset_menu(self):
        # del self.menu
        self.menu.clear()
        # self.top_icon.setContextMenu(self.menu)

    def change_icon(self, element, icon):
        element.setIcon(icon)
        try:
            element.show()
        except:
            pass

    def set_top_icon(self, icon):
        if not icon in self.icons:
            self.add_icon(icon)

        self.change_icon(self.top_icon, self.favicon.icons[icon])

    def add_icon_to_menu(self, icon_name, text, callback):
        return self.menu.addAction(self.favicon.icons[icon_name], text, callback)

    def add_to_menu(self, text, callback):
        return self.menu.addAction(text, callback)

    # def _show_tray_add(self):
    #     self.new_tray.raise_()
    #     self.new_tray.activateWindow()
    #     self.app.setActiveWindow(self.new_tray)
    #     self.app.restoreOverrideCursor()
    #     self.new_tray.show()

    def add_separator(self):
        self.menu.addSeparator()

    def add_quit_btn(self):
        # self.menu.addAction('Initialise API', self.init_api)
        # self.menu.addAction('New Tray App', self._show_tray_add)
        self.menu.addAction('Quit', self._quit)
        # self.menu.addSeparator()

    def _quit(self):
        # for icon in self.favicon.icons:
        #     print 'Should remove %s' % icon
        QtGui.QApplication.quit()

    def run(self):
        self.top_icon.show()
        self.top_icon.setContextMenu(self.menu)
        self.app.exec_()

    def hide_mac_dock_icon(self):
        try:
            import AppKit
            # https://developer.apple.com/library/mac/#documentation/AppKit/Reference/NSRunningApplication_Class/Reference/Reference.html
            NSApplicationActivationPolicyRegular = 0
            NSApplicationActivationPolicyAccessory = 1
            NSApplicationActivationPolicyProhibited = 2
            AppKit.NSApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)
        except:
            # Don't do anything if we can't remove dock icon...
            print 'Cant remove icon from dock. Install pyobjc to fix this'
            pass

if __name__ == '__main__':
    x = Indicatr()
    x.add_icon('apple.png')
    x.set_top_icon('apple')
    x.add_quit_btn()
    # x.cls_factory('Reddit')
    #x._show_tray_add()
    x.run()
