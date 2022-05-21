#!/bin/bash
rm -rf ./test/*

FILES_PATH=./test/files
mkdir "$FILES_PATH"
touch "$FILES_PATH/joe bob.txt"
touch "$FILES_PATH/bob smith.txt"
touch "$FILES_PATH/Bob test Smith.txt"
touch "$FILES_PATH/bob smith_1234.txt"
touch "$FILES_PATH/chris dieh.blahl"
touch "$FILES_PATH/another test.sum"


FOLDERS_PATH=./test/folders
mkdir "$FOLDERS_PATH"
mkdir "$FOLDERS_PATH/joe bob"
mkdir "$FOLDERS_PATH/bob smith +"
mkdir "$FOLDERS_PATH/serenity diehl"
mkdir "$FOLDERS_PATH/anonymous person"