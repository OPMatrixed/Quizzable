# Imports os.path to make a file path relative to this file.
import os.path
# This is the library that requires installation and doesn't come with python.
# It handles database connections and executing SQL statements.
import pyodbc

class DatabaseManager(object):
    def __init__(self, filename: str) -> None:
        # This works out the filepath of the directory that this file is stored in, then it adds the filename of the database to the end.
        self.filepath = os.path.join(os.path.dirname(__file__), filename)
        # Logs the database location which was generated above.
        print("Database Path", self.filepath)
        # Connects to the database, using the pyodbc module and its Microsoft Access Driver.
        self.dbcon = pyodbc.connect("Driver={Microsoft Access Driver (*.mdb, *.accdb)}; Dbq="+self.filepath+";")
        # The cursor allows you to execute SQL commands on the database.
        self.dbCursor = self.dbcon.cursor()
    
    """ - Replaced with new execute statement that allows you to run select statements properly.
    def execute(self, *command):
        # This executes the given SQL command given as many arguments as necessary.
        self.dbCursor.execute(*command)
        # This applies the statement to the actual database file.
        self.dbcon.commit()
    """
    
    def execute(self, *command):
        """
        This method completely handles executing SQL statements, including select statements.
        Arguments:
        The SQL command with question marks in place of the input data, which the rest of the arguments are to fill in.
        Returns:
        if a SELECT statement, then it returns a list.
        else, it returns the number of affected lines.
        """
        # This executes the given SQL command given as many arguments as necessary.
        value = self.dbCursor.execute(*command)
        # Returns the results of the command.
        try:
            # This tries to get the results from a select statement. If a non-select statement has been executed, this raises an exception.
            return self.dbCursor.fetchall()
        except:
            # This catches the error thrown by the .fetchall() if the command yielded no output.
            # The line below applies the statement's changes to the database file.
            self.dbcon.commit()
            # This value is returned from the .execute(*command) line, and usually is the amount of rows modified by a command.
            return value
    
    def dispose(self) -> None:
        """Run when this object needs to be destroyed, usually on application exit."""
        self.dbcon.close()
        print("Database connection closed.")
