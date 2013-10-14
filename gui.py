try:
    from PyQt4 import QtCore
    from PyQt4 import QtGui
except ImportError:
    try:
        from Qt import QtCore
        from Qt import QtGui
        print dir(QtGui)
    except Exception, e:
        raise e

import requests
# Enum from QAbstractItemView.SelectionMode
""" From: http://pyqt.sourceforge.net/Docs/PyQt4/qabstractitemview.html
    #SelectionMode-enum """
ABSTR_SELECTION_MODES = {
    """ When the user selects an item, any already-selected item becomes
         unselected, and the user cannot unselect the selected item by
         clicking on it. """
    'single': 1,

    """ When the user selects an item in the usual way, the selection status
         of that item is toggled and the other items are left alone. Multiple
         items can be toggled by dragging the mouse over them. """
    'multi':  2,

    """ item, the clicked item gets toggled and all other items are left
        untouched. If the user presses the Shift key while clicking on an
        item, all items between the current item and the clicked item are
        selected or unselected, depending on the state of the clicked item.
        Multiple items can be selected by dragging the mouse over them. """
    'extend': 3,

    """ When the user selects an item in the usual way, the selection is
        cleared and the new item selected. However, if the user presses the
        Shift key while clicking on an item, all items between the current
        item and the clicked item are selected or unselected, depending on
        the state of the clicked item. """
    'contig': 4

}
SELECTION_MODE_PROJECT_BOX = 2


class FilterBox(QtGui.QLineEdit):
    def __init__(self, parent=None, completion_set=[], *args, **kwargs):
        self.parent = parent
        self.completion_set = completion_set
        super(FilterBox, self).__init__(*args, **kwargs)

    def add_completion_set(self, new_set):
        self.completion_set = new_set

    def keyPressEvent(self, event):
        # First delegate to parent class
        QtGui.QLineEdit.keyPressEvent(self, event)

        something_changed = False
        new_items = []

        for item in self.completion_set:
            if not self.text() in item:
                continue

            something_changed = True if something_changed is False else True
            new_items.append(item)

        if something_changed:
            self.parent.projects_placeholder.clear()
            if new_items == []:
                # Take the old set if there's no matches
                new_items = self.completion_set

            self.parent.projects_placeholder.addItems(new_items)
            self.parent.selectProjects()


class JenkinsConfigWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(JenkinsConfigWindow, self).__init__()
        self.parent = parent
        self.setWindowTitle('Jenkins setup')
        self.overall_layout = QtGui.QGridLayout()
        self.inital_box = QtGui.QGroupBox("Jenkinz Settings")
        self.buttonLayout = QtGui.QVBoxLayout()

        self.url = QtGui.QLineEdit(self.parent.get_url())

        refresh_rate_text = str(self.parent.get_refresh_rate())
        self.refresh_rate = QtGui.QLineEdit(refresh_rate_text)

        QtCore.QObject.connect(
            self.url,
            QtCore.SIGNAL('returnPressed()'),
            self.get_projects
        )

        self.buttonLayout.addWidget(QtGui.QLabel('Jenkins url'))
        self.buttonLayout.addWidget(self.url)

        self.list_projects = QtGui.QPushButton("Refresh list")
        self.list_projects.clicked.connect(self.get_projects)
        self.buttonLayout.addWidget(self.list_projects)

        self.buttonLayout.addWidget(QtGui.QLabel('Refresh rate(seconds)'))
        self.buttonLayout.addWidget(self.refresh_rate)

        self.confirm = QtGui.QPushButton("&Confirm")
        self.confirm.clicked.connect(self.submit_form)

        self.project_box = QtGui.QGroupBox('Project list')
        self.project_layout = QtGui.QVBoxLayout()
        self.project_layout.addWidget(QtGui.QLabel('Filter'))

        self.projects_placeholder = QtGui.QListWidget()  # Need this for later.
        self.projects_placeholder.setSelectionMode(2)  # Multiselect-> http://pyqt.sourceforge.net/Docs/PyQt4/qabstractitemview.html#SelectionMode-enum

        self.filter_bar = FilterBox(parent=self)
        self.project_layout.addWidget(self.filter_bar)
        self.project_layout.addWidget(self.projects_placeholder)

        self.buttonLayout.addWidget(self.confirm)
        self.inital_box.setLayout(self.buttonLayout)
        self.project_box.setLayout(self.project_layout)

        self.overall_layout.addWidget(self.inital_box, 0, 0)
        self.overall_layout.addWidget(self.project_box, 0, 1)
        self.setLayout(self.overall_layout)

        if str(self.url.text()) != 'http://default':
            # default actions here
            self.get_projects()
            self.selectProjects()
        else:
            self.url.setFocus()
            self.url.selectAll()

    def selectProjects(self):
        for project in self.parent.get_important_projects():
            try:
                _pr = self.projects_placeholder.findItems(project, QtCore.Qt.MatchExactly)[0]
                _pr.setSelected(True)
            except Exception:
                # Just shut up if you can't find the project.
                pass

    def get_projects(self):
        url = str(self.url.text())
        try:
            json_url = '{0}/api/json?tree=jobs[name]'.format(url)
            posts = requests.get(json_url, timeout=self.parent.timeout).json()
        except Exception:
            posts = {'jobs': []}

        self.filter_bar.add_completion_set([p['name'] for p in posts['jobs']])
        self.project_list = QtCore.QStringList()
        for post in posts['jobs']:
            self.project_list.append(post['name'])

        self.projects_placeholder.clear()
        self.projects_placeholder.addItems(self.project_list)

    def submit_form(self):
        url = str(self.url.text())
        monitor_projects = [str(x.text()) for x in self.projects_placeholder.selectedItems()]

        if not monitor_projects:
            monitor_projects = self.parent.get_important_projects()

        self.close()
        self.parent.set_monitor_projects(monitor_projects)
        self.parent.set_url(url)
        self.parent.set_refresh_rate(self.refresh_rate.text())
        self.parent.refresh_now()
