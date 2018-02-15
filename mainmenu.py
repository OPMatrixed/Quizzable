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
import math

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

class MainApp(object):
    appName = "Quizzable"
    appVersion = "Alpha v0.6"
    def __init__(self, tkobj: tk.Tk) -> None:
        """
        This method is called when MainApp is initialised as a variable, and passes in tkobj e.g. "MainApp(app)"
        Arguments:
        tkobj is the window object
        """
        self.tk = tkobj
        # This sets the default dimensions of the window, 800 pixels wide by 600 pixels high.
        self.tk.geometry("800x600")
        # This sets the minimum dimensions of the window, 700 pixels wide by 350 pixels high.
        self.tk.minsize(width = 700, height = 350)
        # This sets the title of the application
        self.tk.title("Home - " + MainApp.appName + " - " + MainApp.appVersion)
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
        
        self.examboardDictionary = {}
        # This queries the database to get the names of the exam boards.
        examboardQueryResults = self.database.execute("SELECT * FROM `Examboards`;")
        if(examboardQueryResults):
            for i in examboardQueryResults:
                self.examboardDictionary[i[0]] = i[1]
        
        self.subjectDictionary = {}
        # This queries the database to get the names of the subjects.
        subjectQueryResults = self.database.execute("SELECT * FROM `Subjects`;")
        if(subjectQueryResults):
            for i in subjectQueryResults:
                self.subjectDictionary[i[0]] = i[1]
        # Inverse dictionaries for backwards lookups
        self.inverseSubjectDictionary = {v: k for k, v in self.subjectDictionary.items()}
        self.inverseExamboardDictionary = {v: k for k, v in self.examboardDictionary.items()}
        # The quiz the user has currently selected, starts off as None.
        self.currentlySelectedQuiz = None
    
    def createTitleBarMenu(self) -> None:
        """
        This will add the menu bar to the top of the window.
        Returns nothing.
        This imports the userGui module from the application directory, which is used for the user settings dialog.
        It also imports statsGui, which has the statistics dialog.
        """
        import userGui
        import statsGui
        
        # Creating the menu object.
        self.menuBar = tk.Menu(self.tk)
        
        # tearoff = 0 means that the drop-down can't be "ripped off", and be turned into its own little mini-dialog window.
        # This code is the "User" drop-down menu.
        self.userMenu = tk.Menu(self.menuBar, tearoff = 0)
        # userGui.UserCreateDialog() makes a Create User window, and it is passed as a lambda statement as arguments have to be passed.
        self.userMenu.add_command(label = "Create New User", command = lambda: userGui.UserCreateDialog(self.tk, self))
        self.userMenu.add_command(label = "User Settings", command = self.userSettings)
        self.userMenu.add_command(label = "Change User", command = self.switchUser)
        
        # This is the subjects & exam boards drop-down.
        self.subjectsAndExamBoardsMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.subjectsAndExamBoardsMenu.add_command(label = "Edit Subject List") # TODO
        self.subjectsAndExamBoardsMenu.add_command(label = "Edit Exam Board List") # TODO
        
        # This is the quiz drop-down, and handles creating quizzes and import quizzes.
        self.quizMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.quizMenu.add_command(label = "Create a Quiz", command = self.createQuizButtonCommand)
        self.quizMenu.add_command(label = "Import a Quiz", command = self.importQuizButtonCommand)
        
        # Adding the above sub-menus to the main menu bar.
        self.menuBar.add_cascade(label = "Quiz Management", menu = self.quizMenu)
        self.menuBar.add_cascade(label = "User", menu = self.userMenu)
        self.menuBar.add_cascade(label = "Subjects & Exam Boards", menu = self.subjectsAndExamBoardsMenu)
        
        self.menuBar.add_command(label = "Statistics", command = lambda: statsGui.StatisticsDialog(self.tk, self))
        
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
        self.tk.grid_columnconfigure(0, weight = 2)
        self.tk.grid_columnconfigure(1, weight = 1)
        self.tk.grid_columnconfigure(2, weight = 2)
        self.tk.grid_rowconfigure(0, weight = 3)
        self.tk.grid_rowconfigure(1, weight = 2)
        self.tk.grid_rowconfigure(2, weight = 1)
        self.tk.grid_rowconfigure(3, weight = 2)
        self.tk.grid_rowconfigure(4, weight = 1)
        self.tk.grid_rowconfigure(5, weight = 2)
        self.tk.grid_rowconfigure(6, weight = 2)
        self.tk.grid_rowconfigure(7, weight = 1)
        # Login screen heading text
        self.loginLabel = tk.Label(self.tk, text="User Selection", font = headerFont)
        
        userList = []
        # This queries the database to get the usernames of all the users.
        userQueryResults = self.database.execute("SELECT `Username` FROM `Users`;")
        if(userQueryResults):
            for i in userQueryResults:
                userList.append(i[0])
        else:
            userList = ["No users created, click \"Create User\""]
        
        # The user selection combobox (drop-down list).
        self.loginComboUser = ttk.Combobox(self.tk, state = "readonly", values = userList)
        # The "login" button, which selects the user currently selected in the combobox.
        self.loginSelectUserButton = tk.Button(self.tk, text = "Select User", bg = "#EAEAEA", border = 3, relief = tk.GROOVE, command = self.selectUser)
        # The create user button, which launches the Create User box.
        self.loginCreateUserButton = tk.Button(self.tk, text = "Create User", bg = "#DFDFDF", border = 3, relief = tk.GROOVE, command = lambda: userGui.UserCreateDialog(self.tk, self))
        # Positioning the above elements in the grid layout.
        self.loginLabel.grid(row = 1, column = 1)
        self.loginComboUser.grid(row = 3, column = 1, sticky = tk.W+tk.E+tk.N+tk.S)
        self.loginSelectUserButton.grid(row = 5, column = 1, sticky = tk.W+tk.E+tk.N+tk.S)
        self.loginCreateUserButton.grid(row = 6, column = 1, sticky = tk.W+tk.E+tk.N+tk.S)
    
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
        self.tk.grid_rowconfigure(0, weight = 0)
        self.tk.grid_rowconfigure(1, weight = 0)
        self.tk.grid_rowconfigure(2, weight = 0)
        self.tk.grid_rowconfigure(3, weight = 0)
        self.tk.grid_rowconfigure(4, weight = 0)
        self.tk.grid_rowconfigure(5, weight = 0)
        self.tk.grid_rowconfigure(6, weight = 0)
        self.tk.grid_rowconfigure(7, weight = 0)
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
        self.state = MainWindowStates.quizBrowser
        # Configuring the window and the window grid. This grid has 4 rows and 4 columns.
        self.tk.title("Quiz Browser - " + MainApp.appName + " - " + MainApp.appVersion)
        self.tk.grid_rowconfigure(0, weight = 0, minsize = 40)
        self.tk.grid_rowconfigure(1, weight = 0, minsize = 40)
        self.tk.grid_rowconfigure(2, weight = 1)
        self.tk.grid_rowconfigure(3, weight = 1)
        self.tk.grid_columnconfigure(0, weight = 1)
        self.tk.grid_columnconfigure(1, weight = 1)
        self.tk.grid_columnconfigure(2, weight = 1)
        self.tk.grid_columnconfigure(3, weight = 1, minsize = 200)
        
        # Adding the search box widget.
        # I create a frame here, as I want the "Search:" text and the text entry to behave like a single element spanning over 2 columns in the window grid.
        self.quizBrowserSearchFrame = tk.Frame(self.tk)
        # Frame grid configuration, 2 columns and 1 row.
        self.quizBrowserSearchFrame.grid_columnconfigure(0, weight = 1)
        self.quizBrowserSearchFrame.grid_columnconfigure(1, weight = 4)
        self.quizBrowserSearchFrame.grid_rowconfigure(0, weight = 1)
        # The search text preceding the text entry box.
        self.quizBrowserSearchLabel = tk.Label(self.quizBrowserSearchFrame, text="Search:")
        self.quizBrowserSearchLabel.grid(row = 0, column = 0, sticky = tk.E)
        # The actual search bar. This will be tied to an event later which updates the search after each letter is typed.
        self.quizBrowserSearchEntry = tk.Entry(self.quizBrowserSearchFrame, width = 10)
        self.quizBrowserSearchEntry.bind("<Key>", lambda e: threading.Timer(0.1, self.applyFilters).start())
        self.quizBrowserSearchEntry.grid(row = 0, column = 1, sticky=tk.W+tk.E)
        self.quizBrowserSearchFrame.grid(row = 0, column = 0, columnspan = 2, sticky=tk.W+tk.E)
        
        # Create a Quiz and Import a Quiz Buttons
        self.createQuizButton = tk.Button(self.tk, text = "Create a Quiz", command = self.createQuizButtonCommand)
        self.importQuizButton = tk.Button(self.tk, text = "Import a Quiz", command = self.importQuizButtonCommand)
        self.createQuizButton.grid(row = 0, column = 2)
        self.importQuizButton.grid(row = 0, column = 3)
        # The quiz filters, as comboboxes. They default to having the text "Filter by ...", but after selecting another value they can't go back to "Filter by ..."
        # To remove the filter after selecting a value for the filter, the user must select the combobox and select "No filter".
        self.filterByExamBoardCombo = ttk.Combobox(self.tk, state = "readonly", values = ["No filter"] + [i for i in self.examboardDictionary.values()])
        self.filterBySubjectCombo = ttk.Combobox(self.tk, state = "readonly", values = ["No filter"] + [i for i in self.subjectDictionary.values()])
        self.filterByDifficultyCombo = ttk.Combobox(self.tk, state = "readonly", values = ["No filter","1","2","3","4","5",
                                                    "2 and above","3 and above","4 and above","2 and below","3 and below","4 and below"])
        self.filterByExamBoardCombo.set("Filter by exam board")
        self.filterBySubjectCombo.set("Filter by subject")
        self.filterByDifficultyCombo.set("Filter by difficulty")
        # Binding the comboboxes to update the list when an option in one of the dropdowns is selected.
        self.filterByExamBoardCombo.bind("<<ComboboxSelected>>", self.applyFilters)
        self.filterBySubjectCombo.bind("<<ComboboxSelected>>", self.applyFilters)
        self.filterByDifficultyCombo.bind("<<ComboboxSelected>>", self.applyFilters)
        # Positioning of the filter comboboxes. All fit on the same row.
        self.filterByExamBoardCombo.grid(row = 1, column = 0, sticky=tk.W+tk.E+tk.N+tk.S) # Sticky just makes the element stretch in certain directions.
        self.filterBySubjectCombo.grid(row = 1, column = 1, sticky=tk.W+tk.E+tk.N+tk.S) # tk.N+tk.S means up and down (North and South), tk.W+tk.E means West and East
        self.filterByDifficultyCombo.grid(row = 1, column = 2, sticky=tk.W+tk.E+tk.N+tk.S) # Adding the directions up makes it expand in all the directions you specify.
        # Start of frame box that contains the lists.
        self.quizListFrame = tk.Frame(self.tk)
        # The frame's grid configuration.
        self.quizListFrame.grid_columnconfigure(0, weight = 3, minsize = 240)
        self.quizListFrame.grid_columnconfigure(1, weight = 1)
        self.quizListFrame.grid_columnconfigure(2, weight = 1)
        self.quizListFrame.grid_columnconfigure(3, weight = 1)
        self.quizListFrame.grid_rowconfigure(1, weight = 1)
        # The column headings for the synchronised lists.
        self.quizListLabelNames = tk.Label(self.quizListFrame, text = "Quiz Name")
        self.quizListLabelSubject = tk.Label(self.quizListFrame, text = "Subject")
        self.quizListLabelExamBoard = tk.Label(self.quizListFrame, text = "Examboard")
        self.quizListLabelBestAttempt = tk.Label(self.quizListFrame, text = "Last Attempt")
        # The positions of the column headings, all on the same row.
        self.quizListLabelNames.grid(row = 0, column = 0)
        self.quizListLabelSubject.grid(row = 0, column = 1)
        self.quizListLabelExamBoard.grid(row = 0, column = 2)
        self.quizListLabelBestAttempt.grid(row = 0, column = 3)
        
        # The scroll bar for the lists.
        self.quizListBoxScrollBar = tk.Scrollbar(self.quizListFrame, command = self.scrollbarCommand)
        self.quizListBoxScrollBar.grid(row = 1, column = 4, sticky=tk.N+tk.S)
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
        # Bind selecting an entry on the list to the self.selectQuiz() method
        self.quizListBoxNames.bind("<Button-1>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxSubject.bind("<Button-1>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxExamBoard.bind("<Button-1>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxBestAttempt.bind("<Button-1>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxNames.bind("<Key>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxSubject.bind("<Key>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxExamBoard.bind("<Key>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        self.quizListBoxBestAttempt.bind("<Key>", lambda e: threading.Timer(0.1, self.selectQuiz).start())
        
        self.refreshList()
        
        self.quizListFrame.grid(row = 2, column = 0, columnspan = 3, rowspan = 2, sticky = tk.W+tk.E+tk.N+tk.S)
        # End of lists frame.
        self.loadSidePanel() # This loads the labels and buttons to the right of the main list.
    
    def refreshList(self):
        self.allQuizzes = [list(i) + [self.database.execute("SELECT * FROM `Results` WHERE `UserID` = ? AND `QuizID` = ? ORDER BY `Score` DESC;", float(self.currentUser.id), float(i[0]))]
                                for i in self.database.execute("SELECT * FROM `Quizzes`;")]
        self.applyFilters()
    
    def applyFilters(self, e = None):
        if(self.state != MainWindowStates.quizBrowser):
            return
        
        startTime = time.clock()
        
        searchQuery = self.quizBrowserSearchEntry.get().lower()
        subjectText = self.filterBySubjectCombo.get()
        examBoardText = self.filterByExamBoardCombo.get()
        difficultyText = self.filterByDifficultyCombo.get()
        
        quizList = self.allQuizzes[:]
        if(not subjectText == "Filter by subject" and not subjectText == "No filter"):
            x = 0
            allowedSubject = self.inverseSubjectDictionary[subjectText]
            while x < len(quizList):
                if(quizList[x][2] != allowedSubject):
                    del quizList[x]
                else:
                    x += 1
        if(not examBoardText == "Filter by exam board" and not examBoardText == "No filter"):
            x = 0
            allowedExamBoard = self.inverseExamboardDictionary[examBoardText]
            while x < len(quizList):
                if(quizList[x][3] != allowedExamBoard):
                    del quizList[x]
                else:
                    x += 1
        if(not difficultyText == "Filter by difficulty" and not difficultyText == "No filter"):
            if(len(difficultyText) == 1):
                x = 0
                allowedDifficulty = int(difficultyText[0])
                while x < len(quizList):
                    if(quizList[x][3] != allowedDifficulty):
                        del quizList[x]
                    else:
                        x += 1
            elif(difficultyText.endswith("above")):
                x = 0
                allowedDifficulty = int(difficultyText[0])
                while x < len(quizList):
                    if(quizList[x][3] < allowedDifficulty):
                        del quizList[x]
                    else:
                        x += 1
            else:
                x = 0
                allowedDifficulty = int(difficultyText[0])
                while x < len(quizList):
                    if(quizList[x][3] > allowedDifficulty):
                        del quizList[x]
                    else:
                        x += 1
        
        # Ranking algorithm
        if(len(searchQuery.strip())):
            searchWords = searchQuery.split(" ")
            quizRankings = {}
            for i in range(len(quizList)):
                score = 0
                for k in searchWords:
                    for j in quizList[i][1].split(" "):
                        score += 2 * math.pow(difflib.SequenceMatcher(None, k, j).ratio(), 3)
                        score += j.count(k)
                    for j in quizList[i][5].split(","):
                        score += 2 * math.pow(difflib.SequenceMatcher(None, k, j).ratio(), 4)
                quizRankings[i] = score / (1 + quizList[i][1].count(" ") + quizList[i][5].count(","))
            counter = collections.Counter(quizRankings)
        
        # Clear the lists
        self.quizListBoxNames.delete(0, tk.END)
        self.quizListBoxSubject.delete(0, tk.END)
        self.quizListBoxExamBoard.delete(0, tk.END)
        self.quizListBoxBestAttempt.delete(0, tk.END)

        self.quizIDs = []
        self.quizNames = []
        self.quizSubjects = []
        self.quizExamboards = []
        self.quizQuestionNumbers = []
        self.quizDifficulties = []
        self.quizTags = {}
        
        if(len(searchQuery.strip())):
            for j in counter.most_common(200):
                i = quizList[j[0]]
                self.quizIDs.append(i[0])
                self.quizNames.append(i[1])
                self.quizSubjects.append(i[2])
                self.quizExamboards.append(i[3])
                self.quizQuestionNumbers.append(i[4])
                self.quizDifficulties.append(i[6])
                self.quizTags[i[0]] = i[5].split(",") if i[5] else []
                # This is adds each quiz to each of the lists.
                self.quizListBoxNames.insert(tk.END, i[1])
                self.quizListBoxSubject.insert(tk.END, self.subjectDictionary.get(i[2], ""))
                self.quizListBoxExamBoard.insert(tk.END, self.examboardDictionary.get(i[3], ""))
                
                if(i[7] and len(i[7])):
                    self.quizListBoxBestAttempt.insert(tk.END, str(round(i[7][0][3] * 100, 1)) + "% - " + str(round(i[7][0][6], 1)) + "s")
                else:
                    self.quizListBoxBestAttempt.insert(tk.END, "Not Attempted")
        else:
            # This goes through each quiz in the database and adds it to these lists which will be used in searching/filtering.
            for j in range(min(200, len(quizList))):
                i = quizList[j]
                self.quizIDs.append(i[0])
                self.quizNames.append(i[1])
                self.quizSubjects.append(i[2])
                self.quizExamboards.append(i[3])
                self.quizQuestionNumbers.append(i[4])
                self.quizDifficulties.append(i[6])
                self.quizTags[i[0]] = i[5].split(",") if i[5] else []
                # This is adds each quiz to each of the lists.
                self.quizListBoxNames.insert(tk.END, i[1])
                self.quizListBoxSubject.insert(tk.END, self.subjectDictionary.get(i[2], ""))
                self.quizListBoxExamBoard.insert(tk.END, self.examboardDictionary.get(i[3], ""))
                if(i[7] and len(i[7])):
                    self.quizListBoxBestAttempt.insert(tk.END, str(round(i[7][0][3] * 100, 1)) + "% - " + str(round(i[7][0][6], 1)) + "s")
                else:
                    self.quizListBoxBestAttempt.insert(tk.END, "Not Attempted")
        
        print("Search and filter took: " + str(round(time.clock() - startTime, 3)) + "s")
    
    def loadSidePanel(self) -> None:
        """
        This method loads the side panel to the Quiz List screen, it contains the quiz details of the currently selected quiz,
        it also contains the buttons for doing actions on the quiz, e.g. launching/editing the selected quiz.
        """
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
        # End of Frame
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
        self.quizListSideLaunchQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Launch Quiz", padx = 18, pady = 8, command = self.launchQuiz, state = tk.DISABLED)
        self.quizListSideEditQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Edit Quiz", padx = 18, pady = 8, command = self.editQuiz, state = tk.DISABLED)
        self.quizListSideExportQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Export Quiz", padx = 18, pady = 8, state = tk.DISABLED)
        self.quizListSideDeleteQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Delete Quiz", padx = 18, pady = 8, state = tk.DISABLED)
        # The positioning for the buttons above.
        self.quizListSideLaunchQuizButton.grid(row = 0, column = 0)
        self.quizListSideEditQuizButton.grid(row = 1, column = 0)
        self.quizListSideExportQuizButton.grid(row = 2, column = 0)
        self.quizListSideDeleteQuizButton.grid(row = 3, column = 0)
        # Placing the button frame.
        self.quizListSideButtonFrame.grid(row = 3, column = 3, sticky = tk.W+tk.E+tk.N+tk.S)
    
    def unloadQuizBrowserScreen(self):
        """This removes all the widgets off the quiz browser screen, in case the login screen needs to be displayed, or potentially the quiz browser needs to re-load."""
        # Resetting the grid configuration.
        self.tk.grid_rowconfigure(0, weight = 0, minsize = 0)
        self.tk.grid_rowconfigure(1, weight = 0, minsize = 0)
        self.tk.grid_rowconfigure(2, weight = 0)
        self.tk.grid_rowconfigure(3, weight = 0)
        self.tk.grid_columnconfigure(0, weight = 0)
        self.tk.grid_columnconfigure(1, weight = 0)
        self.tk.grid_columnconfigure(2, weight = 0)
        self.tk.grid_columnconfigure(3, weight = 0, minsize = 0)
        
        # The search bar
        self.quizBrowserSearchLabel.destroy()
        self.quizBrowserSearchEntry.destroy()
        # Create/import quiz buttons
        self.createQuizButton.destroy()
        self.importQuizButton.destroy()
        # Filters
        self.filterByExamBoardCombo.destroy()
        self.filterBySubjectCombo.destroy()
        self.filterByDifficultyCombo.destroy()
        # The column headings for the synchronised lists.
        self.quizListLabelNames.destroy()
        self.quizListLabelSubject.destroy()
        self.quizListLabelExamBoard.destroy()
        self.quizListLabelBestAttempt.destroy()
        # The scroll bar for the lists.
        self.quizListBoxScrollBar.destroy()
        # The lists
        self.quizListBoxNames.destroy()
        self.quizListBoxSubject.destroy()
        self.quizListBoxExamBoard.destroy()
        self.quizListBoxBestAttempt.destroy()
        # Removing widget frames
        self.quizBrowserSearchFrame.destroy()
        self.quizListFrame.destroy()
    
    def unloadSidePanel(self):
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
    
    def selectQuiz(self, *args) -> None:
        """This is run every time the user makes a change to the quiz currently selected in the list."""
        # This gets the currently selected entry in the list, as variable n
        n = -1
        if(self.quizListBoxNames.curselection()):
            n = self.quizListBoxNames.curselection()[0]
        elif(self.quizListBoxSubject.curselection()):
            n = self.quizListBoxSubject.curselection()[0]
        elif(self.quizListBoxExamBoard.curselection()):
            n = self.quizListBoxExamBoard.curselection()[0]
        elif(self.quizListBoxBestAttempt.curselection()):
            n = self.quizListBoxBestAttempt.curselection()[0]
        self.currentlySelectedQuiz = int(n)
        # This changes all the text labels on the right to the details of the currently selected quiz.
        self.quizListSideName.config(text = self.quizNames[self.currentlySelectedQuiz])
        if(self.quizSubjects[self.currentlySelectedQuiz]):
            self.quizListSideSubject.config(text = self.subjectDictionary[self.quizSubjects[self.currentlySelectedQuiz]])
        else:
            self.quizListSideSubject.config(text = "")
        if(self.quizExamboards[self.currentlySelectedQuiz]):
            self.quizListSideExamboard.config(text = self.examboardDictionary[self.quizExamboards[self.currentlySelectedQuiz]])
        else:
            self.quizListSideExamboard.config(text = "")
        numberOfQuestions = self.quizQuestionNumbers[self.currentlySelectedQuiz]
        self.quizListSideTotalQuestions.config(text = str(numberOfQuestions) + " question"
                                    + ("s" if numberOfQuestions != 1 else "") + " in this quiz.\nDifficulty: " + str(self.quizDifficulties[self.currentlySelectedQuiz]))
        bestAttempt = self.database.execute("SELECT * FROM `Results` WHERE `UserID`=? AND `QuizID`=? ORDER BY `Score` DESC;",
                                    float(self.currentUser.id), float(self.quizIDs[self.currentlySelectedQuiz]))
        if(bestAttempt and len(bestAttempt)):
            self.quizListSideBestAttempt.config(text = "Best score: " + str(round(bestAttempt[0][3] * 100, 1)) + "%\nTime taken: " + str(round(bestAttempt[0][6], 1)) + "s")
        else:
            self.quizListSideBestAttempt.config(text = "Not attempted yet.")
        # Re-enable all the buttons on the right
        self.quizListSideLaunchQuizButton.config(state = tk.NORMAL)
        self.quizListSideEditQuizButton.config(state = tk.NORMAL)
        self.quizListSideExportQuizButton.config(state = tk.NORMAL)
        self.quizListSideDeleteQuizButton.config(state = tk.NORMAL)
    
    def scrollbarCommand(self, *args) -> None:
        """
        This method is for adjusting the list, which gets called by the scrollbar every time the scrollbar is moved.
        This method is called by tkinter (the GUI module), so I can't control what arguments are entered.
        """
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
        self.quizListBoxScrollBar.set(args[0], args[1])
        self.quizListBoxNames.yview("moveto", args[0])
        self.quizListBoxSubject.yview("moveto", args[0])
        self.quizListBoxExamBoard.yview("moveto", args[0])
        self.quizListBoxBestAttempt.yview("moveto", args[0])
    
    def launchQuiz(self) -> None:
        """This launches the quiz window for the currently selected quiz."""
        import quiz, quizGui
        # The following if statements check each list to see if an entry from any of the lists has been selected, and sets the number n to the selected row number.
        if(self.currentlySelectedQuiz == None):
            # An error message is shown if there are no rows selected, and this method returns so it doesn't try to load a quiz with id of negative one.
            tkmb.showerror("Launch quiz error", "No quiz selected to launch, please select a quiz by clicking on one from the list.")
            return
        
        print("Loading: " + self.quizNames[self.currentlySelectedQuiz]) # A debugging line, to check if the correct quiz is being loaded.
        # This loads the quiz from the database, the method .getQuiz() returns a Quiz object.
        quiz = quiz.Quiz.getQuiz(self.quizIDs[self.currentlySelectedQuiz], self.database)
        # This then launches the window, passing the loaded quiz as an argument.
        quizGui.ActiveQuizDialog(self.tk, self, quiz, self.currentUser)
    
    def editQuiz(self):
        """This launches the quiz window for the currently selected quiz."""
        import quiz, quizCreator
        # The following if statements check each list to see if an entry from any of the lists has been selected, and sets the number n to the selected row number.
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
        except Exception:
            # If another error occurs.
            tkmb.showerror("Error", "The selected quiz is invalid or corrupt.", parent = self.tk)
    
    def createQuizButtonCommand(self) -> None:
        """This function is tied to the create quiz button and the create quiz option on the top menu."""
        import quizCreator
        # Launches the quiz creator window
        quizCreator.QuizCreatorDialog(self.tk, self)
    
    def importQuizButtonCommand(self) -> None:
        """This function is tied to the import quiz button and the import quiz option on the top menu."""
        import quiz
        # This launches your OS's file explorer, and lets you select a file that ends with ".xml".
        filename = tkfile.askopenfilename(filetypes = ["\"Quiz File\" .xml"], parent = self.tk, title = "Import Quiz")
        print(filename) # Line useful for debugging
        if(filename == None or filename == ""):
            # If the user didn't choose a file, usually by closing the window, we take no further action.
            return
        # Imports the quiz if the user has selected a file.
        q = quiz.Quiz.importQuiz(self, filename)
        # TODO: Add imported quiz to quiz browser (if successful).
    
    def userSettings(self) -> None:
        """This launches the user settings window, if there is a user logged in."""
        if(self.currentUser):
            import userGui
            userGui.UserSettingsDialog(self.tk, self)
        else:
            tkmb.showerror("User error", "No user currently selected, can't change user settings.")
    
    def switchUser(self):
        """This unloads the quiz browser and displays the select user screen again."""
        if(self.state != MainWindowStates.quizBrowser):
            # If the user isn't on the quiz browser, stop executing this subroutine.
            return
        self.state = MainWindowStates.login
        self.currentUser = None
        self.unloadQuizBrowserScreen()
        self.unloadSidePanel()
        self.loadLoginScreen()
    
    def endApplication(self) -> None:
        """Called when the application is ending."""
        print("Application closing...")
        self.state = MainWindowStates.closing
        self.tk.destroy()

def startGUI() -> None:
    """This method launches the application. This is called by default if this file is run directly and not imported as a module."""
    print("Building GUI...")
    # Creates the window
    master = tk.Tk()
    # This loads the MainApp class and loads all the graphical elements.
    app = MainApp(master)
    print("Finished building GUI.")
    # The following try-except blocks are to catch any errors during runtime so the program can continue running to close the database connection correctly.
    # This is to try and prevent corrupting the database or failing to save any data that should have been saved during a session of application use.
    try:
        # This line makes the program continue running, as it is an interface-based program and needs to stay running for the user to use the application.
        master.mainloop()
    except:
        # The following code gets the error message and prints it as an error.
        import traceback
        import sys
        tkmb.showerror("Error occured", traceback.format_exc() + "\n\n" + sys.stderr, parent = master)
        print(traceback.format_exc() + "\n\n" + sys.stderr)
    # This will run even if the app ends in a crash, as most errors should be caught above.
    app.database.dispose()

if(__name__ == "__main__"):
    # This will only run if this file is run directly. It will not run if this file is imported as a module.
    startGUI()
