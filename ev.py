# @auth: Oliver Ruoff
# for better use, copy this script to e.g. /usr/local/ev.py
# and create (Unix) alias e.g. "alias ev='python /usr/local/ev.py"

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
# Defining the push the user is working on at the moment
curr_push = 0


def push(push_tag):
    # creates new push, including all entries in affected files.
    # if it is the first push, ev structure gets initialized
    # push tag is optional, if empty 'v<push_id>' is added after push_id
    # e.g.: 3 - v3
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
    curr_push = str(int(last_line.split()[0]) + 1)
    if push_tag == '*':
        push_tag = 'v' + curr_push
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
    write_curr_push(curr_push)

    # copy all files and folders excluding ignore_list to new folder
    for item in os.listdir(current_dir):
        if item not in ignore_list:
            if os.path.isfile(item):
                shutil.copyfile(current_dir+'/'+item, push_path+item)
            elif os.path.isdir(item):
                shutil.copytree(current_dir+'/'+item, push_path+item)

    # zip created directory
    shutil.make_archive(push_path, 'zip', push_path)
    # remove unzipped directory
    shutil.rmtree(push_path, ignore_errors=True)

    print('Pushed', push_map_string)


def pull(push_id):
    # loads a push with push_id to the working directory
    if not os.path.exists(ev_dir):
        print('There is no .ev file, initialize EzVersion by pushing.')
        return 0
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

    des_push_tup = [i for i in push_ids if push_id == i[0]][0]
    des_push_tag = des_push_tup[1]
    des_push_id = des_push_tup[0]

    desired_pull_dir = pushes_dir + des_push_tag

    # delete  files from current dir
    for item in os.listdir(current_dir):
        if item not in ignore_list:
            if os.path.isfile(item):
                os.unlink(current_dir+'/'+item)
            elif os.path.isdir(item):
                shutil.rmtree(current_dir+'/'+item, ignore_errors=True)

    # copy zip to working dir
    shutil.copy(desired_pull_dir, current_dir+'/'+des_push_tag)
    # extracting zip
    shutil.unpack_archive(current_dir+'/'+des_push_tag)
    # remove zip from working dir
    os.unlink(current_dir+'/'+des_push_tag)

    # updates .ev/.current_push file
    write_curr_push(des_push_id)

    print('Pulled push:', des_push_tag)


def status():
    # prints out the curent push, the user is working on atm
    print('Current push:', curr_push)


def back():
    # pulls one push before the current one if exists
    curr_push = get_curr_push()
    if int(curr_push) <= 0:
        print('You are on the first push, can\'t go back!')
        return 0
    pull(str(int(curr_push) - 1))


def forward():
    # pulls one push after the current one if exists
    if not os.path.exists(ev_dir):
        print('There is no .ev file, initialize EzVersion by pushing.')
        return 0
    curr_push = get_curr_push()
    if curr_push == read_last_line(map_path).split()[0]:
        print('You are on the latest push, can\'t go forward!')
        return 0
    elif curr_push > read_last_line(map_path).split()[0]:
        print('ERROR! The current push is newer than the latest one!' +
              ' This should never happen!')
    pull(str(int(curr_push)+1))


def latest():
    # pulls the latest push
    if not os.path.exists(ev_dir):
        print('There is no .ev file, initialize EzVersion by pushing.')
        return 0
    pull(read_last_line(map_path).split()[0])


def list_pushes():
    # prints out all pushes that were made
    if not os.path.exists(ev_dir):
        print('There is no .ev file, initialize EzVersion by pushing.')
        return 0
    print('Pushes:')
    print(''.join(read_file(map_path)))


def help():
    # prints out available commands and their descriptions
    print('push / ps <tag>	-	Creates new push with tag')
    print('pull / pl <tag>	-	Rerolls to specific push')
    print('status / st      -   Shows push user is on atm')
    print('list / ls        -   Lists all pushes')
    print('latest / la      -   Pulls the latest push')
    print('back / b         -   Pulls the push before the current one')
    print('forward / f      -   Pulls the push after the current one')
    print('help / h         -   Shows available commands')


def read_file(file):
    # reads file, saves each line as entry in list
    file_handle = open(file, "r")
    line_list = file_handle.readlines()
    file_handle.close()
    return line_list


def read_last_line(file):
    # reads and returns the last line of a file.
    # if file is empty, returns -1
    line_list = read_file(file)
    if len(line_list) > 0:
        return line_list[len(line_list)-1]
    else:
        return '-1'


def update_ignore_list():
    # reads .ev/.evignore and adds it to the internal ignore list
    global ignore_list
    # adding dirs / files to ignore from .evignore
    with open(evignore_path) as f:
        evignore_content = f.readlines()
    [ignore_list.append(
        x.strip()) for x in evignore_content]


def write_curr_push(curr_push):
    # writes an integer to the .ev/.curr_push file
    if os.path.exists(curr_push_path):
        with open(curr_push_path, 'w') as myfile:
            myfile.write(curr_push)
    else:
        print('There is no curr_push file, initialize EzVersion by pushing.')


def get_curr_push():
    # reads ./ev/.curr_push and sets 'curr_push' class var, also
    # returns it. returns '0' if .curr_push doesn't exist
    global curr_push
    if os.path.exists(curr_push_path):
        curr_push = read_file(curr_push_path)[0]
        return curr_push
    else:
        curr_push = '0'
        return '0'


# Starting point ------------------------------------
# loading current push to env
get_curr_push()

# handling arguments
for idx, arg in enumerate(sys.argv):
    if idx == 1:
        if arg == 'push' or arg == 'ps':
            if len(sys.argv) >= 3:
                push(sys.argv[idx+1])
            else:
                push('*')
        elif arg == 'pull' or arg == 'pl':
            if len(sys.argv) >= 3:
                pull(sys.argv[idx+1])
            else:
                print('3rd argument missing! Please enter tag to pull!')
        elif arg == 'help' or arg == 'h':
            help()
        elif arg == 'status' or arg == 'st':
            status()
        elif arg == 'list' or arg == 'ls':
            list_pushes()
        elif arg == 'latest' or arg == 'la':
            latest()
        elif arg == 'back' or arg == 'b':
            back()
        elif arg == 'forward' or arg == 'f':
            forward()
        else:
            print('Command not recognized! Available commands:')
            help()
