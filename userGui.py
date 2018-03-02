# This file will handle two screens specified on the design document:
# the user creation screen, and the user settings screen.

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import tkinter.messagebox as tkmb
import re

import user

class UserCreateDialog(object):
    def __init__(self, toplevel: tk.Tk, parent) -> None:
        """
        toplevel is the tkinter object of the parent window.
        parent in the MainApp object, unless another dialog opens this window.
        """
        self.parent = parent
        self.toplevel = toplevel
        # This creates the window. padx and pady here add 5 pixels padding horizontally and vertically respectively
        # This is to stop the widgets on the window from touching the edges of the window, which doesn't look that good.
        self.window = tk.Toplevel(toplevel, padx = 5, pady = 5)
        # This makes this window always render above the base window.
        self.window.transient(self.toplevel)
        # Dimensions of the window: 500 pixels wide by 300 pixels high.
        self.window.geometry("500x300")
        # The minimum dimensions of the window, as this window is resizable.
        self.window.minsize(width = 500, height = 300)
        # Setting the title of the window.
        self.window.title("Create User - Quizzable")
        
        # Configuring the grid configuration of the window, in which the elements/widgets on the window will fit into.
        # There are 4 columns and 5 rows.
        self.window.grid_columnconfigure(0, weight = 1)
        self.window.grid_columnconfigure(1, weight = 1)
        self.window.grid_columnconfigure(2, weight = 1)
        self.window.grid_columnconfigure(3, weight = 1)
        self.window.grid_rowconfigure(0, weight = 1)
        self.window.grid_rowconfigure(1, weight = 1)
        self.window.grid_rowconfigure(2, weight = 1)
        self.window.grid_rowconfigure(3, weight = 1)
        self.window.grid_rowconfigure(4, weight = 1)
        
        # The header text font
        self.headerFont = tkfont.Font(family = "Helvetica", size = 28)
        # The header itself.
        self.headerLabel = tk.Label(self.window, text = "Create User", font = self.headerFont)
        self.headerLabel.grid(row = 0, column = 0, columnspan = 2)
        
        # The Labels/Text widgets to the left of the entry boxes/buttons with the name of the input expected on the right.
        self.usernameLabel = tk.Label(self.window, text = "Username:")
        self.defaultExamBoardLabel = tk.Label(self.window, text = "Default exam board:")
        self.timerSettingsLabel = tk.Label(self.window, text = "Timer setting:  No timer")
        self.timeSetting = 0
        # These go on the first column (column 0)
        self.usernameLabel.grid(row = 1, column = 0)
        self.defaultExamBoardLabel.grid(row = 2, column = 0)
        self.timerSettingsLabel.grid(row = 3, column = 0)
        
        examboardList = ["No preference"]
        # This queries the database to get the names of the examboards
        examboardQueryResults = self.parent.database.execute("SELECT `EName` FROM `Examboards`;")
        if(examboardQueryResults):
            for i in examboardQueryResults:
                examboardList.append(i[0])
        
        # The actual entry fields for the user settings.
        self.usernameEntry = tk.Entry(self.window, width = 20)
        # Examboard entry is a combobox. It gets the options from the examboards tabel in the database.
        self.defaultExamBoardEntry = ttk.Combobox(self.window, values = examboardList)
        # The three timer button options represent three different timer settings. These are the only three, so I used buttons rather than drop down.
        self.timerButton1 = tk.Button(self.window, text = "No timer (easy)", command = lambda: self.changeTimeSetting(0))
        self.timerButton2 = tk.Button(self.window, text = "Long timer (medium)", command = lambda: self.changeTimeSetting(1))
        self.timerButton3 = tk.Button(self.window, text = "Short timer (hard)", command = lambda: self.changeTimeSetting(2))
        # Each of the buttons needs its own column, so the username and examboard entries are spread over three columns, using columnspan = 3.
        self.usernameEntry.grid(row = 1, column = 1, columnspan = 3, sticky = tk.W+tk.E)
        self.defaultExamBoardEntry.grid(row = 2, column = 1, columnspan = 3, sticky = tk.W+tk.E)
        # The three buttons are all on the same row.
        self.timerButton1.grid(row = 3, column = 1, sticky = tk.W+tk.E)
        self.timerButton2.grid(row = 3, column = 2, sticky = tk.W+tk.E)
        self.timerButton3.grid(row = 3, column = 3, sticky = tk.W+tk.E)
        
        # This button finalises the user and will save the users details to the database, and select the user, brining the actual user straight to the quiz browser.
        self.completeButton = tk.Button(self.window, text = "Create User", command = self.finish)
        self.completeButton.grid(row = 4, column = 3, sticky = tk.W+tk.E+tk.N+tk.S)
    
    def changeTimeSetting(self, setting: int) -> None:
        self.timeSetting = setting
        if(setting == 0):
            self.timerSettingsLabel.config(text = "Timer setting: No timer")
        elif(setting == 1):
            self.timerSettingsLabel.config(text = "Timer setting: Long timer")
        else:
            self.timerSettingsLabel.config(text = "Timer setting: Short timer")
    
    def finish(self) -> None:
        """
        This is called when the user clicks the "Create User" button in the bottom right of the dialog.
        This adds the user to the database, selects the user as the current user, and changes the main window to the quiz browser.
        """
        
        # This gets the username from the entry box, and removes whitespace at the start and the end of the string.
        username = self.usernameEntry.get().strip()
        # Length/Presence check
        if(len(username) < 3):
            # Username too short, display an error message.
            tkmb.showerror("Username error", "Username is too short, it should be between 3 and 20 characters inclusive.\nSpaces at the start and end of the username are ignored.", parent = self.window)
            return
        if(len(username) > 20):
            # Username too long, display an error message.
            tkmb.showerror("Username error", "Username is too long, it should be between 3 and 20 characters inclusive.", parent = self.window)
            return
        # This removes invalid characters with the regular expression defined at the top of this file.
        reducedUsername = re.compile('[^a-zA-Z0-9\-_ ]').sub("", username)
        if(reducedUsername != username):
            # Username has invalid characters, display an error message.
            tkmb.showerror("Username error", "Username contains invalid characters, it should only contain english letters, numbers, spaces, underscores and dashes.", parent = self.window)
            return
        # Check to see if username is already in use.
        queryResult = self.parent.database.execute("SELECT * FROM `Users` WHERE `Username`=?;", username)
        if(queryResult):
            # Username is already in use, display an error message.
            print("Username already in use.")
            tkmb.showerror("Username error", "Username is already in use.", parent = self.window)
            return
        
        defaultExamBoard = self.defaultExamBoardEntry.get()
        defaultExamBoardID = -1
        # The following gets the default exam board setting.
        if(defaultExamBoard != "" and defaultExamBoard != "No preference"):
            query = self.parent.database.execute("SELECT `ExamboardID` FROM `Examboards` WHERE `EName`=?;", defaultExamBoard)
            defaultExamBoardID = query[0][0]
        # This creates the user object, which automatically adds the user to the database.
        self.parent.currentUser = user.User(self.parent.database, -1, username, self.timeSetting, defaultExamBoardID)
        
        import mainmenu
        # If the user is on the login screen, turn it to the quiz browser screen.
        if(self.parent.state == mainmenu.MainWindowStates.login):
            self.parent.unloadLoginScreen()
            self.parent.loadQuizBrowserScreen()
        # This destroys the window after all the previous tasks are finished.
        self.window.destroy()

