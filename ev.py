# @auth: Oliver Ruoff
# for better use, copy this script to e.g. /usr/local/ev.py
# and create (Unix) alias e.g. "alias ev='python /usr/local/ev.py"

import sys
import os
import shutil

# paths to directories / files
CURRENT_DIR = os.getcwd()
EV_DIR = os.path.join(CURRENT_DIR, '.ev')
PUSHES_DIR = os.path.join(EV_DIR, 'pushes')
MAP_PATH = os.path.join(EV_DIR, '.push_map')
EVIGNORE_PATH = os.path.join(EV_DIR, '.evignore')
CURR_PUSH_PATH = os.path.join(EV_DIR, '.curr_push')

# list of directories / files that will be ignored by pushing
IGNORE_LIST = ['.ev', '.evignore']
# list of files to be created in .ev directory
CREATE_LIST = [MAP_PATH, EVIGNORE_PATH, CURR_PUSH_PATH]
# Defining the push the user is working on at the moment
CURR_PUSH = 0


def push(push_tag):
    '''creates new push, including all entries in affected files.
    if it is the first push, ev structure gets initialized
    push tag is optional, if empty 'v<push_id>' is added after push_id
    e.g.: 3 - v3

    Arguments:
        push_tag {String} -- Name of push
    '''
    global CURR_PUSH
    global IGNORE_LIST

    # create (if not exists) .ev/
    if not os.path.exists(EV_DIR):
        print('No .ev directory detected, creating one.')
        os.makedirs(PUSHES_DIR)
        for f in CREATE_LIST:
            with open(f, 'a'):
                os.utime(f, None)

    # getting new push id
    last_line = read_last_line(MAP_PATH)
    CURR_PUSH = str(int(last_line.split()[0]) + 1)
    if push_tag == '*':
        push_tag = 'v' + CURR_PUSH
    push_map_string = CURR_PUSH + ' - ' + push_tag + '\n'

    push_path = os.path.join(PUSHES_DIR, CURR_PUSH + ' - ' + push_tag)

    update_ignore_list()

    # create new folder in .ev/ with unique ID
    while os.path.exists(push_path):
        push_tag = input(
            'Tag '+push_tag+' already exists! Enter new (unique) tag.>>')
        push_path = os.path.join(PUSHES_DIR, push_tag)
    os.makedirs(push_path)

    # create file in .ev/.push_map to map push tag to date and push_id
    # appending new push to map
    with open(MAP_PATH, 'a') as myfile:
        myfile.write(push_map_string)
    # switching current push
    write_curr_push(CURR_PUSH)

    # copy all files and folders excluding IGNORE_LIST to new folder
    for item in os.listdir(CURRENT_DIR):
        if item not in IGNORE_LIST:
            if os.path.isfile(item):
                shutil.copyfile(os.path.join(
                    CURRENT_DIR, item), os.path.join(push_path, item))
            elif os.path.isdir(item):
                shutil.copytree(os.path.join(
                    CURRENT_DIR, item), os.path.join(push_path, item))

    # zip created directory
    shutil.make_archive(push_path, 'zip', push_path)
    # remove unzipped directory
    shutil.rmtree(push_path, ignore_errors=True)

    print('Pushed', push_map_string)


def pull(push_id):
    '''loads a push with push_id to the working directory

    Arguments:
        push_id {Integer} -- Id of a push

    Returns:
        Integer -- 1 if no .ev folder found
                     2 if no pushes found
                     3 if certain push id not found
    '''
    if not os.path.exists(EV_DIR):
        print('There is no .ev file, initialize EzVersion by pushing.')
        return 1
    global IGNORE_LIST
    update_ignore_list()

    # check if push path exists
    if not os.path.exists(PUSHES_DIR) or len(os.listdir(PUSHES_DIR)) < 1:
        print('No pushes found! Please use ev push ' +
              '<tag> to initialize EzVersion.')
        return 2
    push_ids = [(i.split()[0], i) for i in os.listdir(PUSHES_DIR)]
    # check if certain push exists
    if push_id not in [i[0] for i in push_ids]:
        print('Push id', push_id, 'does not exist!')
        return 3

    des_push_tup = [i for i in push_ids if push_id == i[0]][0]
    des_push_tag = des_push_tup[1]
    des_push_id = des_push_tup[0]

    desired_pull_dir = PUSHES_DIR + os.sep + des_push_tag

    # delete  files from current dir
    for item in os.listdir(CURRENT_DIR):
        if item not in IGNORE_LIST:
            if os.path.isfile(item):
                os.unlink(os.path.join(CURRENT_DIR, item))
            elif os.path.isdir(item):
                shutil.rmtree(os.path.join(CURRENT_DIR, item),
                              ignore_errors=True)

    # copy zip to working dir
    shutil.copyfile(desired_pull_dir, os.path.join(CURRENT_DIR, des_push_tag))
    # extracting zip
    shutil.unpack_archive(os.path.join(CURRENT_DIR, des_push_tag))
    # remove zip from working dir
    os.unlink(os.path.join(CURRENT_DIR, des_push_tag))

    # updates .ev/.current_push file
    write_curr_push(des_push_id)

    print('Pulled push:', des_push_tag)


