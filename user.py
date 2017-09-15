# This file contains the User class
# The User class holds the data on a user that has just been created or loaded from the database.
# The class handles saving/loading users from database, changing user settings, and creating new users.

class User(object):
	def __init__(self, id = -1, username, timeConfig, defaultExamBoard):
		# This is the initializer function, and takes in the following arguments:
		# Arguments: id: Integer
		#            username: String,
		#            timeConfig: Integer between 0 and 2 inclusive
		#            defaultExamBoard: Integer (id of exam board)
		# Returns: self (User object)
		self.id = id
		self.username = username
		self.timeConfig = timeConfig
		self.defaultExamBoard = defaultExamBoard
		if(id == -1):
			self.addUserToDatabase()
	
	def addUserToDatabase(self):
		# This adds this user to the database.
		# TODO: Create database entry and set self.id to the auto-generated id.
		pass
		
	def saveUserPreferences(self, timeConfig = -1, defaultExamBoard = -1):
		# This allows the software to change the user's settings and update the database if they have changed.
		# Arguments: timeConfig: Integer between -1 and 2 inclusive (-1 is the rogue value to indicate no change).
		#            defaultExamBoard: Integer (-1 is the rogue value to indicate no change).
		# Returns: True if saved successfully.
		#          False if failed, an error will be printed to std.err (visible in the console log)
		if(timeConfig == self.timeConfig and defaultExamBoard == self.defaultExamBoard):
			return True
		if(timeConfig != -1):
			self.timeConfig = timeConfig
		if(defaultExamBoard != -1):
			self.defaultExamBoard = defaultExamBoard
		# TODO: Update database entry
	
	def deleteUser(self):
		# Removes the user from the database.
		# Returns: True if successfully deleted.
		#          False if failed to delete.
		pass # TODO: Add code to delete from database.
	
	def loadUsers(): # This doesn't get called on a User object, but the User class (a static method).
		# Takes no arguments
		# Returns a list of users from the database.
		pass # TODO: Add code
