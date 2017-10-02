"""This file contains the code to design the main login screen, and also the main quiz list viewer."""

# These imports load in the tkinter library, which is used to make windows and add widgets to those windows.
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import tkinter.filedialog as tkfile

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
    appVersion = "Alpha v0.2"
    def __init__(self, tkobj: tk.Tk) -> None:
        """
        This method is called when MainApp is initialised as a variable, and passes in tkobj e.g. "MainApp(app)"
        Arguments:
        tkobj : tk.Tk  (The window object)
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
        self.selectedUser = None
        # This creates the database connection.
        self.database = database.DatabaseManager("QuizAppDatabase.accdb")
        # This creates the menu bar at the top of the window.
        self.createTitleBarMenu()
        # This loads the login screen on the main window.
        self.loadLoginScreen()
    
    def createTitleBarMenu(self) -> None: # TODO: Only show if there is a user selected.
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
        
        # This has the "Application" drop-down menu, which only contains one option at the moment.
        # tearoff = 0 means that the drop-down can't be "ripped off", and be turned into its own little mini-dialog window.
        self.appMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.appMenu.add_command(label = "Exit", command = self.endApplication)
        
        # This code is the "User" drop-down menu, of which the buttons are only active if a user is selected.
        self.userMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.userMenu.add_command(label = "Create New User", command = lambda: userGui.UserCreateDialog(self.tk, self))
        self.userMenu.add_command(label = "User Settings",   command = lambda: userGui.UserSettingsDialog(self.tk, self))
        self.userMenu.add_command(label = "Change User") # TODO
        
        # This is the subjects & exam boards drop-down.
        self.subjectsAndExamBoardsMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.subjectsAndExamBoardsMenu.add_command(label = "Edit Subject List") # TODO
        self.subjectsAndExamBoardsMenu.add_command(label = "Edit Exam Board List") # TODO
        
        # This is the quiz drop-down, and handles creating quizzes and import quizzes.
        self.quizMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.quizMenu.add_command(label = "Create a Quiz") # TODO
        self.quizMenu.add_command(label = "Import a Quiz", command = self.importQuizButtonCommand)
        
        # Adding the above sub-menus to the main menu bar.
        self.menuBar.add_cascade(label = "Quiz Management",        menu = self.quizMenu)
        self.menuBar.add_cascade(label = "User",                   menu = self.userMenu)
        self.menuBar.add_cascade(label = "Subjects & Exam Boards", menu = self.subjectsAndExamBoardsMenu)
        self.menuBar.add_cascade(label = "Application",            menu = self.appMenu)
        
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
        self.loginLabel = tk.Label(self.tk, text="User Selection", font=headerFont)
        # The user selection combobox (drop-down list).
        self.loginComboUser = ttk.Combobox(self.tk, state="readonly", values=["No users created, click \"Create User\""])
        # The "login" button, which selects the user currently selected in the combobox.
        self.loginSelectUserButton = tk.Button(self.tk, text="Select User", bg="#EAEAEA", border=3, relief=tk.GROOVE, command = self.selectUser)
        # The create user button, which launches the Create User box.
        self.loginCreateUserButton = tk.Button(self.tk, text="Create User", bg="#DFDFDF", border=3, relief=tk.GROOVE, command = lambda: userGui.UserCreateDialog(self.tk, self))
        # Positioning the above elements in the grid layout.
        self.loginLabel.grid(row = 1, column = 1)
        self.loginComboUser.grid(row = 3, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
        self.loginSelectUserButton.grid(row = 5, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
        self.loginCreateUserButton.grid(row = 6, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
    
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
        TODO: Get user from combobox
            Select that user
        This code is only temporary, so it allows you to see the app without the functionality being added yet.
        """
        self.unloadLoginScreen()
        self.loadQuizBrowserScreen()
    
    def loadQuizBrowserScreen(self) -> None:
        """
        This method loads the quiz browser screen onto the main window.
        It takes no arguments and doesn't return anything.
        """
        self.state = MainWindowStates.quizBrowser
        # Configuring the window and the window grid. This grid has 4 rows and 4 columns.
        self.tk.title("Quiz Browser - " + MainApp.appName + " - " + MainApp.appVersion)
        self.tk.grid_rowconfigure(0, weight = 0, minsize=40)
        self.tk.grid_rowconfigure(1, weight = 0, minsize=40)
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
        # The search text preceeding the text entry box.
        self.quizBrowserSearchLabel = tk.Label(self.quizBrowserSearchFrame, text="Search:")
        self.quizBrowserSearchLabel.grid(row = 0, column = 0, sticky = tk.E)
        # The actual search bar. This will be tied to an event later which updates the search after each letter is typed.
        self.quizBrowserSearchEntry = tk.Entry(self.quizBrowserSearchFrame, width = 10)
        self.quizBrowserSearchEntry.grid(row = 0, column = 1, sticky=tk.W+tk.E)
        self.quizBrowserSearchFrame.grid(row = 0, column = 0, columnspan = 2, sticky=tk.W+tk.E)
        
        # Create a Quiz and Import a Quiz Buttons
        self.createQuizButton = tk.Button(self.tk, text = "Create a Quiz")
        self.importQuizButton = tk.Button(self.tk, text = "Import a Quiz", command = self.importQuizButtonCommand)
        self.createQuizButton.grid(row = 0, column = 2)
        self.importQuizButton.grid(row = 0, column = 3)
        # The quiz filters, as comboboxes. They default to having the text "Filter by ...", but after selecting another value they can't go back to "Filter by ..."
        # To remove the filter after selecting a value for the filter, the user must select the combobox and select "No filter".
        self.filterByExamBoardCombo  = ttk.Combobox(self.tk, state = "readonly", values = ["No filter"])
        self.filterBySubjectCombo    = ttk.Combobox(self.tk, state = "readonly", values = ["No filter"])
        self.filterByDifficultyCombo = ttk.Combobox(self.tk, state = "readonly", values = ["No filter","1","2","3","4","5","2 and above","3 and above","4 and above","2 and below","3 and below","4 and below"])
        self.filterByExamBoardCombo.set ("Filter by exam board")
        self.filterBySubjectCombo.set   ("Filter by subject")
        self.filterByDifficultyCombo.set("Filter by difficulty")
        # Positioning of the filter comboboxes. All fit on the same row.
        self.filterByExamBoardCombo.grid (row = 1, column = 0, sticky=tk.W+tk.E+tk.N+tk.S) # Sticky just makes the element strech in certain directions.
        self.filterBySubjectCombo.grid   (row = 1, column = 1, sticky=tk.W+tk.E+tk.N+tk.S) # tk.N+tk.S means up and down (North and South), tk.W+tk.E means West and East
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
        self.quizListLabelNames       = tk.Label(self.quizListFrame, text = "Quiz Name")
        self.quizListLabelSubject     = tk.Label(self.quizListFrame, text = "Subject")
        self.quizListLabelExamBoard   = tk.Label(self.quizListFrame, text = "Examboard")
        self.quizListLabelBestAttempt = tk.Label(self.quizListFrame, text = "Last Attempt")
        # The positions of the column headings, all on the same row.
        self.quizListLabelNames.grid      (row = 0, column = 0)
        self.quizListLabelSubject.grid    (row = 0, column = 1)
        self.quizListLabelExamBoard.grid  (row = 0, column = 2)
        self.quizListLabelBestAttempt.grid(row = 0, column = 3)
        # The scroll bar for the lists.
        self.quizListBoxScrollBar = tk.Scrollbar(self.quizListFrame, command = self.scrollbarCommand)
        self.quizListBoxScrollBar.grid(row = 1, column = 4, sticky=tk.N+tk.S)
        # The main Quizzes List is split up into four synchronised lists, due to the nature of the listbox in tkinter.
        # The Quiz Name goes in the first (biggest) column.
        self.quizListBoxNames       = tk.Listbox(self.quizListFrame, yscrollcommand = self.scrollOnList)
        # The Subject goes in the second column.
        self.quizListBoxSubject     = tk.Listbox(self.quizListFrame, yscrollcommand = self.scrollOnList)
        # The Exam Board goes in the thrird column.
        self.quizListBoxExamBoard   = tk.Listbox(self.quizListFrame, yscrollcommand = self.scrollOnList)
        # The Best Attempt for each quiz goes in the fourth column.
        self.quizListBoxBestAttempt = tk.Listbox(self.quizListFrame, yscrollcommand = self.scrollOnList)
        # The positioning of the synchronized lists, all on the second row, and all taking as much space as possible in their grid cell using sticky = ...
        self.quizListBoxNames.grid      (row = 1, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.quizListBoxSubject.grid    (row = 1, column = 1, sticky = tk.W+tk.E+tk.N+tk.S)
        self.quizListBoxExamBoard.grid  (row = 1, column = 2, sticky = tk.W+tk.E+tk.N+tk.S)
        self.quizListBoxBestAttempt.grid(row = 1, column = 3, sticky = tk.W+tk.E+tk.N+tk.S)
        
        for i in range(200): # This is an example entry generator for testing the quiz browser.
            # This is a temporary feature for testing the application's design.
            self.quizListBoxNames.insert      (tk.END, "N"+str(i))
            self.quizListBoxSubject.insert    (tk.END, "S"+str(i))
            self.quizListBoxExamBoard.insert  (tk.END, "E"+str(i))
            self.quizListBoxBestAttempt.insert(tk.END, "B"+str(i))
        
        self.quizListFrame.grid(row = 2, column = 0, columnspan = 3, rowspan = 2, sticky=tk.W+tk.E+tk.N+tk.S)
        # End of lists frame.
        self.loadSidePanel() # This loads the labels and buttons to the right of the main list.
    
    def loadSidePanel(self) -> None:
        """
        This method loads the side panel to the Quiz List screen, it contains the quiz details of the currently selected quiz,
        it also contains the buttons for doing actions on the quiz, e.g. launching/editing the selected quiz.
        """
        self.quizListSidePanel = tk.Frame(self.tk)
        self.quizListSidePanel.grid_columnconfigure(0, weight = 1)
        # Text fields, these will be updated whenever a new quiz is selected on the list.
        self.quizListSideName           = tk.Label(self.quizListSidePanel, text = "<Quiz Name>")
        self.quizListSideSubject        = tk.Label(self.quizListSidePanel, text = "<Quiz Subject>")
        self.quizListSideExamboard      = tk.Label(self.quizListSidePanel, text = "<Quiz Examboard>")
        self.quizListSideTotalQuestions = tk.Label(self.quizListSidePanel, text = "<Total number of questions>")
        self.quizListSideBestAttempt    = tk.Label(self.quizListSidePanel, text = "<Quiz Best Attempt>")
        # Positioning of the text fields.
        self.quizListSideName.grid          (row = 0, column = 0)
        self.quizListSideSubject.grid       (row = 1, column = 0)
        self.quizListSideExamboard.grid     (row = 2, column = 0)
        self.quizListSideTotalQuestions.grid(row = 3, column = 0)
        self.quizListSideBestAttempt.grid   (row = 4, column = 0)
        
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
        self.quizListSideLaunchQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Launch Quiz", padx = 18, pady = 8, command = self.launchQuiz)
        self.quizListSideEditQuizButton   = tk.Button(self.quizListSideButtonFrame, text =   "Edit Quiz", padx = 18, pady = 8)
        self.quizListSideExportQuizButton = tk.Button(self.quizListSideButtonFrame, text = "Export Quiz", padx = 18, pady = 8)
        self.quizListSideDelteQuizButton  = tk.Button(self.quizListSideButtonFrame, text = "Delete Quiz", padx = 18, pady = 8)
        # The positioning for the buttons above.
        self.quizListSideLaunchQuizButton.grid(row = 0, column = 0)
        self.quizListSideEditQuizButton.grid  (row = 1, column = 0)
        self.quizListSideExportQuizButton.grid(row = 2, column = 0)
        self.quizListSideDelteQuizButton.grid (row = 3, column = 0)
        # Placing the button frame.
        self.quizListSideButtonFrame.grid(row = 3, column = 3, sticky = tk.W+tk.E+tk.N+tk.S)
    
    def scrollbarCommand(self, *args) -> None:
        """This method is for adjusting the list, which gets called by the scrollbar everytime the scrollbar is moved."""
        self.quizListBoxNames.yview      (*args)
        self.quizListBoxSubject.yview    (*args)
        self.quizListBoxExamBoard.yview  (*args)
        self.quizListBoxBestAttempt.yview(*args)
    
    def scrollOnList(self, *args) -> None:
        """
        This method is called each time the user scrolls (often with the mouse's scroll wheel) with a list in-focus,
        and adjusts the other lists and the scrollbar based on how much is scrolled.
        """
        self.quizListBoxScrollBar.set(args[0], args[1])
        self.quizListBoxNames.yview      ("moveto", args[0])
        self.quizListBoxSubject.yview    ("moveto", args[0])
        self.quizListBoxExamBoard.yview  ("moveto", args[0])
        self.quizListBoxBestAttempt.yview("moveto", args[0])
    
    def launchQuiz(self) -> None:
        """This launches the quiz window for the currently selected quiz."""
        import quiz, quizGui
        quiz = quiz.Quiz("Example Quiz", ["An Example"], "Example Subject", "Example Exam Board", 1, [])
        quizGui.ActiveQuizDialog(self.tk, self, quiz)
    
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
        q = quiz.Quiz.importQuiz(filename)
    
    def endApplication(self) -> None:
        """Called when the application is ending."""
        self.database.dispose()
        self.state = MainWindowStates.closing
        self.tk.destroy()

def startGUI() -> None:
    """This method launches the application. This is called by default if this file is run directly and not imported as a module."""
    print("Building GUI...")
    # Creates the window
    master = tk.Tk()
    # This loads the MainApp class and loads all the graphical elements.
    MainApp(master)
    print("Finished building GUI.")
    # This makes the program continue running, as it is an interface-based program and needs to stay running for the user to use the application.
    master.mainloop()

if(__name__=="__main__"):
    # This will only run if this file is run directly. It will not run if imported as a module.
    startGUI()