def status():
    '''prints out the curent push, the user is working on atm
    '''
    print('Current push:', CURR_PUSH)


def back():
    '''pulls one push before the current one if exists

    Returns:
        Integer -- 0 if user is on the first push and can't go back
    '''
    CURR_PUSH = get_curr_push()
    if int(CURR_PUSH) <= 0:
        print('You are on the first push, can\'t go back!')
        return 0
    pull(str(int(CURR_PUSH) - 1))


def forward():
    '''pulls one push after the current one, if exists

    Returns:
        Integer -- 0 if there is no .ev folder
                   1 if user is on the latest push and can't go any further
    '''
    if not os.path.exists(EV_DIR):
        print('There is no .ev file, initialize EzVersion by pushing.')
        return 0
    CURR_PUSH = get_curr_push()
    if CURR_PUSH == read_last_line(MAP_PATH).split()[0]:
        print('You are on the latest push, can\'t go forward!')
        return 1
    elif CURR_PUSH > read_last_line(MAP_PATH).split()[0]:
        print('ERROR! The current push is newer than the latest one!' +
              ' This should never happen!')
    pull(str(int(CURR_PUSH)+1))


def latest():
    '''pulls the latest push

    Returns:
        Integer -- 0 if no .ev folder exists
    '''
    if not os.path.exists(EV_DIR):
        print('There is no .ev file, initialize EzVersion by pushing.')
        return 0
    pull(read_last_line(MAP_PATH).split()[0])


def list_pushes():
    '''Prints out all pushes that have been made

    Returns:
        Integer -- 0 if no .ev folder exists
    '''
    if not os.path.exists(EV_DIR):
        print('There is no .ev file, initialize EzVersion by pushing.')
        return 0
    print('Pushes:')
    print(''.join(read_file(MAP_PATH)))


def help():
    '''Prints out all available comamnds and their descriptions
    '''
    print('push / ps <tag>	-	Creates new push with tag')
    print('pull / pl <tag>	-	Rerolls to specific push')
    print('status / st      -   Shows push user is on atm')
    print('list / ls        -   Lists all pushes')
    print('latest / la      -   Pulls the latest push')
    print('back / b         -   Pulls the push before the current one')
    print('forward / f      -   Pulls the push after the current one')
    print('help / h         -   Shows available commands')


def read_file(file):
    '''Reads file, saves each line as entry in list

    Arguments:
        file {String} -- name of file

    Returns:
        list -- list that contains each line of file as entry
    '''
    file_handle = open(file, "r")
    line_list = file_handle.readlines()
    file_handle.close()
    return line_list


def read_last_line(file):
    '''Reads and returns the last line of a file.
    If file is empty, returs -1.

    Arguments:
        file {String} -- name of file

    Returns:
        String -- Last line of a file
    '''
    line_list = read_file(file)
    if len(line_list) > 0:
        return line_list[len(line_list)-1]
    else:
        return '-1'


def update_ignore_list():
    '''reads .ev/.evignore and adds it to the internal ignore list
    '''
    global IGNORE_LIST
    # adding dirs / files to ignore from .evignore
    with open(EVIGNORE_PATH) as f:
        evignore_content = f.readlines()
    [IGNORE_LIST.append(
        x.strip()) for x in evignore_content]


def write_curr_push(CURR_PUSH):
    '''writes an integer to the .ev/.CURR_PUSH file

    Arguments:
        CURR_PUSH {Integer} -- If of the current push
    '''
    if os.path.exists(CURR_PUSH_PATH):
        with open(CURR_PUSH_PATH, 'w') as myfile:
            myfile.write(CURR_PUSH)
    else:
        print('There is no CURR_PUSH file, initialize EzVersion by pushing.')


def get_curr_push():
    '''reads ./ev/.CURR_PUSH and sets 'CURR_PUSH' class var, also
    returns it. returns '0' if .CURR_PUSH doesn't exist

    Returns:
        Integer -- Current push id, or 0, if .CURR_PUSH doesn't exist
    '''
    global CURR_PUSH
    if os.path.exists(CURR_PUSH_PATH):
        CURR_PUSH = read_file(CURR_PUSH_PATH)[0]
        return CURR_PUSH
    else:
        CURR_PUSH = '0'
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
