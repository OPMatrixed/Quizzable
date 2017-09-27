# Imports os.path to make a file path relative to this file.
import os.path
# This is the library that requires installation and doesn't come with python.
# It handles database connections and executing SQL statements.
import pyodbc

class DatabaseManager(object):
	def __init__(self, filename):
		self.filepath = os.path.join(os.path.dirname(__file__), filename)
		print("Database Path", self.filepath)
		self.dbcon = pyodbc.connect("Driver={Microsoft Access Driver (*.mdb, *.accdb)}; Dbq="+self.filepath+";")
		self.dbCursor = self.dbcon.cursor()
	
	def execute(self, *command):
		self.dbCursor.execute(*command)
		self.dbcon.commit()

	def dispose(self):
		self.dbcon.close()
