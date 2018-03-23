"""This file will handle the GUI for users answering the questions on a quiz."""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import tkinter.messagebox as tkmb

import math as maths
import threading

class ActiveQuizDialog(object):
    def __init__(self, toplevel: tk.Tk, parent, quiz: 'Quiz', currentUser: 'User') -> None:
        """
        toplevel is the tkinter object of the parent window.
        parent is the MainApp object, unless another dialog opens this window.
        quiz is the Quiz object that will contain all the Quiz's data.
        currentUser is the User object of the currently selected user, used for recording results at the end.
        """
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
        # The minimum dimensions of the window, as this window is re-sizable.
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
        
        # The fonts for the quiz title, question and buttons.
        self.quizNameFont = tkfont.Font(family = "Helvetica", size = 20)
        self.questionFont = tkfont.Font(family = "Helvetica", size = 16)
        self.buttonFont = tkfont.Font(family = "Helvetica", size = 12)
        
        # The text labels in the top 3 rows.
        self.quizNameLabel = tk.Label(self.window, text = quiz.name, anchor = tk.NW, font = self.quizNameFont)
        subjectExamBoard = []
        if(quiz.subject in parent.subjectDictionary.keys()):
            subjectExamBoard.append(parent.subjectDictionary[quiz.subject])
        if(quiz.examBoard in parent.examboardDictionary.keys()):
            subjectExamBoard.append(parent.examboardDictionary[quiz.examBoard])
        self.quizSubjectAndExamBoardLabel = tk.Label(self.window, text =  " - ".join(subjectExamBoard), anchor = tk.NW)
        # Lots of arguments on the next line of code. anchor = tk.W means that all new lines are left-aligned.
        # justify = tk.LEFT means that the whole chunk of text should be left-aligned. Both anchor and justify are needed because they have small differences.
        # wraplength is the amount of pixels the text can fill horizontally before needing to go onto a new line.
        # TODO: Dynamic wraplength (in pixels), which should always be 75% of the window width.
        #       Add an event listener on toplevel for window size changes.
        self.questionLabel  = tk.Label(self.window, anchor = tk.W, font = self.questionFont, justify = tk.LEFT, wraplength = 550,
                text = "<Question goes here> \n<If the question is a long question, then this text box spans over multiple lines>")
        self.usernameLabel  = tk.Label(self.window, text = self.user.username, font = self.questionFont)
        self.timeLimitLabel = tk.Label(self.window, text = "", font = self.questionFont)
        # Positioning the text labels on the top 3 rows.
        self.quizNameLabel.grid(row = 0, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.quizSubjectAndExamBoardLabel.grid(row = 1, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.questionLabel.grid(row = 2, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.usernameLabel.grid(row = 0, column = 1, rowspan = 2)
        self.timeLimitLabel.grid(row = 2, column = 1)
        # The answer buttons
        self.answerButtons = [None, None, None, None]
        self.answerButtons[0] = tk.Button(self.window, text = "<Option 1>", font = self.buttonFont, command = lambda: self.answerButtonClick(0))
        self.answerButtons[1] = tk.Button(self.window, text = "<Option 2>", font = self.buttonFont, command = lambda: self.answerButtonClick(1))
        self.answerButtons[2] = tk.Button(self.window, text = "<Option 3>", font = self.buttonFont, command = lambda: self.answerButtonClick(2))
        self.answerButtons[3] = tk.Button(self.window, text = "<Option 4>", font = self.buttonFont, command = lambda: self.answerButtonClick(3))
        # Positioning the answer buttons.
        self.answerButtons[0].grid(row = 3, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.answerButtons[1].grid(row = 4, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.answerButtons[2].grid(row = 5, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.answerButtons[3].grid(row = 6, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        # The option buttons
        self.hintButton = tk.Button(self.window, text = "Hint", command = self.showHint)
        self.helpButton = tk.Button(self.window, text = "Help!", command = self.showHelp)
        self.pauseButton = tk.Button(self.window, text = "Pause", command = self.pause)
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
        if(self.currentState == 0):
            self.theirAnswer = answer
            self.currentState = 1
    
    def showHint(self):
        if(self.quiz.questions[self.questionNumber].hint):
            tkmb.showinfo("Hint", self.quiz.questions[self.questionNumber].hint, parent = self.window)
    
    def showHelp(self):
        if(self.quiz.questions[self.questionNumber].help):
            self.theirAnswer = 4
            self.currentState = 1
            tkmb.showinfo("Help", self.quiz.questions[self.questionNumber].help, parent = self.window)
    
    def pause(self):
        self.paused = not self.paused
    
    def quizThread(self):
        """This subroutine is run in a separate thread, and it will manage the quiz window while the user is doing the quiz."""
        import time # Used to keep track of times
        self.questionNumber = 0 # The question number of the quiz that should be displayed on the next iteration.
        currentQuestion = -1 # The current question number that is currently being displayed.
        currentQuestionStartTime = 0 # The time that the current question was initially displayed, stored as the time since the thread started, in seconds.
        answerTime = 0 # The time that the quiz window will move on from the current question after the user has answered, stored as the time since the thread started, in seconds.
        self.currentState = -1 # The current state of the quiz. States: -1 - Quiz hasn't started, 0 - Time to answer question, 1 - Question answered, 2 - Quiz finished.
        self.theirAnswer = -1 # The answer that the user gives, which is set every time a user clicks on an answer button.
        correctAnswer = -1 # The correct answer to the current question.
        self.numberOfCorrectAnswers = 0 # The number of answers that have been answered correctly.
        self.totalPausedDuration = 0 # The length of time that the quiz has been paused for, in seconds.
        self.timesTakenToAnswer = [None for i in range(len(self.quiz.questions))] # The time it took to answer each question, in seconds.
        self.totalDuration = None # The total duration of the quiz, in seconds.
        self.startTime = time.clock() # The time that the quiz started, in seconds.
        wasPaused = False
        self.paused = False
        while self.running:
            if(self.paused == True and wasPaused == True):
                # The quiz is still paused.
                time.sleep(0.1)
                self.totalPausedDuration += 0.1
                currentQuestionStartTime += 0.1
                continue
            if(self.paused == True and wasPaused == False):
                # Quiz has just been paused.
                self.questionLabel.config(text = "PAUSED")
                self.hintButton.config(state = tk.DISABLED)
                self.helpButton.config(state = tk.DISABLED)
                for i in range(4):
                    # This disables all the buttons.
                    self.answerButtons[i].config(state = tk.DISABLED, text = "PAUSED")
                wasPaused = True
                continue
            if(self.paused == False and wasPaused == True):
                # Quiz has just been unpaused.
                if(self.state == 0):
                    self.questionLabel.config(text = self.quiz.questions[self.questionNumber].question)
                    answers, correctAnswer = self.quiz.questions[self.questionNumber].getShuffledAnswers()
                    for i in range(len(answers)):
                        # This recolours and re-enables buttons, as after each question the font colour of each button changes, and some buttons may be disabled.
                        self.answerButtons[i].config(text = answers[i], fg = "black", bg = "SystemButtonFace")
                        self.answerButtons[i].config(state = tk.NORMAL)
                    for i in range(4, len(answers), -1):
                        # This disables buttons if there is less than four answers for a given question.
                        self.answerButtons[i].config(state = tk.DISABLED, text = "")
                    self.hintButton.config(state = tk.NORMAL if self.quiz.questions[self.questionNumber].hint else tk.DISABLED)
                    self.helpButton.config(state = tk.NORMAL if self.quiz.questions[self.questionNumber].help else tk.DISABLED)
                else:
                    self.questionLabel.config(text = "Next question coming in a moment...")
                wasPaused = False
            if(currentQuestion != self.questionNumber):
                # A new question needs to be displayed
                if(len(self.quiz.questions) == self.questionNumber):
                    # This code is run when the user has finished the quiz.
                    self.currentState = 2
                    self.running = False
                    continue
                # The next question's text is displayed
                self.questionLabel.config(text = self.quiz.questions[self.questionNumber].question)
                currentQuestionStartTime = time.clock()
                currentQuestion = self.questionNumber
                # Gets the shuffled answers to the current question.
                answers, correctAnswer = self.quiz.questions[self.questionNumber].getShuffledAnswers()
                for i in range(len(answers)):
                    # This recolours and re-enables buttons, as after each question the font colour of each button changes, and some buttons may be disabled.
                    self.answerButtons[i].config(text = answers[i], fg = "black", bg = "SystemButtonFace")
                    self.answerButtons[i].config(state = tk.NORMAL)
                for i in range(4, len(answers), -1):
                    # This disables buttons if there is less than four answers for a given question.
                    self.answerButtons[i].config(state = tk.DISABLED, text = "")
                self.hintButton.config(state = tk.NORMAL if self.quiz.questions[self.questionNumber].hint else tk.DISABLED)
                self.helpButton.config(state = tk.NORMAL if self.quiz.questions[self.questionNumber].help else tk.DISABLED)
                self.timeLimitLabel.config(text = "")
                # Resetting their answer and the state variables.
                self.theirAnswer = -1
                self.currentState = 0
            if(self.currentState == 1 and self.theirAnswer != -1):
                # The following code runs immediately after they click an answer.
                # Record the time taken to answer the question
                self.timesTakenToAnswer[currentQuestion] = time.clock() - currentQuestionStartTime
                if(correctAnswer == self.theirAnswer):
                    # If the answer they entered is correct:
                    # Show the next question after 1 second of delay
                    answerTime = time.clock() + 1
                    # Display 'Correct', in green, where the countdown timer was.
                    self.timeLimitLabel.config(text = "Correct!", fg = "green")
                    self.numberOfCorrectAnswers += 1
                else:
                    # If the answered they entered is wrong:
                    # Show the next question after 5 seconds of delay.
                    answerTime = time.clock() + 5
                    # Display 'Wrong', in red, where the countdown timer was.
                    self.timeLimitLabel.config(text = "Wrong!", fg = "red")
                for i in range(len(self.answerButtons)):
                    # For each of the answer buttons:
                    if(i == correctAnswer):
                        # Make the text green if it was the correct button
                        self.answerButtons[i].config(fg = "green")
                    else:
                        # Make the text red if it was the wrong button
                        self.answerButtons[i].config(fg = "red")
                    if(i == self.theirAnswer):
                        # If it was the button that they clicked, make the background of that button white.
                        self.answerButtons[i].config(bg = "white")
                self.theirAnswer = -1
            if(self.theirAnswer == -1):
                if(self.currentState == 0):
                    # If they have not entered an answer, and the window is in the state where it is awaiting an answer:
                    if(self.user.timeConfig):
                        # If the user has timers enabled in their settings, calculate the time remaining.
                        timeRemaining = currentQuestionStartTime -  time.clock()
                        if(self.user.timeConfig == 1):
                            # If the timer setting is set to long, time allowed is 5 seconds + 5 per difficulty level.
                            timeRemaining += 5 + self.quiz.difficulty * 5
                        else:
                            # If the timer is set to short, it is half the long time.
                            timeRemaining += 2.5 + self.quiz.difficulty * 2.5
                        if(timeRemaining <= 0):
                            # If the user has ran out of time:
                            # Display 'Out of time!', in red, where the countdown timer was.
                            self.timeLimitLabel.config(text = "Out of time!", fg = "red")
                            for i in range(len(self.answerButtons)):
                                # For each of the answer buttons:
                                if(i == correctAnswer):
                                    # Make the text green if it was the correct button
                                    self.answerButtons[i].config(fg = "green")
                                else:
                                    # Make the text red if it was the wrong button
                                    self.answerButtons[i].config(fg = "red")
                            self.currentState = 1
                            # Display the next question after 5 seconds of delay.
                            answerTime = time.clock() + 5
                        else:
                            # If the user still has time left, display the remaining time in seconds, rounded up to the nearest integer.
                            self.timeLimitLabel.config(text = str(maths.ceil(timeRemaining)), fg = "black")
                elif(self.currentState == 1 and answerTime <= time.clock()):
                    # If the delay after answering a question is over, show the next question.
                    self.questionNumber += 1
            # Wait 0.1 seconds before running through the loop again, to reduce load on CPU.
            time.sleep(0.1)
        # If the user has finished the quiz and hasn't terminated the quiz elsewhere:
        if(self.currentState == 2):
            # Remove the buttons
            self.unloadQuestionView()
            # Calculate the average time to answer a question.
            averageAnswerTime = sum(self.timesTakenToAnswer) / len(self.timesTakenToAnswer)
            self.totalDuration = time.clock() - self.totalPausedDuration - self.startTime
            # Display the user's performance statistics.
            self.loadFinishedView()
            self.running = True
            import datetime
            # Adds the result to the database.
            self.parent.database.execute("INSERT INTO `Results` (UserID, QuizID, Score, DateCompleted, AverageAnswerTime, TotalDuration) VALUES (?, ?, ?, ?, ?, ?);",
                    float(self.user.id), float(self.quiz.id), self.numberOfCorrectAnswers / len(self.quiz.questions), datetime.datetime.now(), averageAnswerTime, self.totalDuration)
            
            # Keep the window alive before closing it, so the user has time to read the results.
            while(self.running):
                time.sleep(0.1)
        # Reload the quiz list in case the best attempt of the quiz has changed.
        self.parent.refreshList()
        self.parent.unloadSidePanel()
        self.parent.loadSidePanel()
        # Destroy the window after everything has finished.
        self.window.destroy()
    
    def unloadQuestionView(self) -> None:
        """This method removes all the buttons of the quiz, ready to display the end screen statistics."""
        self.timeLimitLabel.destroy()
        for i in self.answerButtons:
            i.destroy()
        self.hintButton.destroy()
        self.helpButton.destroy()
        self.pauseButton.destroy()
        self.endQuizButton.destroy()
    
    def loadFinishedView(self) -> None:
        """This method displays the end of quiz statistics, after the user has finished the quiz."""
        self.questionLabel.config(text = "Quiz Completed!", anchor = tk.CENTER)
        self.scoreLabel = tk.Label(self.window, text = "Score: " + str(self.numberOfCorrectAnswers) + "/" + str(len(self.quiz.questions)), font = self.questionFont)
        timeTakenString = (str(round(self.totalDuration // 60)) + "m " if self.totalDuration >= 60 else "") + (str(round((maths.ceil(self.totalDuration * 10) / 10) % 60, 1)) + "s" if round((maths.ceil(self.totalDuration * 10) / 10) % 60, 1) else "")
        self.timeLabel = tk.Label(self.window, text = "Time taken: " + timeTakenString, font = self.questionFont)
        self.scoreLabel.grid(row = 3, column = 0)
        self.timeLabel.grid(row = 4, column = 0)
    
    def finish(self) -> None:
        """This destroys the window after all the previous tasks are finished, by setting running to false, so the window closes once the thread has finished its last iteration."""
        self.running = False
