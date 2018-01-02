# This file will handle the GUI for users answering the questions on a quiz.

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

class ActiveQuizDialog(object):
    def __init__(self, toplevel: tk.Tk, parent, quiz: 'Quiz', currentUser: 'User') -> None:
        """
        toplevel is the tkinter object of the parent window.
        parent is the MainApp object, unless another dialog opens this window.
        quiz is the Quiz object that will contain all the Quiz's data.
        currentUser is the User object of the currently selected user, used for recording results at the end.
        """
        import threading
        
        self.parent = parent
        self.toplevel = toplevel
        # The quiz the window is dealing with.
        self.quiz = quiz
        # The user that has launched the quiz.
        self.user = currentUser
        # This creates the window. padx and pady here add 5 pixels padding horizontally and vertically respectively
        # This is to stop the widgets on the window from touching the edges of the window, which doesn't look that good.
        self.window = tk.Toplevel(toplevel, padx = 5, pady = 5)
        # Dimensions of the window: 500 pixels wide by 300 pixels high.
        self.window.geometry("800x500")
        # The minimum dimensions of the window, as this window is resizable.
        self.window.minsize(width = 500, height = 400)
        # Setting the title of the window.
        self.window.title(quiz.name + " - Quiz - Quizzable")
        # This makes the self.finish method run when the window is closed.
        self.window.protocol("WM_DELETE_WINDOW", self.finish)
        
        # Configuring the grid configuration of the window, in which the elements/widgets on the window will fit into.
        # There are 2 columns and 7 rows.
        self.window.grid_columnconfigure(0, weight = 3)
        self.window.grid_columnconfigure(1, weight = 1)
        self.window.grid_rowconfigure(0, weight = 0)
        self.window.grid_rowconfigure(1, weight = 1)
        self.window.grid_rowconfigure(2, weight = 2)
        self.window.grid_rowconfigure(3, weight = 1)
        self.window.grid_rowconfigure(4, weight = 1)
        self.window.grid_rowconfigure(5, weight = 1)
        self.window.grid_rowconfigure(6, weight = 1)
        
        # The fonts for the quiz title and question.
        self.quizNameFont = tkfont.Font(family = "Helvetica", size = 20)
        self.questionFont = tkfont.Font(family = "Helvetica", size = 16)
        
        # The text labels in the top 3 rows.
        self.quizNameLabel                = tk.Label(self.window, text = quiz.name, anchor = tk.NW, font = self.quizNameFont)
        self.quizSubjectAndExamBoardLabel = tk.Label(self.window, text = parent.subjectDictionary[quiz.subject] + " - " + parent.examboardDictionary[quiz.examBoard], anchor = tk.NW)
        # Lots of arguments on the next line of code. anchor = tk.W means that all new lines are left-aligned.
        # justify = tk.LEFT means that the whole chunk of text should be left-aligned. Both anchor and justify are needed because they have small differences.
        # wraplength is the amount of pixels the text can fill horizontally before needing to go onto a new line.
        # TODO: Dynamic wraplength (in pixels), which should always be 75% of the window width.
        #       Add an event listener on toplevel for window size changes.
        self.questionLabel  = tk.Label(self.window, anchor = tk.W, font = self.questionFont, justify = tk.LEFT, wraplength = 550,
                text = "<Question goes here> \n<If the question is a long question, then this text box spans over multiple lines>")
        self.usernameLabel  = tk.Label(self.window, text = self.user.username)
        self.timeLimitLabel = tk.Label(self.window, text = "<Time limit>")
        # Positioning the text labels on the top 3 rows.
        self.quizNameLabel.grid(row = 0, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.quizSubjectAndExamBoardLabel.grid(row = 1, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.questionLabel.grid(row = 2, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.usernameLabel.grid(row = 0, column = 1, rowspan = 2)
        self.timeLimitLabel.grid(row = 2, column = 1)
        # The answer buttons
        self.answerButton1 = tk.Button(self.window, text = "<Option 1>", command = lambda: self.answerButtonClick(0))
        self.answerButton2 = tk.Button(self.window, text = "<Option 2>", command = lambda: self.answerButtonClick(1))
        self.answerButton3 = tk.Button(self.window, text = "<Option 3>", command = lambda: self.answerButtonClick(2))
        self.answerButton4 = tk.Button(self.window, text = "<Option 4>", command = lambda: self.answerButtonClick(3))
        # Positioning the answer buttons.
        self.answerButton1.grid(row = 3, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.answerButton2.grid(row = 4, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.answerButton3.grid(row = 5, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.answerButton4.grid(row = 6, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        # The option buttons
        self.hintButton = tk.Button(self.window, text = "Hint")
        self.helpButton = tk.Button(self.window, text = "Help!")
        self.pauseButton = tk.Button(self.window, text = "Pause")
        self.endQuizButton = tk.Button(self.window, text = "End Quiz", command = self.finish)
        # Positioning the option buttons
        self.hintButton.grid(row = 3, column = 1, sticky = tk.W+tk.E+tk.N+tk.S)
        self.helpButton.grid(row = 4, column = 1, sticky = tk.W+tk.E+tk.N+tk.S)
        self.pauseButton.grid(row = 5, column = 1, sticky = tk.W+tk.E+tk.N+tk.S)
        self.endQuizButton.grid(row = 6, column = 1, sticky = tk.W+tk.E+tk.N+tk.S)
        
        # Starting the quiz thread
        t = threading.Thread(target = self.quizThread)
        self.running = True
        t.start()
    
    def answerButtonClick(self, answer: int) -> None:
        """This method is a simple method to be run in a lambda statement whenever an answer button is clicked."""
        self.theirAnswer = answer
    
    def quizThread(self):
        """This subroutine is run in a separate thread, and it will manage the quiz window while the user is doing the quiz."""
        import time
        import math
        questionNumber = 0
        currentQuestion = -1
        currentQuestionStartTime = 0
        self.theirAnswer = -1
        correctAnswer = -1
        while self.running:
            if(currentQuestion != questionNumber):
                self.questionLabel.config(text = self.quiz.questions[questionNumber].question)
                currentQuestionStartTime = time.clock()
                currentQuestion = questionNumber
                answers, correctAnswer = self.quiz.questions[questionNumber].getShuffledAnswers()
                self.answerButton1.config(text = answers[0])
                self.answerButton2.config(text = answers[1])
                self.answerButton3.config(text = answers[2]) # TODO: Disable buttons if there are less than 4 answers.
                self.answerButton4.config(text = answers[3])
                self.theirAnswer = -1
            if(self.theirAnswer == -1):
                timeRemaining = currentQuestionStartTime + 5 + self.quiz.difficulty * 5 - time.clock()
                if(timeRemaining <= 0):
                    self.timeLimitLabel.config(text = "Out of time!")
                else:
                    self.timeLimitLabel.config(text = str(math.ceil(timeRemaining)))
            else:
                if(correctAnswer == self.theirAnswer):
                    self.timeLimitLabel.config(text = "Correct!") # TODO: Change text colour.
                else:
                    self.timeLimitLabel.config(text = "Wrong!") # TODO: Change text colour.
            
        # Closes the window after it has stopped running
        self.window.destroy()
    
    def finish(self) -> None:
        # This destroys the window after all the previous tasks are finished, by setting running to false, so the window closes once the thread has finished its last iteration.
        self.running = False
