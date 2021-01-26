# nemo-desktop-groups
Group files in Nemo based on file associations
Author: Sam Lane

Adds Nemo action to group / ungroup desktop items based on the app used to open the file

W-I-P: Use at your own risk.

Credits:<br>
This is based on:<br><br>
stacks-for-windows-linux<br>
by: Emilian Zawrotny<br>
https://github.com/SynneK1337/stacks-for-windows-linux<br>

and used with permission.
If modified or redistributed, please ensure this information stays intact.

to install:

`./install.sh`

This will add a right click option in Nemo file manager on the desktop to group / ungroup files.  Images, videos, and audio will be grouped in their respective folders.  The other files will be grouped according to the application used to open them.  The script attempts to guess the mime type using default libraries.  However, if python-magic is installed, it will increase the accuracy a bit.

To install python-magic:

`pip3 install python-magic`
