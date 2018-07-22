# @auth: Oliver Ruoff
# for better use, copy this script to e.g. /usr/local/ev.py
# and create alias e.g. "alias ev='python /usr/local/ev.py"

import sys
import os
import shutil

# paths to directories / files
current_dir = os.getcwd()
ev_dir = current_dir + '/.ev/'
pushes_dir = ev_dir + 'pushes/'
map_path = ev_dir + '.push_map'
evignore_path = ev_dir + '.evignore'
curr_push_path = ev_dir + '.curr_push'

# list of directories / files that will be ignored by pushing
ignore_list = ['.ev', '.evignore']
# list of files to be created in .ev directory
create_list = [map_path, evignore_path, curr_push_path]


def push(push_tag):
    # TODO: tag may not contain whitespaces! (cut them away)
    # TODO: with certain push_tag automatically generate unique push_tag
    # TODO: Add compression instead of simply copying files

    global curr_push
    global ignore_list

    # create (if not exists) .ev/
    if not os.path.exists(ev_dir):
        print('No .ev directory detected, creating one.')
        os.makedirs(pushes_dir)
        for f in create_list:
            with open(f, 'a'):
                os.utime(f, None)

    # getting new push id
    last_line = read_last_line(map_path)
    if last_line == 0:
        push_map_string = '0 - ' + push_tag + '\n'
    else:
        curr_push = str(int(last_line.split()[0]) + 1)
        push_map_string = curr_push + ' - ' + push_tag + '\n'

    push_path = pushes_dir + curr_push + ' - ' + push_tag + '/'

    update_ignore_list()

    # create new folder in .ev/ with unique ID
    while os.path.exists(push_path):
        push_tag = input(
            'Tag '+push_tag+' already exists! Enter new (unique) tag.>>')
        push_path = pushes_dir+push_tag+'/'
    os.makedirs(push_path)

    # create file in .ev/.push_map to map push tag to date and push_id
    # appending new push to map
    with open(map_path, 'a') as myfile:
        myfile.write(push_map_string)
    # switching current push
    with open(curr_push_path, 'w') as myfile:
        myfile.write(curr_push)

    # copy all files and folders excluding ignore_list to new folder
    for item in os.listdir(current_dir):
        if item not in ignore_list:
            if os.path.isfile(item):
                shutil.copyfile(current_dir+'/'+item, push_path+item)
            elif os.path.isdir(item):
                shutil.copytree(current_dir+'/'+item, push_path+item)

    print('Pushed', push_map_string)


def pull(push_id):

    global ignore_list
    update_ignore_list()

    # check if push path exists
    if not os.path.exists(pushes_dir) or len(os.listdir(pushes_dir)) < 1:
        print('No pushes found! Please use ev push ' +
              '<tag> to initialize EzVersion.')
        return 0
    push_ids = [(i.split()[0], i) for i in os.listdir(pushes_dir)]
    # check if certain push exists
    if push_id not in [i[0] for i in push_ids]:
        print('Push id', push_id, 'does not exist!')
        return 0

    desired_pull_dir = pushes_dir + \
        [i[1] for i in push_ids if push_id == i[0]][0]

    # delete  files from current dir
    print(os.listdir(current_dir))
    print(ignore_list)
    for item in os.listdir(current_dir):
        if item not in ignore_list:
            if os.path.isfile(item):
                os.unlink(current_dir+'/'+item)
            elif os.path.isdir(item):
                shutil.rmtree(current_dir+'/'+item)

    # copy desired push to working directory
    print('desired pull directory:', desired_pull_dir)
    print('files:', os.listdir(desired_pull_dir))
    for item in os.listdir(desired_pull_dir):
        if os.path.isfile(item):
            shutil.copyfile(desired_pull_dir+'/'+item, current_dir+item)
        elif os.path.isdir(item):
            shutil.copytree(desired_pull_dir+'/'+item, current_dir+item)

    print('Desired push path:', desired_pull_dir)

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
    print('push / ps <tag>	-	Creates new push with tag')
    print('pull / pl <tag>	-	Rerolls to specific push')
    # TODO: add all commands


def read_file(file):
    file_handle = open(file, "r")
    line_list = file_handle.readlines()
    file_handle.close()
    return line_list


def read_last_line(file):
    line_list = read_file(file)
    if len(line_list) > 0:
        return line_list[len(line_list)-1]
    else:
        return 0


def update_ignore_list():
    global ignore_list
    # adding dirs / files to ignore from .evignore
    with open(evignore_path) as f:
        evignore_content = f.readlines()
    [ignore_list.append(
        x.strip()) for x in evignore_content]


def status():
    print('Current push:', curr_push)

# Starting point ------------------------------------


# the push number the user is currently working on
if os.path.exists(curr_push_path):
    curr_push = read_file(curr_push_path)[0]
else:
    curr_push = '0'

for idx, arg in enumerate(sys.argv):
    if idx == 1:
        if arg == 'push' or 'ps':
            if len(sys.argv) >= 3:
                push(sys.argv[idx+1])
            else:
                print('3rd argument missing! Please enter tag!')

        elif arg == 'pull' or 'pl':
            if len(sys.argv) >= 3:
                pull(sys.argv[idx+1])

            else:
                print('3rd argument missing! Please enter tag to pull!')
        elif arg == 'help':
            help()
        elif arg == 'status':
            status()
        else:
            print('Command not recognized! Listing available commands:')
            help()
