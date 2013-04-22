try:
    from PyQt4 import QtGui
except ImportError:
    try:
        from Qt import QtGui
    except Exception, e:
        raise e

try:
    import AppKit as ak
except:
    ak = None
    pass


class Indicatr(object):
    def __init__(self, application=None):
        if application is None:
            application = QtGui.QApplication([])
        self.app = application
        self.top_icon = QtGui.QSystemTrayIcon()

        # The important part: the menu itself.
        self.menu = QtGui.QMenu()

        self.icons = {}

    def reset_menu(self):
        self.menu.clear()

    def change_icon(self, element, icon):
        element.setIcon(icon)
        try:
            element.show()
        except:
            pass

    def add_icon_to_menu(self, icon, text, callback):
        return self.menu.addAction(icon, text, callback)

    def add_to_menu(self, text, callback):
        return self.menu.addAction(text, callback)

    def add_separator(self):
        self.menu.addSeparator()

    def init_top_icon(self):
        self.top_icon.show()
        self.top_icon.setContextMenu(self.menu)

    def hide_mac_dock_icon(self):
        if not ak:
            return
        # https://developer.apple.com/library/mac/#documentation/AppKit/Reference/NSRunningApplication_Class/Reference/Reference.html
        NSApplicationActivationPolicyAccessory = 1
        ak.NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
