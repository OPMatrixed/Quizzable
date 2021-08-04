"""This file contains the code to design the main login screen, and also the main quiz list viewer."""

# These imports load in the tkinter library, which is used to make windows and add widgets to those windows.
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import tkinter.filedialog as tkfile
import tkinter.messagebox as tkmb
# Threading module is needed to add a delay to some code, to fix a bug that is documented in the "Developmental Testing" section.
import threading
# Difflib is used to compare how alike two strings are, used in the search bar.
import difflib
# Collections is used to sort the quizzes based off of their 'scores' based on how similar a quiz is to the search query.
import collections
# Time is used to track how long each search/filter takes.
import time
# The 'math' module is used for its floor and ceiling functions. I have renamed it 'maths' because it's better this way.
import math as maths

# This imports the database file from the same directory as this file.
import database

class MainWindowStates:
    """
    Stored in MainApp.state, it holds one of these integers, which corresponds to the state of the main window of the application.
    This would be called an enumeration class in a language like Java, but as far as I know this is Python's closest equivalent.
    """
    closing = 0
    login = 1
    quizBrowser = 2

class MainMenu(object):
    # The app title and the version, stored as strings here and can be accessed from anywhere in the system.
    # These variables are usually used in window titles.
    appName = "Quizzable"
    appVersion = "v1"
    # If you haven't seen the following method notation before, you can put a colon after a parameter name to indicate what type it should be.
    # This type is not enforced, it is just to make it quickly understandable to anyone reading the code.
    # The return type can follow a "->" after the close bracket but before the colon. This also isn't strictly enforced by Python,
    # it is just for making it easier to understand when someone else is looking at the code.
    def __init__(self, tkobj: tk.Tk) -> None:
        """
        This method is called when MainMenu is initialised as a variable, and passes in tkobj e.g. "MainApp(app)"
        Arguments:
        tkobj is the window object
        """
        self.tk = tkobj
        # This sets the default dimensions of the window, 800 pixels wide by 600 pixels high.
        self.tk.geometry("800x600")
        # This sets the minimum dimensions of the window, 700 pixels wide by 350 pixels high.
        self.tk.minsize(width = 700, height = 350)
        # This sets the title of the application.
        self.tk.title("Home - " + MainMenu.appName + " - " + MainMenu.appVersion)
        # Makes the program destroy the window when the X button in the top right is pressed.
        self.tk.protocol("WM_DELETE_WINDOW", self.endApplication)
        # This sets the state of the application, to keep track of what's on the main window.
        self.state = MainWindowStates.login
        # This gets changed once a user is selected.
        self.currentUser = None
        # This creates the database connection.
        self.database = database.DatabaseManager("QuizAppDatabase.accdb")
        # This creates the menu bar at the top of the window.
        self.createTitleBarMenu()
        # This loads the login screen on the main window.
        self.loadLoginScreen()
        
        # Exam boards are stored in a dictionary, where the database IDs map to each exam board's name.
        self.examboardDictionary = {}
        # This queries the database to get the names of the exam boards.
        examboardQueryResults = self.database.execute("SELECT * FROM `Examboards`;")
        if(examboardQueryResults):
            # If exam boards have been found in the database:
            for i in examboardQueryResults:
                # Loop through each exam board in the database table, and add it to the exam board dictionary.
                self.examboardDictionary[i[0]] = i[1]
        
        # Subjects are stored in a dictionary, where the database IDs map to each subject's name.
        self.subjectDictionary = {}
        # This queries the database to get the names of the subjects.
        subjectQueryResults = self.database.execute("SELECT * FROM `Subjects`;")
        if(subjectQueryResults):
            # If subjects have been found in the database:
            for i in subjectQueryResults:
                # Loop through each subject in the database table, and add it to the subject dictionary.
                self.subjectDictionary[i[0]] = i[1]
        # Inverse dictionaries for backwards lookups, where the system needs to find a database ID from a subject or exam board name.
        self.inverseSubjectDictionary = {v: k for k, v in self.subjectDictionary.items()}
        self.inverseExamboardDictionary = {v: k for k, v in self.examboardDictionary.items()}
        # The quiz the user has currently selected, starts off as None (as no quiz is selected by default).
        self.currentlySelectedQuiz = None
    
    def createTitleBarMenu(self) -> None:
        """
        This will add the menu bar to the top of the window.
        Returns nothing.
        This imports the userGui module from the application directory, which is used for the user settings dialog.
        This also imports the listEditor module, which is used to open the subject and exam board editor dialogs.
        """
        import userGui
        import listEditor
        
        # Creating the menu object.
        self.menuBar = tk.Menu(self.tk)
        
        # tearoff = 0 means that the drop-down can't be "ripped off", and be turned into its own little mini-dialog window.
        # This code is the "User" drop-down menu.
        self.userMenu = tk.Menu(self.menuBar, tearoff = 0)
        # userGui.UserCreateDialog() makes a Create User window, and it is passed as a lambda statement as arguments have to be passed.
        self.userMenu.add_command(label = "Create New User", command = lambda: userGui.UserCreateDialog(self.tk, self))
        # The command to open the user settings window.
        self.userMenu.add_command(label = "User Settings", command = self.userSettings)
        # The command to switch user, which only works after the user has logged in.
        self.userMenu.add_command(label = "Change User", command = self.switchUser)
        
        # This is the subjects & exam boards drop-down.
        self.subjectsAndExamBoardsMenu = tk.Menu(self.menuBar, tearoff = 0)
        # This launches the subject list editor window.
        self.subjectsAndExamBoardsMenu.add_command(label = "Edit Subject List", command = lambda: listEditor.SubjectEditor(self.tk, self))
        # This launches the exam board list editor window.
        self.subjectsAndExamBoardsMenu.add_command(label = "Edit Exam Board List", command = lambda: listEditor.ExamBoardEditor(self.tk, self))
        
        # This is the quiz drop-down, and handles creating quizzes and import quizzes.
        self.quizMenu = tk.Menu(self.menuBar, tearoff = 0)
        # The command to open the quiz creator window.
        self.quizMenu.add_command(label = "Create a Quiz", command = self.createQuizButtonCommand)
        # The command to start the process of importing a quiz, firstly by opening the Windows open file dialog.
        self.quizMenu.add_command(label = "Import a Quiz", command = self.importQuizButtonCommand)
        
        # Adding the above sub-menus to the main menu bar.
        # The "Quiz Management" drop-down which contains the create/import quiz command buttons.
        self.menuBar.add_cascade(label = "Quiz Management", menu = self.quizMenu)
        # The "User" drop-down, which contains the "Add User", "Edit user settings", and "Change user" commands.
        self.menuBar.add_cascade(label = "User", menu = self.userMenu)
        # The "Subjects & Exam Boards" drop-down, which has the command buttons to open the list editor windows.
        self.menuBar.add_cascade(label = "Subjects & Exam Boards", menu = self.subjectsAndExamBoardsMenu)
        # The "Statistics" button, which is next to the drop-down menus, which also launches the statistics window.
        self.menuBar.add_command(label = "Statistics", command = self.launchStatistics)
        
        # Assigns the menu to the window.
        self.tk.config(menu = self.menuBar)
    
    def loadLoginScreen(self) -> None:
        """
        This method loads the elements of the login screen on to the main window.
        No arguments or return values.
        """
        # This import is a file in the base directory, and holds the UserCreateDialog class which is used here.
        import userGui
        # This is the specification of the header font.
        headerFont = tkfont.Font(family = "Helvetica", size = 28)
        
        # The following lines configure the "grid", on which elements are placed, to adjust the sizes of the rows and columns.
        # This grid will have 3 columns and 8 rows.
        # Column configuration:
        # All the visual elements will be placed in the centre column, the two surrounding columns are for padding.
        self.tk.grid_columnconfigure(0, weight = 2)
        self.tk.grid_columnconfigure(1, weight = 1)
        self.tk.grid_columnconfigure(2, weight = 2)
        # Row configuration:
        # The 2nd row holds the heading text, the 4th row holds the user drop-down,
        # the 6th and 7th rows contain the select/create user buttons.
        # Note that row '0' is the 1st row, and '1' is the 2nd row, etc.
        self.tk.grid_rowconfigure(0, weight = 3)
        self.tk.grid_rowconfigure(1, weight = 2)
        self.tk.grid_rowconfigure(2, weight = 1)
        self.tk.grid_rowconfigure(3, weight = 2)
        self.tk.grid_rowconfigure(4, weight = 1)
        self.tk.grid_rowconfigure(5, weight = 2)
        self.tk.grid_rowconfigure(6, weight = 2)
        self.tk.grid_rowconfigure(7, weight = 1)
        # Creating the login screen heading text
        self.loginLabel = tk.Label(self.tk, text = "User Selection", font = headerFont)
        
        # Creating a list to hold all the usernames of the users, to be placed in the user drop-down.
        userList = []
        # This queries the database to get the usernames of all the users.
        userQueryResults = self.database.execute("SELECT `Username` FROM `Users`;")
        if(userQueryResults):
            # If users are found in the database:
            for i in userQueryResults:
                # For each user in the database, add their username to the user list.
                userList.append(i[0])
        else:
            # If no users are found in the database, show the following message:
            userList = ["No users created, click \"Create User\""]
        
        # The user selection combobox (drop-down list).
        self.loginComboUser = ttk.Combobox(self.tk, state = "readonly", values = userList)
        # The "login" button, which selects the user currently selected in the combobox.
        self.loginSelectUserButton = tk.Button(self.tk, text = "Select User", bg = "#EAEAEA", border = 3, relief = tk.GROOVE, command = self.selectUser)
        # The create user button, which launches the Create User box.
        self.loginCreateUserButton = tk.Button(self.tk, text = "Create User", bg = "#DFDFDF", border = 3, relief = tk.GROOVE, command = lambda: userGui.UserCreateDialog(self.tk, self))
        # Positioning the above elements in the grid layout.
        self.loginLabel.grid(row = 1, column = 1) # The heading text.
        self.loginComboUser.grid(row = 3, column = 1, sticky = tk.W+tk.E+tk.N+tk.S) # The user selection drop-down menu.
        self.loginSelectUserButton.grid(row = 5, column = 1, sticky = tk.W+tk.E+tk.N+tk.S) # The select user button.
        self.loginCreateUserButton.grid(row = 6, column = 1, sticky = tk.W+tk.E+tk.N+tk.S) # The create user button.
    
    def unloadLoginScreen(self) -> None:
        """
        This method removes all the elements off the login screen and resets the grid configuration
        Basically, it cleans the window of elements so another screen can be loaded.
        Takes no arguments and also returns nothing.
        """
        # Removing the elements.
        self.loginLabel.destroy()
        self.loginComboUser.destroy()
        self.loginCreateUserButton.destroy()
        self.loginSelectUserButton.destroy()
        # Resetting the grid configuration.
        for i in range(8):
            # Resetting each row.
            self.tk.grid_rowconfigure(i, weight = 0)
        # Resetting the columns.
        self.tk.grid_columnconfigure(0, weight = 0)
        self.tk.grid_columnconfigure(1, weight = 0)
        self.tk.grid_columnconfigure(2, weight = 0)
    
    def selectUser(self) -> None:
        """
        Called on clicking the select user button on the login screen.
        """
        # Gets the text from the Combobox.
        username = self.loginComboUser.get()
        if(not username): # Presence check 
            return
        if(username == "No users created, click \"Create User\""): # Rogue value check
            return
        # Imports the user module from the base directory.
        import user
        # This gets the user details from the database.
        userDetails = self.database.execute('SELECT * FROM `Users` WHERE `Username`=?;', username)[0]
        # Creates the user object and stores it as a variable in the application object.
        self.currentUser = user.User(self.database, *userDetails)
        # Unloads the elements on the screen
        self.unloadLoginScreen()
        # Loads the quiz browser screen.
        self.loadQuizBrowserScreen()
    
    def loadQuizBrowserScreen(self) -> None:
        """
        This method loads the quiz browser screen onto the main window.
        It takes no arguments and doesn't return anything.
        """
        # Changing the application state, which is tracked to prevent errors such as reloading the quiz list on the login screen.
        self.state = MainWindowStates.quizBrowser
        # Changing the title of the window.
        self.tk.title("Quiz Browser - " + MainMenu.appName + " - " + MainMenu.appVersion)
        # Configuring the window and the window grid. This grid has 4 rows and 4 columns.
        # The row configuration:
        # The top two rows must have a minimum height, each has a minimum of 40px height.
        # The heights of the rows can be larger if any of the elements on the top two rows need more space, space is added automatically by TkInter.
        self.tk.grid_rowconfigure(0, weight = 0, minsize = 40)
        self.tk.grid_rowconfigure(1, weight = 0, minsize = 40)
        # The bottom two rows are for the large frame that holds the question lists and the side panel.
        self.tk.grid_rowconfigure(2, weight = 1)
        self.tk.grid_rowconfigure(3, weight = 1)
        # The column configuration:
        self.tk.grid_columnconfigure(0, weight = 1)
        self.tk.grid_columnconfigure(1, weight = 1)
        self.tk.grid_columnconfigure(2, weight = 1)
        # The last column is the side panel column, which is forced to have a width larger than 200px.
        self.tk.grid_columnconfigure(3, weight = 1, minsize = 200)
        
        # Adding the search box widget.
        # I create a frame here, as I want the "Search:" text and the text entry to behave like a single element spanning over 2 columns in the window grid.
        self.quizBrowserSearchFrame = tk.Frame(self.tk)
        # Frame grid configuration, 2 columns and 1 row - the second column should be much wider than the first column, hence the larger weight.
        self.quizBrowserSearchFrame.grid_columnconfigure(0, weight = 1)
        self.quizBrowserSearchFrame.grid_columnconfigure(1, weight = 4)
        self.quizBrowserSearchFrame.grid_rowconfigure(0, weight = 1)
        # The search text preceding the text entry box.
        self.quizBrowserSearchLabel = tk.Label(self.quizBrowserSearchFrame, text = "Search:")
        # "sticky = tk.E" below makes the search label go as far to the right within its column as it can.
        self.quizBrowserSearchLabel.grid(row = 0, column = 0, sticky = tk.E)
        # The actual search bar. This will be tied to an event later which updates the search after each letter is typed.
        self.quizBrowserSearchEntry = tk.Entry(self.quizBrowserSearchFrame, width = 10) # Width is the minimum width in characters.
        # This binds any key press to launch the search algorithm 0.1 seconds after the user has pressed a key.
        # It also starts it in another thread, to prevent the application lagging after every button press.
        self.quizBrowserSearchEntry.bind("<Key>", lambda e: threading.Timer(0.1, self.applyFilters).start())
        # "sticky = tk.W + tk.E" makes the element take as much horizontal space within its column as it can.
        self.quizBrowserSearchEntry.grid(row = 0, column = 1, sticky = tk.W + tk.E)
        # Positioning the frame over two columns in the whole window grid.
        self.quizBrowserSearchFrame.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W + tk.E)
        
        # Create a Quiz, Import a Quiz, and view statistics Buttons
        self.createQuizButton = tk.Button(self.tk, text = "Create a Quiz", command = self.createQuizButtonCommand)
        self.importQuizButton = tk.Button(self.tk, text = "Import a Quiz", command = self.importQuizButtonCommand)
        self.statisticsViewButton = tk.Button(self.tk, text = "View statistics", command = self.launchStatistics)
        # Positioning them in the top right of the window.
        self.createQuizButton.grid(row = 0, column = 2)
        self.importQuizButton.grid(row = 0, column = 3)
        self.statisticsViewButton.grid(row = 1, column = 3)
        # The quiz filters, as comboboxes. They default to having the text "Filter by ...", but after selecting another value they can't go back to "Filter by ..."
        # To remove the filter after selecting a value for the filter, the user must select the combobox and select "No filter".
        self.filterByExamBoardCombo = ttk.Combobox(self.tk, state = "readonly", values = ["No filter"] + [i for i in self.examboardDictionary.values()])
        self.filterBySubjectCombo = ttk.Combobox(self.tk, state = "readonly", values = ["No filter"] + [i for i in self.subjectDictionary.values()])
        # The difficulty filter options are hard coded, because the user can't add their own difficulty levels.
        self.filterByDifficultyCombo = ttk.Combobox(self.tk, state = "readonly", values = ["No filter", "1", "2", "3", "4", "5",
                                                    "2 and above", "3 and above", "4 and above", "2 and below", "3 and below", "4 and below"])
        # Setting the default values for the filters.
        self.filterByExamBoardCombo.set("Filter by exam board")
        self.filterBySubjectCombo.set("Filter by subject")
        self.filterByDifficultyCombo.set("Filter by difficulty")
        # Binding the comboboxes to update the list when an option in one of the dropdowns is selected.
        self.filterByExamBoardCombo.bind("<<ComboboxSelected>>", self.applyFilters)
        self.filterBySubjectCombo.bind("<<ComboboxSelected>>", self.applyFilters)
        self.filterByDifficultyCombo.bind("<<ComboboxSelected>>", self.applyFilters)
        # Positioning of the filter comboboxes. All fit on the same row.
        self.filterByExamBoardCombo.grid(row = 1, column = 0, sticky = tk.W+tk.E+tk.N+tk.S) # Sticky just makes the element stretch in certain directions.
        self.filterBySubjectCombo.grid(row = 1, column = 1, sticky = tk.W+tk.E+tk.N+tk.S) # tk.N+tk.S means up and down (North and South), tk.W+tk.E means West and East
        self.filterByDifficultyCombo.grid(row = 1, column = 2, sticky = tk.W+tk.E+tk.N+tk.S) # Adding the directions up makes it expand in all the directions you specify.
        # Start of frame box that contains the lists.
        self.quizListFrame = tk.Frame(self.tk)
        # The frame's grid configuration.
        # The first column with the quiz titles should be much larger than the other columns, and has a minimum width of 240px.
        self.quizListFrame.grid_columnconfigure(0, weight = 3, minsize = 240)
        self.quizListFrame.grid_columnconfigure(1, weight = 1)
        self.quizListFrame.grid_columnconfigure(2, weight = 1)
        self.quizListFrame.grid_columnconfigure(3, weight = 1)
        self.quizListFrame.grid_rowconfigure(1, weight = 1)
        # The column headings for the synchronised lists.
        self.quizListLabelNames = tk.Label(self.quizListFrame, text = "Quiz Name")
        self.quizListLabelSubject = tk.Label(self.quizListFrame, text = "Subject")
        self.quizListLabelExamBoard = tk.Label(self.quizListFrame, text = "Examboard")
        self.quizListLabelBestAttempt = tk.Label(self.quizListFrame, text = "Best Attempt")
        # The positions of the column headings, all on the same row.
        self.quizListLabelNames.grid(row = 0, column = 0)
        self.quizListLabelSubject.grid(row = 0, column = 1)
        self.quizListLabelExamBoard.grid(row = 0, column = 2)
        self.quizListLabelBestAttempt.grid(row = 0, column = 3)
        
        # The scroll bar for the lists.
        self.quizListBoxScrollBar = tk.Scrollbar(self.quizListFrame, command = self.scrollbarCommand)
        self.quizListBoxScrollBar.grid(row = 1, column = 4, sticky = tk.N+tk.S)
        # The main Quizzes List is split up into four synchronised lists, due to the nature of the listbox in tkinter.
        # The Quiz Name goes in the first (biggest) column.
        self.quizListBoxNames = tk.Listbox(self.quizListFrame, yscrollcommand = self.scrollOnList)
        # The Subject goes in the second column.
        self.quizListBoxSubject = tk.Listbox(self.quizListFrame, yscrollcommand = self.scrollOnList)
        # The Exam Board goes in the third column.
        self.quizListBoxExamBoard = tk.Listbox(self.quizListFrame, yscrollcommand = self.scrollOnList)
        # The Best Attempt for each quiz goes in the fourth column.
        self.quizListBoxBestAttempt = tk.Listbox(self.quizListFrame, yscrollcommand = self.scrollOnList)
        # The positioning of the synchronized lists, all on the second row, and all taking as much space as possible in their grid cell using sticky = ...
        self.quizListBoxNames.grid(row = 1, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.quizListBoxSubject.grid(row = 1, column = 1, sticky = tk.W+tk.E+tk.N+tk.S)
        self.quizListBoxExamBoard.grid(row = 1, column = 2, sticky = tk.W+tk.E+tk.N+tk.S)
        self.quizListBoxBestAttempt.grid(row = 1, column = 3, sticky = tk.W+tk.E+tk.N+tk.S)
        # Bind selecting an entry on the list to the self.selectQuiz() method.
        # It launches in a separate thread 0.1 seconds after clicking on the list, which is to prevent errors
        # and stop the main thread from lagging.
        self.quizListBoxNames.bind("<Button-1>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxSubject.bind("<Button-1>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxExamBoard.bind("<Button-1>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxBestAttempt.bind("<Button-1>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        # Also bind it to pressing any key, in case that changes the selected quiz.
        self.quizListBoxNames.bind("<Key>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxSubject.bind("<Key>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxExamBoard.bind("<Key>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxBestAttempt.bind("<Key>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        
        # Refresh the list of quizzes, which in this case just populates the list for the first time.
        self.refreshList()
        # Position the frame on the window.
        self.quizListFrame.grid(row = 2, column = 0, columnspan = 3, rowspan = 2, sticky = tk.W+tk.E+tk.N+tk.S)
        # Then load the labels and buttons to the right of the main list, the "side panel".
        self.loadSidePanel()
    
    def refreshList(self) -> None:
        """This method loads all the quizzes from the database and finds each one's best attempt - ready to be filtered, and searched."""
        if(self.state != MainWindowStates.quizBrowser):
            # If the quiz browser isn't open, don't referesh the quiz list.
            return
        # For each quiz in the database, put it in a list of result rows and then add each quiz's best attempt by the currently selected user to the end of each row (not affecting the database).
        self.allQuizzes = [list(i) + [self.database.execute("SELECT * FROM `Results` WHERE `UserID` = ? AND `QuizID` = ? ORDER BY `Score` DESC, `TotalDuration` ASC;", float(self.currentUser.id), float(i[0]))]
                                for i in self.database.execute("SELECT * FROM `Quizzes`;")]
        # With all the quizzes gathered from the database, reapply any filters and searches applied.
        self.applyFilters()
    
    def applyFilters(self, e = None) -> None:
        """
        This is run by the refreshList method, and by changing a filter or changing the text in the search bar.
        The only argument is taken because triggering a method by an event other than clicking causes an event to be passed to the method,
        that argument's default value is None and is not used.
        """
        if(self.state != MainWindowStates.quizBrowser):
            # If the window is not on the quiz browser, i.e. it is on the login screen, return here.
            return
        
        # Record the time at which this method starts running.
        startTime = time.clock()
        
        # Get the search query from the search bar.
        searchQuery = self.quizBrowserSearchEntry.get().lower()
        # Get the values of the filters
        subjectText = self.filterBySubjectCombo.get()
        examBoardText = self.filterByExamBoardCombo.get()
        difficultyText = self.filterByDifficultyCombo.get()
        # Copy the list of all the quizzes, if the [:] is omitted, then the quizList variable just refrences the self.allQuizzes list.
        quizList = self.allQuizzes[:]
        if(not subjectText == "Filter by subject" and not subjectText == "No filter"):
            # If the subject filter has been set:
            x = 0
            # Get the subject ID.
            allowedSubject = self.inverseSubjectDictionary[subjectText]
            while x < len(quizList):
                # Go through the list of quizzes, and remove those ones that don't match the subject filter.
                if(quizList[x][2] != allowedSubject):
                    del quizList[x]
                else:
                    x += 1
        if(not examBoardText == "Filter by exam board" and not examBoardText == "No filter"):
            # If the exam board filter has been set:
            x = 0
            # Get the exam board ID:
            allowedExamBoard = self.inverseExamboardDictionary[examBoardText]
            while x < len(quizList):
                # Go through the list of quizzes, and remove those ones that don't match the exam board filter.
                if(quizList[x][3] != allowedExamBoard):
                    # If the quiz doesn't match the filter, remove it.
                    del quizList[x]
                else:
                    # Otherwise, carry on.
                    x += 1
        if(not difficultyText == "Filter by difficulty" and not difficultyText == "No filter"):
            # If the difficulty filter has been set:
            if(len(difficultyText) == 1):
                # And if the difficulty filter is just one difficulty, not a range:
                x = 0
                # Get the allowed difficulty.
                allowedDifficulty = int(difficultyText[0])
                while x < len(quizList):
                    # Then go through the list of quizzes, and remove those ones that don't match the difficulty filter.
                    if(quizList[x][6] != allowedDifficulty):
                        # If the quiz doesn't match the filter, remove it.
                        del quizList[x]
                    else:
                        # Otherwise, carry on.
                        x += 1
            elif(difficultyText.endswith("above")):
                # If the difficulty filter is a range with the word "above", e.g. "3 and above".
                x = 0
                # Find the minimum difficulty
                allowedDifficulty = int(difficultyText[0])
                while x < len(quizList):
                    # Then go through the list of quizzes, and remove those ones that are below the minimum difficulty.
                    if(quizList[x][6] < allowedDifficulty):
                        # If the quiz doesn't match the filter, remove it.
                        del quizList[x]
                    else:
                        # Otherwise, carry on.
                        x += 1
            else:
                # If the difficulty filter is a range with the word "below", e.g. "2 and below".
                x = 0
                # Get the maximum diffiuclty
                allowedDifficulty = int(difficultyText[0])
                while x < len(quizList):
                    # Then go through the list of quizzes, and remove those ones that are above the maximum difficulty.
                    if(quizList[x][6] > allowedDifficulty):
                        # If the quiz doesn't match the filter, remove it.
                        del quizList[x]
                    else:
                        # Otherwise, carry on.
                        x += 1
        
        # Ranking algorithm
        if(len(searchQuery.strip())):
            # If there is text in the search bar that isn't white space:
            # Split the query into a list of words, separated by spaces.
            searchWords = searchQuery.split(" ")
            quizRankings = {}
            for i in range(len(quizList)):
                # For each quiz:
                score = 0
                for k in searchWords:
                    if(not k):
                        # If there is just a space with no word following, then ignore that word.
                        continue
                    # For each word in the search query:
                    for j in quizList[i][1].split(" "):
                        # For each word in the quiz title, work out how similar the words are and add it to the score.
                        score += 2 * maths.pow(difflib.SequenceMatcher(None, k, j).ratio(), 3)
                        # Also add the number of exact word matches to the score.
                        score += j.count(k)
                    for j in quizList[i][5].split(","):
                        # Then go through the tags, and work out how similar the words are and add it to the score.
                        score += 2 * maths.pow(difflib.SequenceMatcher(None, k, j).ratio(), 4)
                # Divide the score to remove the advantage of having a large number of words in the title and a large amount of tags.
                quizRankings[i] = score / (1 + quizList[i][1].count(" ") + quizList[i][5].count(","))
            # The counter is a way to order the quizzes by their scores easily.
            counter = collections.Counter(quizRankings)
        
        # Clear the visual lists.
        self.quizListBoxNames.delete(0, tk.END)
        self.quizListBoxSubject.delete(0, tk.END)
        self.quizListBoxExamBoard.delete(0, tk.END)
        self.quizListBoxBestAttempt.delete(0, tk.END)
        # Clear the behind-the-scenes lists.
        self.quizIDs = []
        self.quizNames = []
        self.quizSubjects = []
        self.quizExamboards = []
        self.quizQuestionNumbers = []
        self.quizDifficulties = []
        self.quizTags = {}
        
        if(len(searchQuery.strip())):
            # If there was a search query:
            # Go through the list of quizzes in order of their scores and add each to the lists and behind-the-scenes lists.
            for j in counter.most_common(200):
                i = quizList[j[0]]
                # Add things to the behind-the-scenes lists.
                self.quizIDs.append(i[0])
                self.quizNames.append(i[1])
                self.quizSubjects.append(i[2])
                self.quizExamboards.append(i[3])
                self.quizQuestionNumbers.append(i[4])
                self.quizDifficulties.append(i[6])
                # The tags needs to be parsed into a list, rather than a CSV string.
                # The in-line IF statement is to prevent .split() being called on a null value, in case a quiz has no tags.
                self.quizTags[i[0]] = i[5].split(",") if i[5] else []
                # This is adds each quiz to each of the on-screen lists.
                self.quizListBoxNames.insert(tk.END, i[1])
                # The subject and exam board for the quiz needs to be looked up in the dictionaries because they are stored as IDs in the database.
                self.quizListBoxSubject.insert(tk.END, self.subjectDictionary.get(i[2], ""))
                self.quizListBoxExamBoard.insert(tk.END, self.examboardDictionary.get(i[3], ""))
                
                if(i[8] and len(i[8])):
                    # If the user has attempted the quiz.
                    timeInSeconds = i[8][0][6]
                    # Calculate the time taken in minutes and seconds.
                    timeTakenString = (str(round(timeInSeconds // 60)) + "m " if timeInSeconds >= 60 else "") + (str(round((maths.ceil(timeInSeconds * 10) / 10) % 60, 1)) + "s" if round((maths.ceil(timeInSeconds * 10) / 10) % 60, 1) else "")
                    # Then add the score and the time taken to the best attempt column.
                    self.quizListBoxBestAttempt.insert(tk.END, str(round(i[8][0][3] * 100, 1)) + "% - " + timeTakenString)
                else:
                    # If the user hasn't attempted the quiz, show "Not Attempted" in the best attempt column.
                    self.quizListBoxBestAttempt.insert(tk.END, "Not Attempted")
        else:
            # If there wasn't a search query:
            # This goes through each quiz in the database and adds it to these lists which will be used in searching/filtering.
            for j in range(min(200, len(quizList))): # A maximum of 200 records will be shown.
                i = quizList[j]
                # Add things to the behind-the-scenes lists.
                self.quizIDs.append(i[0])
                self.quizNames.append(i[1])
                self.quizSubjects.append(i[2])
                self.quizExamboards.append(i[3])
                self.quizQuestionNumbers.append(i[4])
                self.quizDifficulties.append(i[6])
                # The tags needs to be parsed into a list, rather than a CSV string.
                # The in-line IF statement is to prevent .split() being called on a null value, in case a quiz has no tags.
                self.quizTags[i[0]] = i[5].split(",") if i[5] else []
                # This is adds each quiz to each of the visual lists.
                self.quizListBoxNames.insert(tk.END, i[1])
                # The subject and exam board for the quiz needs to be looked up in the dictionaries because they are stored as IDs in the database.
                self.quizListBoxSubject.insert(tk.END, self.subjectDictionary.get(i[2], ""))
                self.quizListBoxExamBoard.insert(tk.END, self.examboardDictionary.get(i[3], ""))
                if(i[8] and len(i[8])):
                    # If the user has attempted the quiz.
                    timeInSeconds = i[8][0][6]
                    # Calculate the time taken in minutes and seconds.
                    timeTakenString = (str(round(timeInSeconds // 60)) + "m " if timeInSeconds >= 60 else "") + (str(round((maths.ceil(timeInSeconds * 10) / 10) % 60, 1)) + "s" if round((maths.ceil(timeInSeconds * 10) / 10) % 60, 1) else "")
                    # Then add the score and the time taken to the best attempt column.
                    self.quizListBoxBestAttempt.insert(tk.END, str(round(i[8][0][3] * 100, 1)) + "% - " + timeTakenString)
                else:
                    # If the user hasn't attempted the quiz, show "Not Attempted" in the best attempt column.
                    self.quizListBoxBestAttempt.insert(tk.END, "Not Attempted")
        # Print to the console how long it took to filter, search, and sort the list of quizzes.
        print("Search and filter took: " + str(round(time.clock() - startTime, 3)) + "s")
    
    def loadSidePanel(self) -> None:
        """
        This method loads the side panel to the Quiz List screen, it contains the quiz details of the currently selected quiz,
        it also contains the buttons for doing actions on the quiz, e.g. launching/editing the selected quiz.
        """
        # Creating the side panel frame element.
        self.quizListSidePanel = tk.Frame(self.tk)
        self.quizListSidePanel.grid_columnconfigure(0, weight = 1)
        # Text fields, these will be updated whenever a new quiz is selected on the list.
        self.quizListSideName = tk.Label(self.quizListSidePanel, text = "")
        self.quizListSideSubject = tk.Label(self.quizListSidePanel, text = "")
        self.quizListSideExamboard = tk.Label(self.quizListSidePanel, text = "")
        self.quizListSideTotalQuestions = tk.Label(self.quizListSidePanel, text = "")
        self.quizListSideBestAttempt = tk.Label(self.quizListSidePanel, text = "")
        # Positioning of the text fields.
        self.quizListSideName.grid(row = 0, column = 0)
        self.quizListSideSubject.grid(row = 1, column = 0)
        self.quizListSideExamboard.grid(row = 2, column = 0)
        self.quizListSideTotalQuestions.grid(row = 3, column = 0)
        self.quizListSideBestAttempt.grid(row = 4, column = 0)
        # Positioning the side panel itself.
        self.quizListSidePanel.grid(row = 2, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # The buttons to do actions on the currently selected quiz. These are contained in their own frame.
        self.quizListSideButtonFrame = tk.Frame(self.tk)
        # The button frame grid configuration. There will be 1 column and 4 rows.
        self.quizListSideButtonFrame.grid_columnconfigure(0, weight = 1)
        self.quizListSideButtonFrame.grid_rowconfigure(0, weight = 1)
        self.quizListSideButtonFrame.grid_rowconfigure(1, weight = 1)
        self.quizListSideButtonFrame.grid_rowconfigure(2, weight = 1)
        self.quizListSideButtonFrame.grid_rowconfigure(3, weight = 1)
        # The actual buttons. Each has horizontal padding of 18 pixels each side of the button, and 8 pixels vertical padding.
        # Each button runs its own subroutine, and each button also starts off disabled, as no quiz will have been selected when the screen loads.
        self.quizListSideLaunchQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Launch Quiz", padx = 18, pady = 8, command = self.launchQuiz, state = tk.DISABLED)
        self.quizListSideEditQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Edit Quiz", padx = 18, pady = 8, command = self.editQuiz, state = tk.DISABLED)
        self.quizListSideExportQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Export Quiz", padx = 18, pady = 8, command = self.exportQuizButtonCommand, state = tk.DISABLED)
        self.quizListSideDeleteQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Delete Quiz", padx = 18, pady = 8, command = self.deleteQuizButtonCommand, state = tk.DISABLED)
        # The positioning for the buttons above.
        self.quizListSideLaunchQuizButton.grid(row = 0, column = 0)
        self.quizListSideEditQuizButton.grid(row = 1, column = 0)
        self.quizListSideExportQuizButton.grid(row = 2, column = 0)
        self.quizListSideDeleteQuizButton.grid(row = 3, column = 0)
        # Placing the button frame.
        self.quizListSideButtonFrame.grid(row = 3, column = 3, sticky = tk.W+tk.E+tk.N+tk.S)
    
    def unloadQuizBrowserScreen(self) -> None:
        """
        This removes all the widgets off the quiz browser screen,
        in case the login screen needs to be displayed,
        or potentially the quiz browser needs to re-load.
        """
        # Resetting the grid configuration. The rows and columns which had minimum sizes set also need to be reset.
        self.tk.grid_rowconfigure(0, weight = 0, minsize = 0)
        self.tk.grid_rowconfigure(1, weight = 0, minsize = 0)
        self.tk.grid_rowconfigure(2, weight = 0)
        self.tk.grid_rowconfigure(3, weight = 0)
        self.tk.grid_columnconfigure(0, weight = 0)
        self.tk.grid_columnconfigure(1, weight = 0)
        self.tk.grid_columnconfigure(2, weight = 0)
        self.tk.grid_columnconfigure(3, weight = 0, minsize = 0)
        
        # Removing the search bar.
        self.quizBrowserSearchLabel.destroy()
        self.quizBrowserSearchEntry.destroy()
        # Removing the create/import quiz buttons.
        self.createQuizButton.destroy()
        self.importQuizButton.destroy()
        self.statisticsViewButton.destroy()
        # Removing the filters.
        self.filterByExamBoardCombo.destroy()
        self.filterBySubjectCombo.destroy()
        self.filterByDifficultyCombo.destroy()
        # Removing the column headings for the synchronised lists.
        self.quizListLabelNames.destroy()
        self.quizListLabelSubject.destroy()
        self.quizListLabelExamBoard.destroy()
        self.quizListLabelBestAttempt.destroy()
        # Removing the scroll bar for the lists.
        self.quizListBoxScrollBar.destroy()
        # Removing the lists themselves.
        self.quizListBoxNames.destroy()
        self.quizListBoxSubject.destroy()
        self.quizListBoxExamBoard.destroy()
        self.quizListBoxBestAttempt.destroy()
        # Removing widget frames.
        self.quizBrowserSearchFrame.destroy()
        self.quizListFrame.destroy()
    
    def unloadSidePanel(self) -> None:
        """This removes all the widgets from the side panel."""
        # Deleting widgets in the side panel
        self.quizListSideName.destroy()
        self.quizListSideSubject.destroy()
        self.quizListSideExamboard.destroy()
        self.quizListSideTotalQuestions.destroy()
        self.quizListSideBestAttempt.destroy()
        # Deleting buttons in side panel
        self.quizListSideLaunchQuizButton.destroy()
        self.quizListSideEditQuizButton.destroy()
        self.quizListSideExportQuizButton.destroy()
        self.quizListSideDeleteQuizButton.destroy()
        # Removing widget frames
        self.quizListSideButtonFrame.destroy()
        self.quizListSidePanel.destroy()
    
    def selectQuiz(self) -> None:
        """This is run every time the user makes a change to the quiz currently selected in the list."""
        # This gets the currently selected entry in the list, as variable n
        n = -1
        # Get the currently selected list index, from which ever list has something selected.
        if(self.quizListBoxNames.curselection()):
            # If an element has been selected in the quiz name list.
            n = self.quizListBoxNames.curselection()[0]
        elif(self.quizListBoxSubject.curselection()):
            # If an element has been selected in the quiz subject list.
            n = self.quizListBoxSubject.curselection()[0]
        elif(self.quizListBoxExamBoard.curselection()):
            # If an element has been selected in the quiz exam board list.
            n = self.quizListBoxExamBoard.curselection()[0]
        elif(self.quizListBoxBestAttempt.curselection()):
            # If an element has been selected in the quiz best attempts list.
            n = self.quizListBoxBestAttempt.curselection()[0]
        # Converting the index to an integer, to prevent errors that could occur if it isn't already an integer.
        self.currentlySelectedQuiz = int(n)
        # This changes all the text labels on the right to the details of the currently selected quiz.
        self.quizListSideName.config(text = self.quizNames[self.currentlySelectedQuiz]) # Showing the quiz title
        if(self.quizSubjects[self.currentlySelectedQuiz]):
            # If the quiz has a subject, display it in the side panel.
            self.quizListSideSubject.config(text = self.subjectDictionary[self.quizSubjects[self.currentlySelectedQuiz]])
        else:
            # If the quiz has no subject set, clear the last quiz's subject text from the side panel.
            self.quizListSideSubject.config(text = "")
        if(self.quizExamboards[self.currentlySelectedQuiz]):
            # If the quiz has an exam board, display it in the side panel.
            self.quizListSideExamboard.config(text = self.examboardDictionary[self.quizExamboards[self.currentlySelectedQuiz]])
        else:
            # If the quiz has no exam board set, clear the last quiz's exam board text from the side panel.
            self.quizListSideExamboard.config(text = "")
        # Get the number of questions for the currently selected quiz.
        numberOfQuestions = self.quizQuestionNumbers[self.currentlySelectedQuiz]
        # Show the number of questions and the diffiuclty on two lines within the same label.
        self.quizListSideTotalQuestions.config(text = str(numberOfQuestions) + " question"
                                    + ("s" if numberOfQuestions != 1 else "") + " in this quiz.\nDifficulty: " + str(self.quizDifficulties[self.currentlySelectedQuiz]))
        # Find the best attempt for that quiz.
        bestAttempt = self.database.execute("SELECT * FROM `Results` WHERE `UserID`=? AND `QuizID`=? ORDER BY `Score` DESC, `TotalDuration` ASC;",
                                    float(self.currentUser.id), float(self.quizIDs[self.currentlySelectedQuiz]))
        if(bestAttempt and len(bestAttempt)):
            # If a best attempt has been set,
            timeInSeconds = bestAttempt[0][6]
            # Format the time it took to complete it.
            timeTakenString = (str(round(timeInSeconds // 60)) + "m " if timeInSeconds >= 60 else "") + (str(round((maths.ceil(timeInSeconds * 10) / 10) % 60, 1)) + "s" if round((maths.ceil(timeInSeconds * 10) / 10) % 60, 1) else "")
            # Show the best attempt's score and time taken.
            self.quizListSideBestAttempt.config(text = "Best score: " + str(round(bestAttempt[0][3] * 100, 1)) + "%\nTime taken: " + timeTakenString)
        else:
            # If no best attempt has been set, tell the user.
            self.quizListSideBestAttempt.config(text = "Not attempted yet.")
        # Re-enable all the buttons on the right, in case this is the first time running this method.
        self.quizListSideLaunchQuizButton.config(state = tk.NORMAL)
        self.quizListSideEditQuizButton.config(state = tk.NORMAL)
        self.quizListSideExportQuizButton.config(state = tk.NORMAL)
        self.quizListSideDeleteQuizButton.config(state = tk.NORMAL)
    
    def scrollbarCommand(self, *args) -> None:
        """
        This method is for adjusting the list, which gets called by the scrollbar every time the scrollbar is moved.
        This method is called by tkinter (the GUI module), so I can't control what arguments are entered.
        """
        # Set all the lists' scroll positions.
        self.quizListBoxNames.yview(*args)
        self.quizListBoxSubject.yview(*args)
        self.quizListBoxExamBoard.yview(*args)
        self.quizListBoxBestAttempt.yview(*args)
    
    def scrollOnList(self, *args) -> None:
        """
        This method is called each time the user scrolls (often with the mouse's scroll wheel) with a list in-focus,
        and adjusts the other lists and the scrollbar based on how much is scrolled.
        This method is called by tkinter (the GUI module), so I can't control what arguments are entered.
        """
        # Set the scroll bar position.
        self.quizListBoxScrollBar.set(args[0], args[1])
        # Set all the visual lists' scroll positions.
        self.quizListBoxNames.yview("moveto", args[0])
        self.quizListBoxSubject.yview("moveto", args[0])
        self.quizListBoxExamBoard.yview("moveto", args[0])
        self.quizListBoxBestAttempt.yview("moveto", args[0])
    
    def launchQuiz(self) -> None:
        """This launches the quiz window for the currently selected quiz."""
        # Import the quiz and quizGui files from within the application's base directory.
        import quiz, quizGui
        # The following if statements check each list to see if an entry from any of the lists has been selected, and sets the number n to the selected row number.
        if(self.currentlySelectedQuiz == None):
            # An error message is shown if there are no rows selected, and this method returns so it doesn't try to load a quiz with id of negative one.
            tkmb.showerror("Launch quiz error", "No quiz selected to launch, please select a quiz by clicking on one from the list.")
            return
        
        print("Loading: " + self.quizNames[self.currentlySelectedQuiz]) # A debugging line, to check if the correct quiz is being loaded.
        # This loads the quiz from the database, the method .getQuiz() returns a Quiz object.
        quizObj = quiz.Quiz.getQuiz(self.quizIDs[self.currentlySelectedQuiz], self.database)
        # This then launches the window, passing the loaded quiz as an argument.
        quizGui.ActiveQuizDialog(self.tk, self, quizObj, self.currentUser)
    
    def editQuiz(self) -> None:
        """This launches the quiz window for the currently selected quiz."""
        # Import the quiz and quizCreator files from within the application's base directory.
        import quiz, quizCreator
        if(self.currentlySelectedQuiz == None):
            # An error message is shown if there are no rows selected, and this method returns so it doesn't try to load a quiz with id of negative one.
            # However, the button should be disabled if there is no quiz selected, so this is just a fallback.
            tkmb.showerror("Edit quiz error", "No quiz selected to launch, please select a quiz by clicking on one from the list.")
            return
        
        print("Editing quiz: " + self.quizNames[self.currentlySelectedQuiz]) # A debugging line, to check if the correct quiz is being loaded.
        # This loads the quiz from the database, the method .getQuiz() returns a Quiz object.
        try:
            quiz = quiz.Quiz.getQuiz(self.quizIDs[self.currentlySelectedQuiz], self.database)
            # This then launches the window, passing the loaded quiz as an argument.
            quizCreator.QuizEditorDialog(self.tk, self, quiz)
        except IndexError:
            # If the quiz isn't found in the database.
            tkmb.showerror("Error", "The selected quiz wasn't found in the database.", parent = self.tk)
        except:
            # If another error occurs.
            tkmb.showerror("Error", "The selected quiz is invalid or corrupt.", parent = self.tk)
    
    def createQuizButtonCommand(self) -> None:
        """This function is tied to the create quiz button and the create quiz option on the top menu."""
        # Import the quizCreator file from within the application's base directory.
        import quizCreator
        # Launches the quiz creator window
        quizCreator.QuizCreatorDialog(self.tk, self)
    
    def importQuizButtonCommand(self) -> None:
        """This function is tied to the import quiz button and the import quiz option on the top menu."""
        # Import the quiz file from within the application's base directory.
        import quiz
        # This launches your OS's file explorer, and lets you select a file that ends with ".xml".
        filename = tkfile.askopenfilename(filetypes = ["\"Quiz File\" .xml"], parent = self.tk, title = "Import Quiz")
        print(filename) # Line useful for debugging
        if(filename == None or filename == ""):
            # If the user didn't choose a file, usually by closing the window, we take no further action.
            return
        # Imports the quiz if the user has selected a file.
        quiz.Quiz.importQuiz(self, filename)
    
    def exportQuizButtonCommand(self):
        """This function is tied to the export quiz button."""
        # Import the quiz file from within the application's base directory.
        import quiz
        if(self.currentlySelectedQuiz == None):
            # An error message is shown if there are no rows selected, and this method returns so it doesn't try to export a quiz with id of negative one.
            # However, the button should be disabled if there is no quiz selected, so this is just a fallback.
            tkmb.showerror("Export quiz error", "No quiz selected to export, please select a quiz by clicking on one from the list.")
            return
        
        print("Exporting quiz: " + self.quizNames[self.currentlySelectedQuiz]) # A debugging line, to check if the correct quiz is being exported.
        # This loads the quiz from the database, the method .getQuiz() returns a Quiz object.
        try:
            quiz = quiz.Quiz.getQuiz(self.quizIDs[self.currentlySelectedQuiz], self.database)
            # This then launches the window, passing the loaded quiz as an argument.
            # This launches your OS's file explorer, and lets you select a file that ends with ".xml".
            filename = tkfile.asksaveasfilename(filetypes = ["\"Quiz File\" .xml"], parent = self.tk, title = "Export Quiz")
            print(filename) # Line useful for debugging
            if(filename == None or filename == ""):
                # If the user didn't choose a file, usually by closing the window, we take no further action.
                return
            # Exports the quiz if the user has selected a save location.
            quiz.exportQuiz(self, filename)
        except IndexError:
            # If the quiz isn't found in the database.
            tkmb.showerror("Error", "The selected quiz wasn't found in the database.", parent = self.tk)
    
    def deleteQuizButtonCommand(self):
        """This function is tied to the delete quiz button."""
        # Get the name and ID of the quiz being deleted.
        quizName = self.quizNames[self.currentlySelectedQuiz]
        quizID = self.quizIDs[self.currentlySelectedQuiz]
        # Ask user if they are sure, return if they say no.
        if(not tkmb.askyesno("Delete Quiz", "Are you sure you want to delete the quiz \"" + quizName + "\"? Quiz is deleted for all users and all past results will be deleted too.", parent = self.tk)):
            return
        # Delete the quiz's questions.
        self.database.execute("DELETE FROM `Questions` WHERE `QuizID` = ?;", float(quizID))
        # Remove the quiz's results.
        self.database.execute("DELETE FROM `Results` WHERE `QuizID` = ?;", float(quizID))
        # Then delete the quiz from the database.
        self.database.execute("DELETE FROM `Quizzes` WHERE `QuizID` = ?;", float(quizID))
        # Refresh the quiz browser list.
        self.refreshList()
    
    def userSettings(self) -> None:
        """This launches the user settings window, if there is a user logged in."""
        if(self.currentUser):
            # If a user is logged in, launch the window. This loads the userGui file from the base directory of the application.
            import userGui
            userGui.UserSettingsDialog(self.tk, self)
        else:
            # If the user has not logged in, then display an error message to the user.
            tkmb.showerror("User error", "No user currently selected, can't change user settings.")
    
    def switchUser(self) -> None:
        """This unloads the quiz browser and displays the select user screen again."""
        if(self.state != MainWindowStates.quizBrowser):
            # If the user isn't on the quiz browser, stop executing this subroutine.
            return
        # Change the window's state.
        self.state = MainWindowStates.login
        # Log the user out.
        self.currentUser = None
        # Remove all the quiz browser's visual elements, except the menu along the top.
        self.unloadQuizBrowserScreen()
        self.unloadSidePanel()
        # Then load the login screen again.
        self.loadLoginScreen()
    
    def launchStatistics(self) -> None:
        """This loads the statistics dialog, if there is a user logged in."""
        if(self.currentUser):
            # If a user is logged in, launch the window. This loads the statsGui file from the base directory of the application.
            import statsGui
            statsGui.StatisticsDialog(self.tk, self)
        else:
            # If the user isn't logged in, display an error.
            tkmb.showerror("User error", "No user currently selected, can't show user statistics.")
    
    def endApplication(self) -> None:
        """Called when the application is ending."""
        print("Application closing...")
        # Change the state.
        self.state = MainWindowStates.closing
        # Destroy the root window.
        self.tk.destroy()

def startGUI() -> None:
    """This method launches the application. This is called by default if this file is run directly and not imported as a module."""
    print("Building GUI...")
    # Creates the window
    master = tk.Tk()
    # This loads the MainApp class and loads all the graphical elements.
    app = MainMenu(master)
    print("Finished building GUI.")
    # The following try-except blocks are to catch any errors during runtime so the program can continue running to close the database connection correctly.
    # This is to try and prevent corrupting the database or failing to save any data that should have been saved during a session of application use.
    try:
        # This line makes the program continue running, as it is an interface-based program and needs to stay running for the user to use the application.
        master.mainloop()
    except:
        # The following code gets the error message and prints it as an error. The two following modules are necessary to fetch and format the error and stack trace.
        import traceback
        import sys
        # Show the error as a message box to the user.
        tkmb.showerror("Error occured", traceback.format_exc() + "\n\n" + sys.stderr, parent = master)
        # Also, print it to the console window as well.
        print(traceback.format_exc() + "\n\n" + sys.stderr)
    # This will run even if the app ends in a crash, as most errors should be caught above.
    app.database.dispose()

if(__name__ == "__main__"):
    # This will only run if this file is run directly. It will not run if this file is imported as a module.
    startGUI()
