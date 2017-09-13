# This file contains the code to design the main login screen, and also the main quiz list viewer.

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

class MainWindowStates:
	closing = 0
	login = 1
	questionlist = 2

class MainApp(object):
	def __init__(self, tkobj):
		self.tk = tkobj
		self.tk.geometry("800x600")
		self.tk.title("Home - Quizzable - Alpha v0.1")
		self.mode = MainWindowStates.login
		self.selectedUser = None
		self.loadLogin()
	def loadLogin(self):
		headerFont = tkfont.Font(family="Helvetica", size=28)
		
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
		self.loginLabel = tk.Label(self.tk, text="User Selection", font=headerFont)
		self.loginLabel.grid(row = 1, column = 1)
		self.loginComboUser = ttk.Combobox(self.tk, state="readonly", values=["No users created, click \"Create User\""])
		self.loginComboUser.grid(row = 3, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
		self.loginCreateUserButton = tk.Button(self.tk, text="Create User", bg="#DFDFDF", border=3, relief=tk.GROOVE)
		self.loginCreateUserButton.grid(row = 6, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
		self.loginCreateUserButton = tk.Button(self.tk, text="Select User", bg="#EAEAEA", border=3, relief=tk.GROOVE)
		self.loginCreateUserButton.grid(row = 5, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
	def loadQuestionView(self):
		pass

def startGUI():
	print("Building GUI...")
	master = tk.Tk()
	master.protocol("WM_DELETE_WINDOW", master.destroy)
	MainApp(master)
	print("Finished building GUI.")
	master.mainloop()

if(__name__=="__main__"):
	startGUI()
