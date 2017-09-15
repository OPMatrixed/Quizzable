# This file will handle two screens specified on the design document:
# the user creation screen, and the user settings screen.

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

class UserDialog(object):
	def __init__(self, toplevel, parent):
		self.parent = parent
		self.toplevel = toplevel
		self.window = tk.Toplevel(toplevel, padx = 5, pady = 5)
		self.window.geometry("500x300")
		self.window.minsize(width = 500, height = 300)
		self.window.title("Create User - Quizzable")
		
		self.window.grid_columnconfigure(0, weight = 1)
		self.window.grid_columnconfigure(1, weight = 1)
		self.window.grid_columnconfigure(2, weight = 1)
		self.window.grid_columnconfigure(3, weight = 1)
		self.window.grid_rowconfigure(0, weight = 1)
		self.window.grid_rowconfigure(1, weight = 1)
		self.window.grid_rowconfigure(2, weight = 1)
		self.window.grid_rowconfigure(3, weight = 1)
		self.window.grid_rowconfigure(4, weight = 1)
		
		self.headerFont = tkfont.Font(family="Helvetica", size=28)
		self.headerLabel = tk.Label(self.window, text = "Create User", font=self.headerFont)
		self.headerLabel.grid(row = 0, column = 0, columnspan=2)
		
		self.usernameLabel = tk.Label(self.window, text = "Username:")
		self.defaultExamBoardLabel = tk.Label(self.window, text = "Default exam board:")
		self.timerSettingsLabel = tk.Label(self.window, text = "Timer settings:  NO TIMER")
		self.usernameLabel.grid(row = 1, column = 0)
		self.defaultExamBoardLabel.grid(row = 2, column = 0)
		self.timerSettingsLabel.grid(row = 3, column = 0)
		
		self.usernameEntry = tk.Entry(self.window, width = 20)
		self.defaultExamBoardEntry = ttk.Combobox(self.window, values=["No preference"])
		self.timerButton1 = tk.Button(self.window, text = "No timer (easy)")
		self.timerButton2 = tk.Button(self.window, text = "Long timer (medium)")
		self.timerButton3 = tk.Button(self.window, text = "Short timer (hard)")
		self.usernameEntry.grid(row = 1, column = 1, columnspan = 3, sticky=tk.W+tk.E)
		self.defaultExamBoardEntry.grid(row = 2, column = 1, columnspan = 3, sticky=tk.W+tk.E)
		self.timerButton1.grid(row = 3, column = 1, sticky=tk.W+tk.E)
		self.timerButton2.grid(row = 3, column = 2, sticky=tk.W+tk.E)
		self.timerButton3.grid(row = 3, column = 3, sticky=tk.W+tk.E)
		
		self.completeButton = tk.Button(self.window, text = "Create User", command = self.finish)
		self.completeButton.grid(row = 4, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
	
	def finish(self):
		self.parent.unloadLoginScreen()
		self.parent.loadQuizBrowserScreen()
		self.window.destroy()
