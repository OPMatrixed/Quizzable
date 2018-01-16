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
        if(defaultExamBoard == None):
            self.defaultExamBoard = -1
        else:
            self.defaultExamBoard = defaultExamBoard
        if(id == -1):
            self.addToDatabase()
    
    def addToDatabase(self) -> None:
        """This adds this user to the database."""
        # This adds the user record.
        if(self.defaultExamBoard == -1):
            self.dbm.execute("INSERT INTO `Users` (Username, TimeConfig) VALUES (?,?);", self.username, self.timeConfig)
        else:
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
            return True
        if(timeConfig != -1):
            self.timeConfig = timeConfig
        if(defaultExamBoard != -2):
            self.defaultExamBoard = defaultExamBoard
        self.dbm.execute("UPDATE `Users` SET `TimeConfig`=?,`DefaultBoardID`=? WHERE `UserID`=?;", self.timeConfig, (self.defaultExamBoard if self.defaultExamBoard != -1 else None), self.id)
    
    def delete(self) -> None:
        """
        Removes the user from the database.
        Returns:
        True if successfully deleted.
        False if failed to delete.
        """
        pass # TODO: Add code to delete from database.
