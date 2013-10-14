from __future__ import with_statement
from fabric.api import *
import fabric
from fabric.contrib.console import confirm
from version import VERSION
from name import NAME
import zipfile
import os
import sys

env.hosts = ['seastar']
env.user = 'thijs'


def increment_release(rel_type='patch', new_number=None):
    (major, minor, patch) = VERSION.split('.')
    if rel_type is 'minor':
        minor = int(minor)+1
    elif rel_type is 'major':
        major = int(major)+1
    else:
        # Increment patch by default or if unknown
        patch = int(patch)+1

    new_num = '{major}.{minor}.{patch}'.format(major=major, minor=minor, patch=patch)
    with open('version.py', 'w') as f:
        f.write("VERSION='%s'" % new_num)
    print 'New version is now: %s' % new_num
    return new_num


def remove_extra_pylib(file_name):
    dist_path = './dist/%s.zip' % file_name
    app_name = NAME


def put_nib_in_place(file_name):
    dist_path = './dist/%s.zip' % file_name
    app_name = NAME + '.app'
    #print dist_path
    ts = zipfile.ZipFile(dist_path, 'a')
    my_nib = '%s/Contents/Frameworks/QtGui.framework/Versions/4/Resources/qt_menu.nib' % app_name

    files_to_copy = []
    for item in ts.namelist():
        if my_nib in item:
            itm = item.split('/')[-1:][0]
            files_to_copy.append((itm, ts.read(item)))

    if len(files_to_copy) < 1:
        print 'Couldnt find files...'

    ts.writestr('%s/%s/%s/Contents/Resources/qt_menu.nib/readme.txt' % (app_name, file_name, app_name), 'Hackity-hack fabricstyle')
    for item, content in files_to_copy:
        #ugly, but works for now
        loc = '%s/%s/%s/Contents/Resources/qt_menu.nib/%s' % (app_name, file_name, app_name, item)
        ts.writestr(loc, content)

    #while we're at it, let's copy the images as well...
    images = [x for x in os.listdir('images') if not os.path.isfile(x)]
    for image in images:
        loc = '%s/%s/%s/Contents/Resources/images/%s' % (app_name, file_name, app_name, image)
        ts.writestr(loc, open('images/%s' % image).read())

    ts.close()
    return dist_path


def rebuild():
    local('python setup.py bdist_esky')
    file_name = fabric.operations.prompt('Copy the weird buildname plx: ')
    print
    print 'was it: %s' % file_name
    print
    if sys.platform.startswith('linux'):
        remove_extra_pylib(file_name)
    elif sys.platform is 'darwin':
        zip_file = put_nib_in_place(file_name)
    print 'All done!! Uploading time!'


def go(version='patch'):
    # Increment release number in version.py
    # increment_release(version)

    # Build package
    local('python setup.py bdist_esky')
    file_name = fabric.operations.prompt('Copy the weird buildname plx: ')
    print
    print 'was it: %s' % file_name
    print

    zip_file = put_nib_in_place(file_name)
    print 'All done!! Uploading time!'
    print zip_file
    deploy(zip_file)


def test():
    local('./manage.py test article')


def commit():
    local('git add -p && git commit')
    local('git pull')


def push():
    local('git push origin master')


def prepare_deploy():
    test()
    commit()
    push()


def deploy(dist_name):
    #prepare_deploy()
    # /opt/domains/kopjekoffie.eu/src/kopjekoffie/koffie/static/

    upload_dir = '/tmp/'
    with cd(upload_dir):
        put(dist_name, upload_dir, mode=0764)
        name = dist_name.split('/')[-1:][0]
        _cmd = 'chown www-data:www-data /tmp/{0}'.format(name)
        _cmd2 = 'mv /tmp/{0} /opt/domains/traypi.com/uploads/{1}'.format(name, name)
        _cmd3 = 'chmod 0764 /opt/domains/traypi.com/uploads/{0}'.format(name)
        sudo(_cmd)
        sudo(_cmd2)
        sudo(_cmd3)


def publish_site():
    site_dir = '/opt/domains/traypi.com/www/'
    with cd(site_dir):
        put('website/*', site_dir)
