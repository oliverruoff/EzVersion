# @auth: Oliver Ruoff
# for better use, copy this script to e.g. /usr/local/ev.py
# and create alias e.g. "alias ev='python /usr/local/ev.py"

import sys
import os
import shutil

# paths to directories / files
current_dir = os.getcwd()
ev_dir = current_dir + '/.ev/'
pushes_dir = ev_dir + '/pushes/'
map_path = ev_dir + 'push_map'
evignore_path = ev_dir + '.evignore'


# list of directories / files that will be ignored by pushing
ignore_list = ['.ev', '.evignore']
# list of files to be created in .ev directory
create_list = [map_path, evignore_path]


def push(push_tag):
    # TODO: tag may not contain whitespaces! (cut them away)
    # TODO: with certain push_tag automatically generate unique push_tag
    # TODO: add .evignore functionality

    # adding dirs / files to ignore from .evignore
    with open(evignore_path) as f:
        evignore_content = f.readlines()
    evignore_content = [ignore_list.append(
        x.strip()) for x in evignore_content]

    # create (if not exists) .ev/
    if not os.path.exists(ev_dir):
        print('No .ev directory detected, creating one.')
        os.makedirs(pushes_dir)
        for f in create_list:
            with open(f, 'a'):
                os.utime(f, None)

    push_path = pushes_dir + push_tag + '/'

    # create new folder in .ev/ with unique ID (millisecs date sufficient?)
    while os.path.exists(push_path):
        push_tag = input(
            'Tag '+push_tag+' already exists! Enter new (unique) tag.>>')
        push_path = pushes_dir+push_tag+'/'
    os.makedirs(push_path)

    # copy all files and folders excluding ignore_list to new folder
    for item in os.listdir(current_dir):
        if item not in ignore_list:
            if os.path.isfile(item):
                shutil.copyfile(current_dir+'/'+item, push_path+item)
            elif os.path.isdir(item):
                shutil.copytree(current_dir+'/'+item, push_path+item)

    # create file in .ev/ to map push tag to date and push_id
    with open(map_path, 'a') as myfile:
        myfile.write(push_tag+'\n')

    print('Pushed \''+push_tag+'\'')


def pull(push_id):
    print('Pulling push id:', push_id)
    # search (if exists) in .ev/pushes/push_tag


def back():
    print('Going back to the last push!')  # TODO: Mention push_id
    # push tmp_current push (to jump back)
    # pull previous push


def curr():
    print('Reloading current push!')
    # pull tmp_current (created at back())


def list_pushes():
    print('Pushes:')
    # list all pushes chronically and with tag

# Lists all commands available


def help():
    print('push <tag>	-	Creates new push with tag')
    print('pull <tag>	-	Rerolls to specific push')
    # TODO: add all commands


for idx, arg in enumerate(sys.argv):
    if idx == 1:
        if arg == 'push':
            if len(sys.argv) >= 3:
                push(sys.argv[idx+1])
            else:
                print('3rd argument missing! Please enter tag!')

        elif arg == 'pull':
            if len(sys.argv) >= 3:
                pull(sys.argv[idx+1])

            else:
                print('3rd argument missing! Please enter tag to pull!')
        elif arg == 'help':
            help()
