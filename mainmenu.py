# This file contains the code to design the main login screen, and also the main quiz list viewer.

# These imports load in the tkinter library, which is used to make windows and add widgets to those windows.
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

class MainWindowStates:
	# Stored in MainApp.state, it holds one of these integers, which corresponds to the state of the main window of the application.
	# This would be called an enumeration class in a language like Java, but as far as I know this is Python's closest equivalent.
	closing = 0
	login = 1
	questionlist = 2

class MainApp(object):
	appName = "Quizzable"
	appVersion = "Alpha v0.1"
	def __init__(self, tkobj):
		# This function is called when MainApp is initialised as a variable, and passes in tkobj e.g. "MainApp(app)"
		# This function techinally returns the object it is initalising (aka "self" in the context of this method), so it can be assigned to a variable.
		
		self.tk = tkobj
		# This sets the default dimensions of the window, 800 pixels wide by 600 pixels high.
		self.tk.geometry("800x600")
		# This sets the minimum dimensions of the window, 700 pixels wide by 350 pixels high.
		self.tk.minsize(width = 700, height = 350)
		# This sets the title of the 
		self.tk.title("Home - "+MainApp.appName+" - "+MainApp.appVersion)
		# This sets the state of the application, to keep track of what's on the main window.
		self.state = MainWindowStates.login
		# This gets changed once a user is selected.
		self.selectedUser = None
		# This loads the login screen on the main window.
		self.loadLoginScreen()
	
	def loadLoginScreen(self):
		# This method loads the elements of the login screen on to the main window.
		# No arguments or return values.
		
		# This import is a file in the base directory, and holds the CreateUserDialog class which is used here.
		import userGui
		# This is the specification of the header font.
		headerFont = tkfont.Font(family="Helvetica", size=28)
		
		# The following lines configure the "grid", on which elements are placed, to adjust the sizes of the rows and columns.
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
		self.loginLabel.grid(row = 1, column = 1)
		# The user selection combobox (drop-down list).
		self.loginComboUser = ttk.Combobox(self.tk, state="readonly", values=["No users created, click \"Create User\""])
		self.loginComboUser.grid(row = 3, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
		# The "login" button, which selects the user currently selected in the combobox.
		self.loginSelectUserButton = tk.Button(self.tk, text="Select User", bg="#EAEAEA", border=3, relief=tk.GROOVE, command = self.selectUser)
		self.loginSelectUserButton.grid(row = 5, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
		# The create user button, which launches the Create User box.
		self.loginCreateUserButton = tk.Button(self.tk, text="Create User", bg="#DFDFDF", border=3, relief=tk.GROOVE, command = lambda: userGui.UserDialog(self.tk, self))
		self.loginCreateUserButton.grid(row = 6, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
	
	def unloadLoginScreen(self):
		# This method removes all the elements off the login screen and resets the grid configuration
		# Basically, it cleans the window of elements so another screen can be loaded.
		
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
	
	def selectUser(self):
		# TODO: Get user from combobox
		#       Select that user
		self.unloadLoginScreen()
		self.loadQuizBrowserScreen()
	
	def loadQuizBrowserScreen(self):
		# This method loads the quiz browser screen onto the main window.
		# It takes no arguments and doesn't return anything.
		
		# Configuring the window and the window grid.
		self.tk.title("Quiz Browser - "+MainApp.appName+" - "+MainApp.appVersion)
		self.tk.grid_rowconfigure(0, weight = 0, minsize=40)
		self.tk.grid_rowconfigure(1, weight = 0, minsize=40)
		self.tk.grid_rowconfigure(2, weight = 1)
		self.tk.grid_rowconfigure(3, weight = 1)
		self.tk.grid_rowconfigure(4, weight = 1)
		self.tk.grid_rowconfigure(5, weight = 1)
		self.tk.grid_rowconfigure(6, weight = 1)
		self.tk.grid_columnconfigure(0, weight = 1)
		self.tk.grid_columnconfigure(1, weight = 1)
		self.tk.grid_columnconfigure(2, weight = 1)
		self.tk.grid_columnconfigure(3, weight = 1, minsize = 200)
		
		# Adding the search box widget.
		# I create a frame here, as I want the "Search:" text and the text entry to behave like a single element spanning over 2 columns in the window grid.
		self.quizBrowserSearchFrame = tk.Frame(self.tk)
		self.quizBrowserSearchFrame.grid_columnconfigure(0, weight = 1)
		self.quizBrowserSearchFrame.grid_columnconfigure(1, weight = 4)
		self.quizBrowserSearchFrame.grid_rowconfigure(0, weight = 1)
		self.quizBrowserSearchLabel = tk.Label(self.quizBrowserSearchFrame, text="Search:")
		self.quizBrowserSearchLabel.grid(row = 0, column = 0, sticky = tk.E)
		self.quizBrowserSearchEntry = tk.Entry(self.quizBrowserSearchFrame, width = 10)
		self.quizBrowserSearchEntry.grid(row = 0, column = 1, sticky=tk.W+tk.E)
		self.quizBrowserSearchFrame.grid(row = 0, column = 0, columnspan = 2, sticky=tk.W+tk.E)
		
		# Create a Quiz and Import a Quiz Buttons
		self.createQuizButton = tk.Button(self.tk, text="Create a Quiz")
		self.importQuizButton = tk.Button(self.tk, text="Import a Quiz")
		self.createQuizButton.grid(row = 0, column = 2)
		self.importQuizButton.grid(row = 0, column = 3)
		# The quiz filters, as comboboxes. They default to having the text "Filter by ...", but after selecting another value they can't go back to "Filter by ..."
		# To remove the filter after selecting a value for the filter, the user must select the combobox and select "No filter".
		self.filterByExamBoardCombo = ttk.Combobox(self.tk, state="readonly", values=["No filter"])
		self.filterByExamBoardCombo.set("Filter by exam board")
		self.filterBySubjectCombo = ttk.Combobox(self.tk, state="readonly", values=["No filter"])
		self.filterBySubjectCombo.set("Filter by subject")
		self.filterByDifficultyCombo = ttk.Combobox(self.tk, state="readonly", values=["No filter","1","2","3","4","5","2 and above","3 and above","4 and above","2 and below","3 and below","4 and below"])
		self.filterByDifficultyCombo .set("Filter by difficulty")
		self.filterByExamBoardCombo.grid(row = 1, column = 0, sticky=tk.W+tk.E+tk.N+tk.S) # Sticky just makes the element strech in certain directions.
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
		self.quizListLabelNames = tk.Label(self.quizListFrame, text="Quiz Name")
		self.quizListLabelSubject = tk.Label(self.quizListFrame, text="Subject")
		self.quizListLabelExamBoard = tk.Label(self.quizListFrame, text="Examboard")
		self.quizListLabelBestAttempt = tk.Label(self.quizListFrame, text="Last Attempt")
		self.quizListLabelNames.grid(row = 0, column = 0)
		self.quizListLabelSubject.grid(row = 0, column = 1)
		self.quizListLabelExamBoard.grid(row = 0, column = 2)
		self.quizListLabelBestAttempt.grid(row = 0, column = 3)
		# The scroll bar for the lists.
		self.quizListBoxScrollBar = tk.Scrollbar(self.quizListFrame, command = self.scrollbarCommand)
		self.quizListBoxScrollBar.grid(row = 1, column = 4, sticky=tk.N+tk.S)
		# The main Quizzes List is split up into four synchronised lists, due to the nature of the listbox in tkinter.
		# The Quiz Name goes in the first (biggest) column.
		self.quizListBoxNames = tk.Listbox(self.quizListFrame, yscrollcommand=self.scrollOnList)
		# The Subject goes in the second column.
		self.quizListBoxSubject = tk.Listbox(self.quizListFrame, yscrollcommand=self.scrollOnList)
		# The Exam Board goes in the thrird column.
		self.quizListBoxExamBoard = tk.Listbox(self.quizListFrame, yscrollcommand=self.scrollOnList)
		# The Best Attempt for each quiz goes in the fourth column.
		self.quizListBoxBestAttempt = tk.Listbox(self.quizListFrame, yscrollcommand=self.scrollOnList)
		self.quizListBoxNames.grid(row = 1, column = 0, sticky=tk.W+tk.E+tk.N+tk.S)
		self.quizListBoxSubject.grid(row = 1, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
		self.quizListBoxExamBoard.grid(row = 1, column = 2, sticky=tk.W+tk.E+tk.N+tk.S)
		self.quizListBoxBestAttempt.grid(row = 1, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
		
		for i in range(200): # This is an example entry generator for testing the quiz browser.
			# This is a temporary feature for testing the application's design.
			self.quizListBoxNames.insert(tk.END, "N"+str(i))
			self.quizListBoxSubject.insert(tk.END, "S"+str(i))
			self.quizListBoxExamBoard.insert(tk.END, "E"+str(i))
			self.quizListBoxBestAttempt.insert(tk.END, "B"+str(i))
		
		self.quizListFrame.grid(row = 2, column = 0, columnspan = 3, rowspan = 5, sticky=tk.W+tk.E+tk.N+tk.S)
		# End of lists frame.
		self.loadSidePanel() # This loads the labels and buttons to the right of the main list.
		
	def loadSidePanel(self):
		# This method loads the side panel to the Quiz List screen, it contains the quiz details of the currently selected quiz,
		# it also contains the buttons for doing actions on the quiz, e.g. launching/editing the selected quiz.
		self.quizListSidePanel = tk.Frame(self.tk)
		self.quizListSidePanel.grid_columnconfigure(0, weight = 1)
		# Text fields, these will be updated whenever a new quiz is selected on the list.
		self.quizListSideName = tk.Label(self.quizListSidePanel, text = "<Quiz Name>")
		self.quizListSideSubject = tk.Label(self.quizListSidePanel, text = "<Quiz Subject>")
		self.quizListSideExamboard = tk.Label(self.quizListSidePanel, text = "<Quiz Examboard>")
		self.quizListSideTotalQuestions = tk.Label(self.quizListSidePanel, text = "<Total number of questions>")
		self.quizListSideBestAttempt = tk.Label(self.quizListSidePanel, text = "<Quiz Best Attempt>")
		# Positioning of the text fields.
		self.quizListSideName.grid(row = 0, column = 0)
		self.quizListSideSubject.grid(row = 1, column = 0)
		self.quizListSideExamboard.grid(row = 2, column = 0)
		self.quizListSideTotalQuestions.grid(row = 3, column = 0)
		self.quizListSideBestAttempt.grid(row = 4, column = 0)
		
		# End of Frame
		self.quizListSidePanel.grid(row = 2, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
		# The buttons to do actions on the currently selected quiz.
		self.quizListSideLaunchQuizButton = tk.Button(self.tk, text = "Launch Quiz")
		self.quizListSideEditQuizButton = tk.Button(self.tk, text = "Edit Quiz")
		self.quizListSideExportQuizButton = tk.Button(self.tk, text = "Export Quiz")
		self.quizListSideDelteQuizButton = tk.Button(self.tk, text = "Delete Quiz")
		# The positioning for the buttons above.
		self.quizListSideLaunchQuizButton.grid(row = 3, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
		self.quizListSideEditQuizButton.grid(row = 4, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
		self.quizListSideExportQuizButton.grid(row = 5, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
		self.quizListSideDelteQuizButton.grid(row = 6, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
	
	def scrollbarCommand(self, *args):
		# This method is for adjusting the list, which gets called by the scrollbar everytime the scrollbar is moved.
		self.quizListBoxNames.yview(*args)
		self.quizListBoxSubject.yview(*args)
		self.quizListBoxExamBoard.yview(*args)
		self.quizListBoxBestAttempt.yview(*args)
	
	def scrollOnList(self, *args):
		# This method is called each time the user scrolls with a list in-focus,
		# and adjusts the other lists and the scrollbar based on how much is scrolled.
		self.quizListBoxScrollBar.set(args[0], args[1])
		self.quizListBoxNames.yview("moveto", args[0])
		self.quizListBoxSubject.yview("moveto", args[0])
		self.quizListBoxExamBoard.yview("moveto", args[0])
		self.quizListBoxBestAttempt.yview("moveto", args[0])

def startGUI():
	print("Building GUI...")
	# Creates the window
	master = tk.Tk()
	# Makes the program destroy the window when the X button in the top right is pressed.
	master.protocol("WM_DELETE_WINDOW", master.destroy)
	# This loads the MainApp class and loads all the graphical elements.
	MainApp(master)
	print("Finished building GUI.")
	# This makes the program continue running, as it is an interface-based program and needs to stay running for the user to use the application.
	master.mainloop()

if(__name__=="__main__"):
	# This will only run if this file is run directly. It will not run if imported as a module.
	startGUI()
