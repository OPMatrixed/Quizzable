# This file will handle two screens specified on the design document:
# the user creation screen, and the user settings screen.

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

class UserCreateDialog(object):
	def __init__(self, toplevel, parent):
		# toplevel is the tkinter object of the parent window.
		# parent in the MainApp object, unless another dialog opens this window.
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
		self.headerFont = tkfont.Font(family="Helvetica", size=28)
		# The header itself.
		self.headerLabel = tk.Label(self.window, text = "Create User", font=self.headerFont)
		self.headerLabel.grid(row = 0, column = 0, columnspan=2)
		
		# The Labels/Text widgets to the left of the entry boxes/buttons with the name of the input expected on the right.
		self.usernameLabel = tk.Label(self.window, text = "Username:")
		self.defaultExamBoardLabel = tk.Label(self.window, text = "Default exam board:")
		self.timerSettingsLabel = tk.Label(self.window, text = "Timer settings:  NO TIMER")
		# These go on the first column (column 0)
		self.usernameLabel.grid(row = 1, column = 0)
		self.defaultExamBoardLabel.grid(row = 2, column = 0)
		self.timerSettingsLabel.grid(row = 3, column = 0)
		
		# The actual entry fields for the user settings.
		self.usernameEntry = tk.Entry(self.window, width = 20)
		# Examboard entry is a combobox. It gets the options from the examboards tabel in the database.
		self.defaultExamBoardEntry = ttk.Combobox(self.window, values=["No preference"])
		# The three timer button options represent three different timer settings. These are the only three, so I used buttons rather than drop down.
		self.timerButton1 = tk.Button(self.window, text = "No timer (easy)")
		self.timerButton2 = tk.Button(self.window, text = "Long timer (medium)")
		self.timerButton3 = tk.Button(self.window, text = "Short timer (hard)")
		# Each of the buttons needs its own column, so the username and examboard entries are spread over three columns, using columnspan = 3.
		self.usernameEntry.grid(row = 1, column = 1, columnspan = 3, sticky=tk.W+tk.E)
		self.defaultExamBoardEntry.grid(row = 2, column = 1, columnspan = 3, sticky=tk.W+tk.E)
		# The three buttons are all on the same row.
		self.timerButton1.grid(row = 3, column = 1, sticky=tk.W+tk.E)
		self.timerButton2.grid(row = 3, column = 2, sticky=tk.W+tk.E)
		self.timerButton3.grid(row = 3, column = 3, sticky=tk.W+tk.E)
		
		# This button finalises the user and will save the users details to the database, and select the user, brining the actual user straight to the quiz browser.
		self.completeButton = tk.Button(self.window, text = "Create User", command = self.finish)
		self.completeButton.grid(row = 4, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
	
	def finish(self):
		# This is called when the user clicks the "Create User" button in the bottom right of the dialog.
		# This adds the user to the database, selects the user as the current user, and changes the main window to the quiz browser.
		
		# If the user is on the login screen, turn it to the quiz browser screen.
		import mainmenu
		if(self.parent.state == mainmenu.MainWindowStates.login):
			self.parent.unloadLoginScreen()
			self.parent.loadQuizBrowserScreen()
		# This destroys the window after all the previous tasks are finished.
		self.window.destroy()

class UserSettingsDialog(object):
	def __init__(self, toplevel, parent):
		# toplevel is the tkinter object of the parent window.
		# parent in the MainApp object, unless another dialog opens this window.
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
		self.headerFont = tkfont.Font(family="Helvetica", size=28)
		# The header itself.
		self.headerLabel = tk.Label(self.window, text = "User Settings", font=self.headerFont)
		self.headerLabel.grid(row = 0, column = 0, columnspan=2)
		
		# The Labels/Text widgets to the left of the entry boxes/buttons with the name of the input expected on the right.
		self.usernameLabel = tk.Label(self.window, text = "<Username here>")
		self.defaultExamBoardLabel = tk.Label(self.window, text = "Default exam board:")
		self.timerSettingsLabel = tk.Label(self.window, text = "Timer settings:  NO TIMER")
		# These go on the first column (column 0)
		self.usernameLabel.grid(row = 1, column = 0)
		self.defaultExamBoardLabel.grid(row = 2, column = 0)
		self.timerSettingsLabel.grid(row = 3, column = 0)
		
		# The actual entry fields for the user settings.
		# Examboard entry is a combobox. It gets the options from the examboards tabel in the database.
		self.defaultExamBoardEntry = ttk.Combobox(self.window, values=["No preference"])
		# The three timer button options represent three different timer settings. These are the only three, so I used buttons rather than drop down.
		self.timerButton1 = tk.Button(self.window, text = "No timer (easy)")
		self.timerButton2 = tk.Button(self.window, text = "Long timer (medium)")
		self.timerButton3 = tk.Button(self.window, text = "Short timer (hard)")
		# Each of the buttons needs its own column, so the examboard entry is spread over three columns, using columnspan = 3.
		self.defaultExamBoardEntry.grid(row = 2, column = 1, columnspan = 3, sticky=tk.W+tk.E)
		# The three buttons are all on the same row.
		self.timerButton1.grid(row = 3, column = 1, sticky=tk.W+tk.E)
		self.timerButton2.grid(row = 3, column = 2, sticky=tk.W+tk.E)
		self.timerButton3.grid(row = 3, column = 3, sticky=tk.W+tk.E)
		
		# This button will run the self.finish() method, and will save the user settings in the database.
		self.completeButton = tk.Button(self.window, text = "Update user settings", command = self.finish)
		self.completeButton.grid(row = 4, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
	
	def finish(self):
		# This is called when the user clicks the "Update user settings" button in the bottom right of the dialog.
		# This will update the user's settings that are currently in RAM and update the user record on the database.
		# This destroys the window after all the previous tasks are finished.
		self.window.destroy()
