# This file contains the User class
# The User class holds the data on a user that has just been created or loaded from the database.
# The class handles saving/loading users from database, changing user settings, and creating new users.

class User(object):
    def __init__(self, databaseManager, id: int, username: str, timeConfig: int, defaultExamBoard: int) -> None:
        """This is the function that instantiates the User object."""
        self.dbm = databaseManager
        self.id = id
        self.username = username
        self.timeConfig = timeConfig
        self.defaultExamBoard = defaultExamBoard
        # If the default exam board hasn't been set, set its value to the rogue value of -1.
        if(defaultExamBoard == None):
            self.defaultExamBoard = -1
        if(id == -1):
            # If the user has no ID, assume that this user isn't in the database, so add the user to the database.
            self.addToDatabase()
    
    def addToDatabase(self) -> None:
        """This adds this user to the database."""
        # This adds the user record.
        if(self.defaultExamBoard == -1):
            # If no default exam board has been set, run the query without it.
            self.dbm.execute("INSERT INTO `Users` (Username, TimeConfig) VALUES (?,?);", self.username, self.timeConfig)
        else:
            # If a default exam board has been set, include it in the query.
            self.dbm.execute("INSERT INTO `Users` (Username, TimeConfig, DefaultBoardID) VALUES (?,?,?);", self.username, self.timeConfig, self.defaultExamBoard)
        # This gets the inserted record's UserID.
        lastRecord = self.dbm.execute("SELECT @@IDENTITY;")
        self.id = lastRecord[0][0]
    
    def savePreferences(self, timeConfig: int = -1, defaultExamBoard: int = -2) -> None:
        """
        This allows the application to change the user's settings and update the database if they have changed.
        Arguments:
        timeConfig: Integer between -1 and 2 inclusive (-1 is the rogue value to indicate no change).
        defaultExamBoard: Integer (-2 is the rogue value to indicate no change, -1 is the rogue value that indicates "No preference").
        """
        if(timeConfig == self.timeConfig and defaultExamBoard == self.defaultExamBoard):
            # If the user's settings haven't changed, cancel execution of the method.
            return
        if(timeConfig != -1):
            # If the time config has been changed, update it in the object.
            self.timeConfig = timeConfig
        if(defaultExamBoard != -2):
            # If the default exam board has been changed, update it in the object.
            self.defaultExamBoard = defaultExamBoard
        # Update the database with the new values.
        self.dbm.execute("UPDATE `Users` SET `TimeConfig`=?, `DefaultBoardID`=? WHERE `UserID`=?;", self.timeConfig, (self.defaultExamBoard if self.defaultExamBoard != -1 else None), self.id)
    
    def delete(self) -> None:
        """Removes the user from the database."""
        if(id != -1):
            # Check if the user has been saved to the database.
            # First, delete the results that the user has.
            self.dbm.execute("DELETE FROM `Results` WHERE UserID = ?;", float(self.id))
            # Then remove the user record.
            self.dbm.execute("DELETE FROM `Users` WHERE UserID = ?;", float(self.id))
