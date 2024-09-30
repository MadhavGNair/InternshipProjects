# DatabaseEditor
**Author: Madhav Girish Nair (madhavgirish02@gmail.com)**

The purpose of this module is to automate basic CRUD functionality of a given database and its tables using Python. This allows insertion of large CSV files of data to the database with ease. It also allows users that are not interested or inexperienced with CLI or SQL queries to have a Python wrapper to reduce the learning curve.

The folder structure and file contents are explained below:

## /database
This folder contains the main code and the following sub-folders,

### database_editor.py
This file is the main class for the DatabaseEditor. It is able to perfom the basic CRUD functionality and can be expanded to include much more complex functionality at a later point.

### main.py
This is where the DatabaseEditor class is initialized and manipulated. Examples of how to use the functions are given in this file (to be moved to README).

### NOTES:
1. The delete_table function currently does not support cascading. Therefore, any relations must be manually removed or cascading query must be executed on CLI.