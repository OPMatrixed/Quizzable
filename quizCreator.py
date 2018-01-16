"""This file will handle the GUI for creating and editing quizzes."""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

class QuizCreatorDialog(object):
    def __init__(self, toplevel: tk.Tk, parent):
        """
        This is the quiz creator window, and this constructor method is run when creating the QuizCreatorDialog object.
        
        toplevel is the tkinter object of the parent window.
        parent in the MainApp object, unless another dialog opens this window.
        """
        self.parent = parent
        self.toplevel = toplevel
        # This creates the window. padx and pady here add 5 pixels padding horizontally and vertically respectively
        # This is to stop the widgets on the window from touching the edges of the window, which doesn't look that good.
        self.window = tk.Toplevel(toplevel, padx = 5, pady = 5)
        # Dimensions of the window: 500 pixels wide by 300 pixels high.
        self.window.geometry("900x600")
        # The minimum dimensions of the window, as this window is re-sizable.
        self.window.minsize(width = 600, height = 500)
        # Setting the title of the window.
        self.window.title("Create Quiz - Quizzable")
        # This makes the self.exit method run when the window is closed without clicking the "Finish Quiz" button.
        self.window.protocol("WM_DELETE_WINDOW", self.exit)
        self.loadScreenElements()
        self.setupQuestionsFrame()
    
    def loadScreenElements(self):
        """This loads all the widgets onto the screen."""
        
        # Configure the grid
        #self.window.grid_columnconfigure(0, weight = 1)
        self.window.grid_columnconfigure(1, weight = 1)
        #self.window.grid_columnconfigure(2, weight = 1)
        self.window.grid_columnconfigure(3, weight = 1)
        #self.window.grid_columnconfigure(4, weight = 1)
        self.window.grid_rowconfigure(3, pad = 12)
        self.window.grid_rowconfigure(4, weight = 1)
        
        self.nameLabel = tk.Label(self.window, text = "Name:")
        self.examBoardLabel = tk.Label(self.window, text = "Exam board:")
        self.subjectLabel = tk.Label(self.window, text = "Subject:")
        self.difficultyLabel = tk.Label(self.window, text = "Difficulty:")
        self.tagsLabel = tk.Label(self.window, text = "Tags (separate using commas):")
        self.nameEntry = tk.Entry(self.window)
        self.examBoardCombobox = ttk.Combobox(self.window, state = "readonly", values = list(self.parent.examboardDictionary.values()))
        self.subjectCombobox = ttk.Combobox(self.window, state = "readonly", values = list(self.parent.subjectDictionary.values()))
        self.difficultyCombobox = ttk.Combobox(self.window, state = "readonly", values = [1, 2, 3, 4, 5])
        self.tagsEntry = tk.Entry(self.window)
        self.finishButton = tk.Button(self.window, text = "Finish Quiz")
        self.addQuestionButton = tk.Button(self.window, text = "Add another question")
        self.horizontalSeparator = ttk.Separator(self.window, orient = "horizontal")
        
        self.nameLabel.grid(row = 0, column = 0)
        self.examBoardLabel.grid(row = 0, column = 2)
        self.subjectLabel.grid(row = 1, column = 0)
        self.difficultyLabel.grid(row = 1, column = 2)
        self.tagsLabel.grid(row = 2, column = 0, columnspan = 2)
        self.nameEntry.grid(row = 0, column = 1, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W+tk.E)
        self.examBoardCombobox.grid(row = 0, column = 3, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W+tk.E)
        self.subjectCombobox.grid(row = 1, column = 1, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W+tk.E)
        self.difficultyCombobox.grid(row = 1, column = 3, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W+tk.E)
        self.tagsEntry.grid(row = 2, column = 2, columnspan = 2, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W+tk.E)
        self.finishButton.grid(row = 0, column = 4)
        self.addQuestionButton.grid(row = 2, column = 4)
        self.horizontalSeparator.grid(row = 3, column = 0, columnspan = 5, sticky = tk.W+tk.E)
    
    def setupQuestionsFrame(self):
        self.frameScrollbar = tk.Scrollbar(self.window)
        self.questionsCanvas = tk.Canvas(self.window, yscrollcommand = self.frameScrollbar.set, bd = 0, highlightthickness = 0)
        self.frameScrollbar.config(command = self.questionsCanvas.yview)
        
        self.questionsCanvas.grid(row = 4, column = 0, columnspan = 5, sticky = tk.W+tk.E+tk.N+tk.S, pady = 10)
        self.frameScrollbar.grid(row = 4, column = 5, sticky = tk.N+tk.S)
        
        self.questionsFrame = tk.Frame(self.window)
        self.questionFrameID = self.questionsCanvas.create_window((0, 0), window = self.questionsFrame, anchor = tk.N+tk.W)
        
        self.questionsFrame.bind("<Configure>", lambda e: self.questionsCanvas.config(scrollregion = "0 0 " + str(self.questionsFrame.winfo_reqwidth()) + " " + str(self.questionsFrame.winfo_reqheight())))
        self.questionsCanvas.bind("<Configure>", lambda e: self.questionsCanvas.itemconfigure(self.questionFrameID, width = self.questionsCanvas.winfo_width()))
        
        for i in range(7):
            self.questionsFrame.grid_columnconfigure(i, weight = 1, minsize = 40)
        
        self.addNewQuestionButton = tk.Button(self.questionsFrame, text = "Add new question", command = self.addNewQuestion)
        self.addNewQuestionButton.grid(row = 1000, column = 0, columnspan = 8)
        
        self.questions = {}
        self.questionIndex = 1
        
        self.frameQuestionLabel = tk.Label(self.questionsFrame, text = "Question")
        self.frameCorrectAnswerLabel = tk.Label(self.questionsFrame, text = "Correct Answer")
        self.frameAnswer2Label = tk.Label(self.questionsFrame, text = "Answer 2")
        self.frameAnswer3Label = tk.Label(self.questionsFrame, text = "Answer 3")
        self.frameAnswer4Label = tk.Label(self.questionsFrame, text = "Answer 4")
        self.frameHintLabel = tk.Label(self.questionsFrame, text = "Hint")
        self.frameHelpLabel = tk.Label(self.questionsFrame, text = "Help")
        self.frameQuestionLabel.grid(row = 0, column = 0)
        self.frameCorrectAnswerLabel.grid(row = 0, column = 1)
        self.frameAnswer2Label.grid(row = 0, column = 2)
        self.frameAnswer3Label.grid(row = 0, column = 3)
        self.frameAnswer4Label.grid(row = 0, column = 4)
        self.frameHintLabel.grid(row = 0, column = 5)
        self.frameHelpLabel.grid(row = 0, column = 6)
    
    def addNewQuestion(self):
        myindex = self.questionIndex
        self.questionIndex += 1
        question = tk.Entry(self.questionsFrame)
        correctAnswer = tk.Entry(self.questionsFrame)
        answer2 = tk.Entry(self.questionsFrame)
        answer3 = tk.Entry(self.questionsFrame)
        answer4 = tk.Entry(self.questionsFrame)
        hint = tk.Entry(self.questionsFrame)
        help = tk.Entry(self.questionsFrame)
        deleteButton = tk.Button(self.questionsFrame, text = "X", command = lambda: self.removeQuestion(myindex))
        
        question.grid(row = self.questionIndex, column = 0)
        correctAnswer.grid(row = self.questionIndex, column = 1)
        answer2.grid(row = self.questionIndex, column = 2)
        answer3.grid(row = self.questionIndex, column = 3)
        answer4.grid(row = self.questionIndex, column = 4)
        hint.grid(row = self.questionIndex, column = 5)
        help.grid(row = self.questionIndex, column = 6)
        deleteButton.grid(row = self.questionIndex, column = 7)
        
        self.questions[myindex] = [question, correctAnswer, answer2, answer3, answer4, hint, help, deleteButton]
    
    def removeQuestion(self, index):
        for i in range(8):
            self.questions[index][i].destroy()
        del self.questions[index]
    
    def exit(self):
        """This function is run when the window is being closed without saving."""
        # TODO: Ask user if they want to save the quiz.
        self.window.destroy()
