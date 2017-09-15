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
		self.loadQuizBrowserScreen()
	
	def loadLoginScreen(self):
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
		self.loginSelectUserButton = tk.Button(self.tk, text="Select User", bg="#EAEAEA", border=3, relief=tk.GROOVE)
		self.loginSelectUserButton.grid(row = 5, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
	
	def unloadLoginScreen(self):
		self.loginLabel.destroy()
		self.loginComboUser.destroy()
		self.loginCreateUserButton.destroy()
		self.loginSelectUserButton.destroy()
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
	
	def loadQuizBrowserScreen(self):
		self.tk.grid_rowconfigure(0, weight = 0, minsize=40)
		self.tk.grid_rowconfigure(1, weight = 0, minsize=40)
		self.tk.grid_rowconfigure(2, weight = 1)
		self.tk.grid_columnconfigure(0, weight = 1)
		self.tk.grid_columnconfigure(1, weight = 1)
		self.tk.grid_columnconfigure(2, weight = 1)
		self.tk.grid_columnconfigure(3, weight = 1)
		# TODO: Put these in a frame
		self.quizBrowserSearchLabel = tk.Label(self.tk, text="Search:")
		self.quizBrowserSearchLabel.grid(row = 0, column = 0, sticky = tk.E)
		self.quizBrowserSearchEntry = tk.Entry(self.tk, width = 30)
		self.quizBrowserSearchEntry.grid(row = 0, column = 1)
		#
		self.createQuizButton = tk.Button(self.tk, text="Create a Quiz")
		self.importQuizButton = tk.Button(self.tk, text="Import a Quiz")
		self.createQuizButton.grid(row = 0, column = 2)
		self.importQuizButton.grid(row = 0, column = 3)
		self.filterByExamBoardCombo = ttk.Combobox(self.tk, state="readonly", values=["No filter"])
		self.filterByExamBoardCombo.set("Filter by exam board")
		self.filterBySubjectCombo = ttk.Combobox(self.tk, state="readonly", values=["No filter"])
		self.filterBySubjectCombo.set("Filter by subject")
		self.filterByDifficultyCombo = ttk.Combobox(self.tk, state="readonly", values=["No filter","1","2","3","4","5","2 and above","3 and above","4 and above","2 and below","3 and below","4 and below"])
		self.filterByDifficultyCombo .set("Filter by difficulty")
		self.filterByExamBoardCombo.grid(row = 1, column = 0, sticky=tk.W+tk.E+tk.N+tk.S)
		self.filterBySubjectCombo.grid(row = 1, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
		self.filterByDifficultyCombo.grid(row = 1, column = 2, sticky=tk.W+tk.E+tk.N+tk.S)
		# Start of frame
		self.quizListFrame = tk.Frame(self.tk)
		
		self.quizListFrame.grid_columnconfigure(0, weight = 1)
		self.quizListFrame.grid_columnconfigure(1, weight = 1)
		self.quizListFrame.grid_columnconfigure(2, weight = 1)
		self.quizListFrame.grid_columnconfigure(3, weight = 1)
		self.quizListFrame.grid_rowconfigure(1, weight = 1)
		
		self.quizListLabelNames = tk.Label(self.quizListFrame, text="Quiz Name")
		self.quizListLabelSubject = tk.Label(self.quizListFrame, text="Subject")
		self.quizListLabelExamBoard = tk.Label(self.quizListFrame, text="Examboard")
		self.quizListLabelBestAttempt = tk.Label(self.quizListFrame, text="Last Attempt")
		self.quizListLabelNames.grid(row = 0, column = 0)
		self.quizListLabelSubject.grid(row = 0, column = 1)
		self.quizListLabelExamBoard.grid(row = 0, column = 2)
		self.quizListLabelBestAttempt.grid(row = 0, column = 3)
		
		self.quizListBoxScrollBar = tk.Scrollbar(self.quizListFrame, command = self.scrollbarCommand)
		self.quizListBoxScrollBar.grid(row = 1, column = 4, sticky=tk.N+tk.S)
		
		self.quizListBoxNames = tk.Listbox(self.quizListFrame, yscrollcommand=self.scrollOnList)
		self.quizListBoxSubject = tk.Listbox(self.quizListFrame, yscrollcommand=self.scrollOnList)
		self.quizListBoxExamBoard = tk.Listbox(self.quizListFrame, yscrollcommand=self.scrollOnList)
		self.quizListBoxBestAttempt = tk.Listbox(self.quizListFrame, yscrollcommand=self.scrollOnList)
		self.quizListBoxNames.grid(row = 1, column = 0, sticky=tk.W+tk.E+tk.N+tk.S)
		self.quizListBoxSubject.grid(row = 1, column = 1, sticky=tk.W+tk.E+tk.N+tk.S)
		self.quizListBoxExamBoard.grid(row = 1, column = 2, sticky=tk.W+tk.E+tk.N+tk.S)
		self.quizListBoxBestAttempt.grid(row = 1, column = 3, sticky=tk.W+tk.E+tk.N+tk.S)
		
		for i in range(200):
			self.quizListBoxNames.insert(tk.END, "N"+str(i))
			self.quizListBoxSubject.insert(tk.END, "S"+str(i))
			self.quizListBoxExamBoard.insert(tk.END, "E"+str(i))
			self.quizListBoxBestAttempt.insert(tk.END, "B"+str(i))
		
		self.quizListFrame.grid(row = 2, column = 0, columnspan = 3, sticky=tk.W+tk.E+tk.N+tk.S)
		# End of frame
	
	def scrollbarCommand(self, *args):
		self.quizListBoxNames.yview(*args)
		self.quizListBoxSubject.yview(*args)
		self.quizListBoxExamBoard.yview(*args)
		self.quizListBoxBestAttempt.yview(*args)
	def scrollOnList(self, *args):
		self.quizListBoxScrollBar.set(args[0],args[1])
		self.quizListBoxNames.yview("moveto", args[0])
		self.quizListBoxSubject.yview("moveto", args[0])
		self.quizListBoxExamBoard.yview("moveto", args[0])
		self.quizListBoxBestAttempt.yview("moveto", args[0])

def startGUI():
	print("Building GUI...")
	master = tk.Tk()
	master.protocol("WM_DELETE_WINDOW", master.destroy)
	MainApp(master)
	print("Finished building GUI.")
	master.mainloop()

if(__name__=="__main__"):
	startGUI()
