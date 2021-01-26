#!/usr/bin/env python3

# stacks-for-budgie
# by Sam Lane

# Based on stacks-for-windows-linux
# by Emilian Zawrotny
# https://github.com/synnek1337/stacks-for-windows-linux

from gi.repository import GLib, Gio
import os
import pathlib
import subprocess
from sys import argv
import mimetypes

try:
    from magic import Magic
    USE_MAGIC = True
except ImportError:
    USE_MAGIC = False

OTHERS = 'Others'

# Use GLib User Dirs to translate
try:
    PICTURES = os.path.split(GLib.get_user_special_dir
                             (GLib.UserDirectory.DIRECTORY_PICTURES))[1]
    VIDEOS = os.path.split(GLib.get_user_special_dir
                           (GLib.UserDirectory.DIRECTORY_VIDEOS))[1]
    AUDIO = os.path.split(GLib.get_user_special_dir
                          (GLib.UserDirectory.DIRECTORY_MUSIC))[1]
    DOCS = os.path.split(GLib.get_user_special_dir
                         (GLib.UserDirectory.DIRECTORY_DOCUMENTS))[1]
except IndexError:
    PICTURES = 'Pictures'
    VIDEOS = 'Videos'
    AUDIO = 'Music'

TRANSLATE = { 'audio': AUDIO,
              'video': VIDEOS,
              'image': PICTURES}


def get_desktop_path():
    # Use GLib to get user Desktop folder, regardless of language
    try:
        desktop = (GLib.get_user_special_dir(
                       GLib.UserDirectory.DIRECTORY_DESKTOP))
    except GLib.GError:
        desktop = os.path.expanduser("~/Desktop")
    return desktop


def get_file_type(file, types):  # types = file_type_by_extension
    for type, extension in types.items():
        if pathlib.Path(file).suffix.lower() in extension:
            return type


def create_folders(types):     # types = file_type_by_extension
    for type_ in types:
        os.makedirs(type_, exist_ok=True)


def get_folders_to_unstack():
    folders = []
    for folder in [OTHERS, AUDIO, PICTURES, VIDEOS]:
        if os.path.isdir(folder):
            folders.append(folder)
    all_apps = get_all_installed()
    for app in all_apps:
        if os.path.isdir(app):
            folders.append(app)
    return folders


def get_all_installed():
   all_names = []
   all_apps = Gio.AppInfo.get_all()
   for app in all_apps:
       all_names.append(app.get_name())
   return all_names


def get_folder_name(filename):
    mime = mimetypes.guess_type(filename)[0]
    if mime is not None:
        category = mime.split('/')[0]
    elif USE_MAGIC:
        magic = Magic(mime=True)
        mime = magic.from_file(filename).split('/')[0]
        category = mime.split('/')[0]
    else:
        return OTHERS
    if category in ['audio','video','image']:
        return TRANSLATE[category]
    elif mime is not None:
        filetype = Gio.app_info_get_default_for_type(mime, False)
        if filetype == None:
            return OTHERS
        else:
            return filetype.get_name()
    else:
        return OTHERS

def get_folders_to_create():
    allfiles = os.listdir()
    all_types = []
    for file in allfiles:
        if not os.path.isdir(file):
            name = get_folder_name(file)
            if name not in all_types:
                all_types.append(name)
    return all_types

def stack():
    folders = get_folders_to_create()
    create_folders(folders)
    files = os.listdir()
    for file in files:
        if os.path.isfile(file):
            move_folder = get_folder_name(file)
            safe_move(file, os.path.join(move_folder, file))
    files = os.listdir()
    for folder in folders:
        if not os.listdir(folder):
            os.removedirs(folder)


def unstack():
    folders = get_folders_to_unstack()
    for folder_name in folders:
        try:
            os.chdir(folder_name)
        except FileNotFoundError:
            print(folder_name + " not found.")
        else:
            for file in os.listdir():
                safe_move(file, os.path.join('..', file))
            os.chdir('..')
            try:
                os.removedirs(folder_name)
            except OSError:
                print('Folder {} not empty'.format(folder_name))

def safe_move(oldfile, newfile):
    # Move the file, but rename instead if the file exists already
    if os.path.exists(newfile):
        newname = get_next_name(newfile)
    else:
        newname = newfile
    os.rename(oldfile, newname)


def has_count(filename):
    # Used to check if a filename already contains a count i.e. "file(1).ext"
    current = get_count_prefix(filename)[1]
    if current.isdigit():
        return True
    return False


def get_count_prefix(filename):
    # Gets the first part of filename if it has a count
    # i.e. "file(1).ext" will return "file" without the "(1)"
    base, ext = os.path.splitext(filename)
    if base[-1] == ")" and "(" in base:
        leftparen = base.rindex("(")
        rightparen = base.rindex(")")
        prefix = base[0:leftparen]
        current = base[leftparen+1:rightparen]
        return prefix, current
    else:
        return base, '0'


def get_next_name(filename):
    # Increments the file number until it finds one that doesn't exist
    base, ext = os.path.splitext(filename)
    if has_count(filename):
        base = get_count_prefix(filename)[0]
    i = 1
    testfile = '{}({}){}'.format(base, i, ext)
    while os.path.exists(testfile):
        i += 1
        testfile = '{}({}){}'.format(base, i, ext)
    return testfile


if __name__ == "__main__":

    os.chdir(get_desktop_path())
    if "--stack" in argv:
        stack()
    elif "--unstack" in argv:
        unstack()
    else:
        print("Error: Argument missing.")
