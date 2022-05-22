#!/usr/local/bin/python3

import sys
import os
import shutil
import yaml
import string
import random

chars_to_strip = [ ".", "_", "+", "-", "'", "," ]

def cleanup_dirs(path):
  # Create a List    
  listOfEmptyDirs = list()
  # Iterate over the directory tree and check if directory is empty.
  for (dirpath, dirnames, filenames) in os.walk(path):
      if len(dirnames) == 0 and len(filenames) == 0 :
          print ('Removing: ' + dirpath)
          os.rmdir(dirpath)

# build a list of fully qualified file names in a folder, recursive
def get_files_list(path):
  items = []
  for root,d_names,f_names in os.walk(path):
    for f in f_names:
      items.append(os.path.join(root, f))    

  if len(items) > 1:
    items.sort()

  return items

# build a dict of folder names as key, each with a blank list to hold fully qualified file names
def get_folders_list(path):
  folders = {}

  for file in os.listdir(path):
    d = os.path.join(path, file)
    if os.path.isdir(d):        
        folders[file] = []

  return folders

# replace chars_to_strip with a space
def strip_file_name(file_name):
  file_name = file_name.casefold()
  for item in chars_to_strip:
    file_name = file_name.replace(item, ' ')
  return file_name

def get_matches(folder_name, files_list):
  matched_files = []

  folder_strings = folder_name.split()
  
  for full_file_name in files_list:
    # strip out the file name since full_file_name is the fq path
    # file_name_strings = full_file_name.split('/')
    # file_name = file_name_strings[len(file_name_strings)-1]
    file_name = os.path.basename(full_file_name)
    result = inspect_file(folder_strings, file_name)

    if result != False:
      matched_files.append(full_file_name)
    
    # word_matches = 0
    # for word in folder_strings:
    #   # print('Checking: ' + word + ' -in- ' + folder_name)
    #   # strip out characters from folder name so they're not used for matching
    #   if word not in chars_to_strip:
    #     if word.casefold() in file_name.casefold():
    #       word_matches += 1

    #     if word_matches > 1:
    #       matched_files.append(full_file_name)
    #       break

  # print("-------")
  return matched_files

def inspect_file(folder_strings, file_name):
  trimmed_file_name = strip_file_name(file_name)

  # print('Stripped file name: ' + trimmed_file_name)
  file_name_strings = trimmed_file_name.split(' ')
  file_name_strings.pop(len(file_name_strings)-1)
  
  word_matches = 0

  # don't check the file extension to speed up operation
  # num_strings = len(file_name_strings) - 1
  # while num_strings > 0:
  #   num_strings -= 1

  # check the concat of index 1 + 2 first for a more exact match
  if len(folder_strings) > 1:
    first_two_strings = folder_strings[0].casefold() + folder_strings[1].casefold()
    first_two_with_space = folder_strings[0].casefold() + " " + folder_strings[1].casefold()
    if first_two_strings in file_name_strings or first_two_with_space in file_name_strings:
      return file_name

  # check each item from folder_Strings to see if it exists in file_name / file_name_strings
  for item in folder_strings:
    folder_name_part = item.casefold()
    if folder_name_part not in chars_to_strip and folder_name_part in file_name_strings:
      word_matches += 1
      # print('Folder word: ' + item)
      # print(file_name_strings)  

    if word_matches > 1:
      return file_name
  
  # if no matches are found..
  return False

def random_string_generator():
  allowed_chars = string.ascii_letters
  return ''.join(random.choice(allowed_chars) for x in range(6))
    
def move_files(target_path, files_list):
  for file_path in files_list:
    file_name_strings = file_path.split("/")
    file_name = file_name_strings[len(file_name_strings)-1]
    file_dest = target_path + "/" + file_name

    if os.path.isfile(file_dest):
      print('File already exists: '+ file_dest)
      src_file_size = os.path.getsize(file_path)
      dst_file_size = os.path.getsize(file_dest)
      if src_file_size == dst_file_size:
        print('Source and destination files are the same size, removing the source file.')
        try:
          os.remove(file_path)
        except:
          print('Unable to remove file: ' + file_path)
      else:
        print('Source and destination sizes differ, will rename when moving.')
        file_name_split = os.path.splitext(file_name)
        file_dest = target_path + "/" + file_name_split[0] + "-" + random_string_generator() + file_name_split[1]

    out_text = 'from: ' + file_path +' --- to: '+ file_dest

    # ensure file doesn't already exist
    if not os.path.isfile(file_dest):
      try:
        shutil.move(file_path, file_dest)
      except:
        print ('Unable to move ' + out_text)
      else:
        print ('Moved ' + out_text)

if __name__ == '__main__':
    num_args = len(sys.argv)
    print('Number of arguments:', num_args, 'arguments.')
    if num_args < 3:
      print('Incorrect number of args supplied. Must include <target path> followed by <path to files to move>.')
      print('Optional 3rd arg "move" will move the files. Default is to print only in yaml format.')
      print('Argument List:', str(sys.argv))
      quit()

    folders_path = sys.argv[1]
    files_path = sys.argv[2]

    do_move = False
    if num_args == 4 and sys.argv[3] == 'move':
      do_move = True

    items = get_folders_list(folders_path)
    files_list = get_files_list(files_path)

    # print(items)
    # print("-------")
    # print(files_list)
    # print("-------")

    for folder in list(items):
      files = get_matches(folder, files_list)
      if len(files) > 0:
        items[folder] = files
      else:
        # remove folder names with emtpy file lists for easier reading / faster processing
        del(items[folder])

    # print the yaml list of matches
    print(yaml.dump(items))

    # print total files to be moved
    file_count = 0
    for folder in sorted(items):
      print('Folder: ' + folder)
      for file in items[folder]:
        print('File: ' + os.path.basename(file))
        file_count += 1
      print("----------------------------")

    # print("----------------------------")
    print('Files to be moved:')
    print(file_count)



    if do_move == True:
      print('Moving files..')
      for folder, files in items.items():
        move_files(folders_path + "/" + folder, items[folder])
      print('Cleaning up empty folders..')
      cleanup_dirs(files_path)
    else:
      print('Not moving files.')
      print(do_move)