class UserSettingsDialog(object):
    def __init__(self, toplevel: tk.Tk, parent) -> None:
        """
        toplevel is the tkinter object of the parent window.
        parent in the MainApp object, unless another dialog opens this window.
        """
        self.parent = parent
        self.toplevel = toplevel
        # This creates the window. padx and pady here add 5 pixels padding horizontally and vertically respectively
        # This is to stop the widgets on the window from touching the edges of the window, which doesn't look that good.
        self.window = tk.Toplevel(toplevel, padx = 5, pady = 5)
        # Dimensions of the window: 500 pixels wide by 300 pixels high.
        self.window.geometry("500x300")
        # The minimum dimensions of the window, as this window is resizable.
        self.window.minsize(width = 500, height = 300)
        # Setting the title of the window.
        self.window.title("User settings - Quizzable")
        
        # Configuring the grid configuration of the window, in which the elements/widgets on the window will fit into.
        self.window.grid_columnconfigure(0, weight = 1)
        self.window.grid_columnconfigure(1, weight = 1)
        self.window.grid_columnconfigure(2, weight = 1)
        self.window.grid_columnconfigure(3, weight = 1)
        self.window.grid_rowconfigure(0, weight = 1)
        self.window.grid_rowconfigure(1, weight = 1)
        self.window.grid_rowconfigure(2, weight = 1)
        self.window.grid_rowconfigure(3, weight = 1)
        self.window.grid_rowconfigure(4, weight = 1)
        
        # The header text font
        self.headerFont = tkfont.Font(family = "Helvetica", size = 28)
        # The header itself.
        self.headerLabel = tk.Label(self.window, text = "User Settings", font = self.headerFont)
        # The Labels/Text widgets to the left of the entry boxes/buttons with the name of the input expected on the right.
        self.usernameLabel = tk.Label(self.window, text = "Username: " + self.parent.currentUser.username)
        self.defaultExamBoardLabel = tk.Label(self.window, text = "Default exam board:")
        self.timerSettingsLabel = tk.Label(self.window, text = "Timer settings:  No Timer")
        # These go on the first column (column 0)
        self.headerLabel.grid(row = 0, column = 0, columnspan=2)
        self.usernameLabel.grid(row = 1, column = 0)
        self.defaultExamBoardLabel.grid(row = 2, column = 0)
        self.timerSettingsLabel.grid(row = 3, column = 0)
        
        # This queries the database to get the names of the examboards
        examBoardQueryResults = self.parent.database.execute("SELECT * FROM `Examboards`;")
        examBoardList = ["No preference"]
        if(examBoardQueryResults):
            examBoardList += [i[1] for i in examBoardQueryResults]
        # To set the user's current exam board as the default value in the field, this code must run
        self.currentExamBoard = tk.StringVar()
        if(self.parent.currentUser.defaultExamBoard != -1):
            self.currentExamBoard.set(self.parent.examboardDictionary[self.parent.currentUser.defaultExamBoard])
        else:
            self.currentExamBoard.set("No preference")
        
        # The actual entry fields for the user settings.
        # Exam board entry is a combobox. It gets the options from the exam boards table in the database.
        self.defaultExamBoardEntry = ttk.Combobox(self.window, values = examBoardList, textvariable = self.currentExamBoard, state = "readonly")
        # The three timer button options represent three different timer settings. These are the only three, so I used buttons rather than drop down.
        self.timerButton1 = tk.Button(self.window, text = "No timer (easy)", command = lambda: self.changeTimeSetting(0))
        self.timerButton2 = tk.Button(self.window, text = "Long timer (medium)", command = lambda: self.changeTimeSetting(1))
        self.timerButton3 = tk.Button(self.window, text = "Short timer (hard)", command = lambda: self.changeTimeSetting(2))
        # Each of the buttons needs its own column, so the exam board entry is spread over three columns, using columnspan = 3.
        self.defaultExamBoardEntry.grid(row = 2, column = 1, columnspan = 3, sticky = tk.W+tk.E)
        # The three buttons are all on the same row.
        self.timerButton1.grid(row = 3, column = 1, sticky = tk.W+tk.E)
        self.timerButton2.grid(row = 3, column = 2, sticky = tk.W+tk.E)
        self.timerButton3.grid(row = 3, column = 3, sticky = tk.W+tk.E)
        
        # This button will run the self.finish() method, and will save the user settings in the database.
        self.completeButton = tk.Button(self.window, text = "Update user settings", command = self.finish)
        self.completeButton.grid(row = 4, column = 3, sticky = tk.W+tk.E+tk.N+tk.S)
        self.changeTimeSetting(self.parent.currentUser.timeConfig)
    
    def changeTimeSetting(self, setting):
        self.timeSetting = setting
        if(setting == 0):
            self.timerSettingsLabel.config(text = "Timer setting: No timer")
        elif(setting == 1):
            self.timerSettingsLabel.config(text = "Timer setting: Long timer")
        else:
            self.timerSettingsLabel.config(text = "Timer setting: Short timer")
    
    def finish(self) -> None:
        """
        This is called when the user clicks the "Update user settings" button in the bottom right of the dialog.
        This will update the user's settings that are currently in memory and update the user record on the database.
        This destroys the window after all the previous tasks are finished.
        """
        
        defaultExamBoard = self.defaultExamBoardEntry.get()
        defaultExamBoardID = -1
        # The following gets the default exam board setting.
        if(defaultExamBoard == ""):
            self.parent.currentUser.savePreferences(timeConfig = self.timeSetting)
            self.window.destroy()
            return
        if(defaultExamBoard != "No preference"):
            query = self.parent.database.execute("SELECT `ExamboardID` FROM `Examboards` WHERE `EName`=?;", defaultExamBoard)
            defaultExamBoardID = query[0][0]
        self.parent.currentUser.savePreferences(timeConfig = self.timeSetting, defaultExamBoard = defaultExamBoardID)
        
        self.window.destroy()
