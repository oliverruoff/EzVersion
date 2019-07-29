# EzVersion
A very simple local versioning system for any files or directories. :)
Copies all files of the current directory, zips them and maps them to a tag.
 
EzVersion is not meant to be a replacement for git, but it's meant to be a very simple,
easy to use and lightweight tool to document changes of any kind of folder structure or of
just a file (without having the repository overhead)
 
Stop adding "very_final_last_rework_99999" to your file endings and start using EzVersion :D
 
## Structure
- [EzVersion](#ezversion)
- [Structure](#structure)
- [Requirements](#requirements)
- [How it works](#how-it-works)
- [Commands](#commands)
 
## Requirements
 
- Pyhton 3 installed
 
## How it works
 
Download the ev.py file from this repository and save it to the folder you want to versionate.
To initialize EzVersion, open a shell within your folder and execute `python ev.py push <any_push_message_without_blanks>`.
This generates a push with the push id 0 and links it with your push message.
Now you can work on the files within your folder and do a `python ev.py push <any_push_message_without_blanks>` whenever you like
to save an intermediate state of your folder. This will generate pushes with ascending push ids.
To jump to a specific push, simply use the 'pull' command and provide a push id to jump to.
E.g.: `python ev.py pull 2`.
To see which push ids exist (and thus, which pushes exist), use: `python ev.py list` to list pushes.
For all available commands, see section [Commands](#commands) below.
 
*Tip: For more convenience, use alias or other tools of your operating system to make pushing and pulling etc. more comfortable.
Additionally, you can use shortcuts etc. to link to ev.py, so that it is not necessary anymore to
locate the ev.py script in every folder you like to versionate, but only in one central place of your system.*
 
## Commands
 
|Command|Shortcut|Description|
|---|---|---|
|push <tag>|ps <tag>|Creates new push with tag|
|pull <id>|pl <id>|Rerolls to specific push|
|status|st|Shows push, user is working on at the moment|
|list|ls|Lists all pushes|
|latest|la|Pulls the latest push|
|back|b|Pulls the push before the one, the user is currently working on|
|forward|f|Pulls the push after the one, the user is currently working on|
|help|h|Shows available commands|
