import requests
import qtray as indicate

import os
import sys
import gui
import errno
import ConfigParser
import notifier
# import notifier2

try:
    import Foundation as FND
except ImportError:
    FND = None

# TODO FIX THIS SHIT
try:
    from PyQt4.QtCore import QTimer, QObject, SIGNAL
    from PyQt4.QtGui import QIcon, QApplication, QMessageBox
except ImportError:
    try:
        from Qt.QtGui import QIcon, QApplication, QMessageBox
        from Qt.QtCore import QTimer, QObject, SIGNAL

        # from Qt import (QtCore, QtGui)
    except Exception, e:
        raise e

from math import floor as math_floor
import version
DEBUG = False
PROJECT_LINK = "http://www.traypi.com"
INSTALL_STARTUP_APP_CMD = """
osascript<<END\n
tell application "Finder"\n
\tset thePath to (POSIX path of (path to application "jenkinz"))\n
end tell\n
tell application "System Events"\n
\tmake login item at end with properties {path:thePath, name:"jenkinz", hidden:true}\n
end tell\n
END
"""


class JenkinsConfig(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.settings = {}
        self.config_section = 'general'.capitalize()
        self._url_flag_read = 0
        self.default_url = 'http://default'
        # if not self.read_last_url():
        #     self.url = 'http://localhost'
        self.icon_map = ['red', 'green', 'blue', 'grey', 'rain', 'default']

        #self.score_map = {20: 'red', 40: 'rain', 60: 'grey', 80: 'green', 100: 'blue', 0: 'red', 'default': 'default'}
        #self.reverse_score_map = {'red': 20, 'rain': 40, 'grey': 60, 'green': 80, 'blue': 100, 'default': 'default'}
        self.new_score_map = {
            20: 'red',
            40: 'rain',
            60: 'grey',
            80: 'green',
            100: 'blue',
            0: 'red',
            'default': 'default'}

        self.colors = ['blue', 'yellow', 'red', 'grey']

        self.new_reverse_score_map = dict(zip(self.new_score_map.values(), self.new_score_map.keys()))

        self.score_map = {20: 'red', 40: 'rain', 60: 'grey', 80: 'green', 100: 'blue', 0: 'red', 'default': 'default'}
        self.reverse_score_map = {'red': 20, 'rain': 40, 'grey': 60, 'green': 80, 'blue': 100, 'default': 'default'}

        self.refresh_rate = 60
        self.micro_rate = self.calc_refresh_rate()
        self.timeout = 2
        self.conf_file = os.path.expanduser(os.path.join('~', '.config', 'jenkinz', 'jenkinz.conf'))
        self.conf_folder = os.path.expanduser(os.path.join('~', '.config', 'jenkinz'))
        self._conf = ConfigParser.ConfigParser()
        # TODO: only do this when necessary
        self.create_conf_dir()
        self.read_config()

        for project in self.get_important_projects():
            self.parent.important_projects[project] = {}

    def get_url(self):
        return self.settings[self.config_section]['url']

    def calc_refresh_rate(self):
        return self.refresh_rate * 1000

    def set_monitor_projects(self, monitor_projects):
        self.settings[self.config_section]['monitor_projects'] = monitor_projects
        for project in self.get_important_projects():
            self.parent.important_projects[project] = {}

    def needs_configuration(self):
        # return True  # for now
        return True if self.settings[self.config_section]['url'] is self.default_url else False

    def create_conf_dir(self):
        try:
            os.makedirs(self.conf_folder)
        except OSError as err:
            if err.errno != errno.EEXIST:
                # TODO: visual feedback
                raise Exception('Problem with writing config')

    def read_config(self):
        opened_files = self._conf.read(self.conf_file)
        if not len(opened_files):
            #touch file for writing later(when we quit)
            try:
                fh = open(self.conf_file, 'w+')
                fh.close()
                os.chmod(self.conf_file, 0600)
            except IOError:
                # TODO visual feedback
                raise Exception('Cant write to conf file')
        else:
            # Settings are there, just read them.
            self.absorb_config()

    def set_default_settings(self):
        self.settings[self.config_section] = {}
        self.settings[self.config_section]['url'] = self.default_url
        self.settings[self.config_section]['refresh_rate'] = 60
        self.settings[self.config_section]['notification_sound'] = 1
        self.settings[self.config_section]['monitor_projects'] = []

    def absorb_config(self):
        if not len(self._conf.sections()):
            return self.set_default_settings()

        for section in self._conf.sections():
            # TODO probably fix the section loop sometime....
            # By adding configparser dict thingey
            self.settings[self.config_section] = dict(self._conf.items(section))
            for key in self.settings[self.config_section]:
                # Read if there are arrays...
                x = self.settings[self.config_section][key].split(',')
                if len(x) <= 1:
                    continue

                self.settings[self.config_section][key] = self.settings[self.config_section][key].split(',')

    def _write_conf(self):
        del self._conf
        self._conf = ConfigParser.ConfigParser()
        for section in self.settings.keys():
            self._conf.add_section(section.capitalize())
            for val in self.settings[section]:
                if type(self.settings[section][val]) == list:
                    self.settings[section][val] = ','.join(self.settings[section][val])  # hack the list.
                self._conf.set(section, val, self.settings[section][val])

        with open(self.conf_file, 'w') as config_file:
            self._conf.write(config_file)

    def set_url(self, url):
        self.settings[self.config_section]['url'] = url

    def set_refresh_rate(self, rate):
        self.refresh_rate = int(rate)
        self.micro_rate = self.calc_refresh_rate()

    def get_raw_refresh_rate(self):
        return self.micro_rate

    def get_refresh_rate(self):
        return self.settings[self.config_section]['refresh_rate']

    def refresh_now(self):
        self.parent.renew_entries()

    def get_important_projects(self):
        return self.settings[self.config_section]['monitor_projects']


class Jenkins(object):
    def __init__(self, *args, **kwargs):
        super(Jenkins, self).__init__(*args, **kwargs)
        self.app = QApplication([])
        self.important_projects = {}

        # Don't quit if a window get closed, remember, we're a tray-icon application!
        self.app.setQuitOnLastWindowClosed(False)
        self.config = JenkinsConfig(parent=self)

        # Let parent be in control of the menu, I just need my jenkins logic.
        self.parent = indicate.Indicatr(application=self.app)

        self.icons = {}
        self.items = {}

        self.jenkinswindow = None

        self._top_icon = 'default'
        self.init_icons()
        self.parent.change_icon(self.parent.top_icon, self.icons[self._top_icon])

        self.refresh_timer = QTimer()
        QObject.connect(self.refresh_timer, SIGNAL("timeout()"), self.renew_entries)

    def show_config_window(self):
        if self.jenkinswindow is None:
            self.jenkinswindow = gui.JenkinsConfigWindow(parent=self.config)
        self.jenkinswindow.show()
        self.jenkinswindow.raise_()

    def add_refresh_btn(self):
        self.parent.add_to_menu('Refresh now', self.renew_entries)

    def _change_top(self, icon_name):
        if icon_name == self._top_icon:
            return

        self.parent.change_icon(self.parent.top_icon, self.icons[icon_name])
        self._top_icon = icon_name

    def init_icon_colors(self, name):
        for color in self.config.colors:
            if name is 'default':
                continue
            colored_name = name + "-" + color
            self.icons[colored_name] = QIcon(os.path.abspath('images/health_%s' % colored_name))

    def init_icons(self):
        for name in self.config.icon_map:
            self.icons[name] = QIcon(os.path.abspath('images/health_%s' % name))
            self.init_icon_colors(name)

    def set_url(self, url):
        self.config.set_url(url)

    def click_link(self, link):
        os.system('open %s' % link)

    def process_item(self, item, url, img, long_text=None):
        image = self.icons[img]
        if not long_text:
            long_text = item

        action = self.parent.add_icon_to_menu(
            image,
            item,
            lambda: self.click_link(url)
        )
        action.setToolTip(long_text)
        return action

    def dertermine_top_icon(self):
        if not self.items:
            self._change_top('default')
            return

        total = 0
        num_items = len(self.items)
        for i, _item in enumerate(self.items):
            # Use first 'icon' for the top icon(so no last_build indicator)
            item = self.items[_item].split('-')[0]
            if 'default' is self.config.reverse_score_map[item]:
                continue
            total += self.config.reverse_score_map[item]

        end = int(math_floor(total / num_items))
        icon = end / 20 * 20
        self._change_top(self.config.score_map[icon])

    def add_to_startup(self):
        import subprocess
        x = subprocess.call(INSTALL_STARTUP_APP_CMD, shell=True)
        # os.system(INSTALL_STARTUP_APP_CMD)

        z = QMessageBox()
        z.setText("All done. I'll start the next time you reboot!")
        z.exec_()

    def add_settings(self):
        # These entries go in the submenu
        self.parent.add_to_settings('&About', lambda: self.click_link(PROJECT_LINK))
        self.parent.add_to_settings('&Configure', self.show_config_window)
        # self.parent.add_to_settings('&Add to Startup programs', self.add_to_startup)
        self.parent.add_to_settings('Version: %s' % version.VERSION, self.renew_entries)
        self.parent.add_settings_separator()
        self.parent.add_to_settings('Quit', self._quit)
        self.parent.add_setting_submenu()

    def renew_entries(self):
        self.parent.reset_menu()
        self.add_settings()
        # Keep this item here?
        self.parent.add_to_menu('Refresh now', self.renew_entries)
        self.parent.add_separator()

        self.get_projects()

        self.dertermine_top_icon()
        self.refresh_timer.start(self.config.get_raw_refresh_rate())

    def round_for_map(self, number):
        _t = number / 20 * 20
        return _t

    def handle_jenkins_report(self, report, post):
        score = self.round_for_map(report['score'])
        img = self.config.score_map[score]
        url = str(post['url'])
        name = str(post['name'])

        last_build = str(post['color'])

        if last_build in ['aborted', 'disabled']:
            last_build = 'grey'

        ''' Just 'disable' the build if it's in building(animated),
        or any other weird states... '''
        if last_build not in self.config.colors:
            last_build = 'grey'

        img += '-' + last_build
        if len([x for x in self.important_projects if x == name]) == 1:
            try:
                if self.important_projects[name]['current_state'] > report['score']:
                    heading = "{name} score lowered".format(name=name)
                    content = "Went from {prev} to {new}".format(prev=self.important_projects[name]['current_state'], new=report['score'])
                    final_note = "You might want to check on it"
                    notifier.notify(heading, content, final_note, sound=True, userInfo={"action": "open_url", "value": url})

                    # Set new score, so there's no spam in the future
                    self.important_projects[name]['current_state'] = report['score']
                    # self.notifier.notify(name, "Score lowered!!", "You might want to take action", sound=True)
                    # print 'NOTIFY!'
            except KeyError:
                # Create state if we haven't got it
                self.important_projects[name]['current_state'] = report['score']

        self.items[name] = img
        descr = str(report['description'])

        return self.process_item(name, url, img, descr)

    def handle_post(self, post):
        # There should be a better way to do this...
        x = [self.handle_jenkins_report(b, post) for
             b in post['healthReport']
             if str(b['description']).startswith('Build stability')
             ]
        if len(x) < 1:
            return None

        return x[0]

    def get_projects(self):
        self.items = {}
        try:
            json_url = '{0}/api/json?tree=jobs[name,url,color,healthReport[description,score,iconUrl]]'.format(self.config.get_url())
            posts = requests.get(json_url, timeout=self.config.timeout).json()
        except Exception:
            if DEBUG:
                import json
                posts = json.loads(open('fakedata.json', 'r').read())
            else:
                posts = {'jobs': []}

        for post in posts['jobs']:
            self.handle_post(post)

    def _quit(self):
        if not DEBUG:
            # No need to override config for debug purposes.
            self.config._write_conf()
        QApplication.quit()

    def run(self):
        if self.config.needs_configuration():
            self.show_config_window()

        self.renew_entries()
        self.parent.init_top_icon()

        self.app.exec_()

if __name__ == '__main__':
    if 'debug' in sys.argv:
        DEBUG = True

    r = Jenkins()
    r.run()
