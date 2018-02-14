"""This file will handle the GUI for creating and editing quizzes."""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import tkinter.messagebox as tkmb
import re

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
        # Add all the widgets to the window.
        self.loadScreenElements()
        self.setupQuestionsFrame()
        # Adds an empty question row when launching the window.
        self.addNewQuestion()
    
    def loadScreenElements(self):
        """This loads all the widgets onto the screen."""
        
        # Configure the grid
        self.window.grid_columnconfigure(1, weight = 1)
        self.window.grid_columnconfigure(3, weight = 1)
        self.window.grid_rowconfigure(3, pad = 12)
        self.window.grid_rowconfigure(4, weight = 1)
        
        # Creating variables to be changed by user
        self.nameString = tk.StringVar()
        self.subjectString = tk.StringVar()
        self.examBoardString = tk.StringVar()
        self.difficultyString = tk.StringVar()
        self.tagsString = tk.StringVar()
        
        # Creating the labels for each entry field.
        self.nameLabel = tk.Label(self.window, text = "Name:")
        self.examBoardLabel = tk.Label(self.window, text = "Exam board:")
        self.subjectLabel = tk.Label(self.window, text = "Subject:")
        self.difficultyLabel = tk.Label(self.window, text = "Difficulty:")
        self.tagsLabel = tk.Label(self.window, text = "Tags (separate using commas):")
        # Creating the text fields and drop down menus.
        self.nameEntry = tk.Entry(self.window, textvariable = self.nameString)
        self.examBoardCombobox = ttk.Combobox(self.window, textvariable = self.examBoardString, state = "readonly", values = ["None"] + list(self.parent.examboardDictionary.values()))
        self.subjectCombobox = ttk.Combobox(self.window, textvariable = self.subjectString, state = "readonly", values = ["None"] + list(self.parent.subjectDictionary.values()))
        self.difficultyCombobox = ttk.Combobox(self.window, textvariable = self.difficultyString, state = "readonly", values = [1, 2, 3, 4, 5])
        self.tagsEntry = tk.Entry(self.window, textvariable = self.tagsString)
        self.finishButton = tk.Button(self.window, text = "Finish Quiz", command = self.submit)
        self.addQuestionButton = tk.Button(self.window, text = "Add another question", command = self.addNewQuestion)
        # Adding visual horizontal separator bar between questions and quiz data.
        self.horizontalSeparator = ttk.Separator(self.window, orient = "horizontal")
        
        # Placing all the elements on the window.
        self.nameLabel.grid(row = 0, column = 0)
        self.examBoardLabel.grid(row = 0, column = 2)
        self.subjectLabel.grid(row = 1, column = 0)
        self.difficultyLabel.grid(row = 1, column = 2)
        self.tagsLabel.grid(row = 2, column = 0, columnspan = 2)
        # padx is horizontal padding in pixels around the element, pady is vertical padding, ipadx is internal horizontal padding, ipady is internal vertical padding.
        self.nameEntry.grid(row = 0, column = 1, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W + tk.E)
        self.examBoardCombobox.grid(row = 0, column = 3, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W + tk.E)
        self.subjectCombobox.grid(row = 1, column = 1, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W + tk.E)
        self.difficultyCombobox.grid(row = 1, column = 3, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W + tk.E)
        self.tagsEntry.grid(row = 2, column = 2, columnspan = 2, padx = 5, pady = 2, ipadx = 4, ipady = 2, sticky = tk.W + tk.E)
        self.finishButton.grid(row = 0, column = 4)
        self.addQuestionButton.grid(row = 2, column = 4)
        self.horizontalSeparator.grid(row = 3, column = 0, columnspan = 5, sticky = tk.W + tk.E)
    
    def setupQuestionsFrame(self):
        """This creates a questions frame where the user can create questions and enter the question details."""
        # Creating the scrollbar for scrolling through the list of questions if the window can't contain all of them.
        self.frameScrollbar = tk.Scrollbar(self.window)
        # The question entries will be placed on a Canvas widget, a sort of 'hacky' way to allow me to scroll through a list of elements with tkinter.
        self.questionsCanvas = tk.Canvas(self.window, yscrollcommand = self.frameScrollbar.set, bd = 0, highlightthickness = 0)
        self.frameScrollbar.config(command = self.questionsCanvas.yview)
        # Placing the canvas and scroll bar.
        self.questionsCanvas.grid(row = 4, column = 0, columnspan = 5, sticky = tk.W+tk.E+tk.N+tk.S, pady = 10)
        self.frameScrollbar.grid(row = 0, column = 5, rowspan = 5, sticky = tk.N+tk.S)
        # Creating a frame to hold all the questions.
        self.questionsFrame = tk.Frame(self.window)
        self.questionFrameID = self.questionsCanvas.create_window((0, 0), window = self.questionsFrame, anchor = tk.N+tk.W)
        # If the size of the window changes, then the size of the internal frame needs to change, as well as the 'scroll region'.
        self.questionsFrame.bind("<Configure>", lambda e: self.questionsCanvas.config(scrollregion = "0 0 " + str(self.questionsFrame.winfo_reqwidth()) + " " + str(self.questionsFrame.winfo_reqheight())))
        self.questionsCanvas.bind("<Configure>", lambda e: self.questionsCanvas.itemconfigure(self.questionFrameID, width = self.questionsCanvas.winfo_width()))
        
        for i in range(7):
            # Setting all of the column weights.
            self.questionsFrame.grid_columnconfigure(i, weight = 1, minsize = 40)
        
        # Add a new question button at the end of all the questions.
        self.addNewQuestionButton = tk.Button(self.questionsFrame, text = "Add another question", command = self.addNewQuestion)
        self.addNewQuestionButton.grid(row = 5000, column = 0, columnspan = 8)
        # Creating a dictionary to hold all the question widgets that are generated.
        self.questions = {}
        self.questionIndex = 1
        # Creating the headings for each of the entry columns.
        self.frameQuestionLabel = tk.Label(self.questionsFrame, text = "Question")
        self.frameCorrectAnswerLabel = tk.Label(self.questionsFrame, text = "Correct Answer")
        self.frameAnswer2Label = tk.Label(self.questionsFrame, text = "Answer 2")
        self.frameAnswer3Label = tk.Label(self.questionsFrame, text = "Answer 3")
        self.frameAnswer4Label = tk.Label(self.questionsFrame, text = "Answer 4")
        self.frameHintLabel = tk.Label(self.questionsFrame, text = "Hint")
        self.frameHelpLabel = tk.Label(self.questionsFrame, text = "Help")
        # Positioning all the headings for the entry columns.
        self.frameQuestionLabel.grid(row = 0, column = 0)
        self.frameCorrectAnswerLabel.grid(row = 0, column = 1)
        self.frameAnswer2Label.grid(row = 0, column = 2)
        self.frameAnswer3Label.grid(row = 0, column = 3)
        self.frameAnswer4Label.grid(row = 0, column = 4)
        self.frameHintLabel.grid(row = 0, column = 5)
        self.frameHelpLabel.grid(row = 0, column = 6)
    
    def addNewQuestion(self):
        """This generates a new row of question field entries below the last added question row."""
        myindex = self.questionIndex
        self.questionIndex += 1
        # Creating all of the text entries.
        question = tk.Entry(self.questionsFrame)
        correctAnswer = tk.Entry(self.questionsFrame)
        answer2 = tk.Entry(self.questionsFrame)
        answer3 = tk.Entry(self.questionsFrame)
        answer4 = tk.Entry(self.questionsFrame)
        hint = tk.Entry(self.questionsFrame)
        help = tk.Entry(self.questionsFrame)
        # Adding a delete button that will remove the question if the "X" button is clicked.
        deleteButton = tk.Button(self.questionsFrame, text = "X", command = lambda: self.removeQuestion(myindex))
        # Positioning all of the entries on the current question row.
        question.grid(row = self.questionIndex, column = 0, sticky = tk.W+tk.E)
        correctAnswer.grid(row = self.questionIndex, column = 1, sticky = tk.W+tk.E)
        answer2.grid(row = self.questionIndex, column = 2, sticky = tk.W+tk.E)
        answer3.grid(row = self.questionIndex, column = 3, sticky = tk.W+tk.E)
        answer4.grid(row = self.questionIndex, column = 4, sticky = tk.W+tk.E)
        hint.grid(row = self.questionIndex, column = 5, sticky = tk.W+tk.E)
        help.grid(row = self.questionIndex, column = 6, sticky = tk.W+tk.E)
        deleteButton.grid(row = self.questionIndex, column = 7)
        # Adding the row of entries to the quiz dictionary, to keep references to the entry fields so the data inside them can be gathered when the quiz is saved.
        self.questions[myindex] = [question, correctAnswer, answer2, answer3, answer4, hint, help, deleteButton]
    
    def removeQuestion(self, index):
        """This removes a question from the list at a given index."""
        for i in range(8):
            # Goes through all the elements and deletes them.
            self.questions[index][i].destroy()
        # Removes the question row entry from the dictionary.
        del self.questions[index]
    
    def submit(self):
        """Gets all the details and questions and saves them in the database."""
        import quiz
        # Get the quiz details from the entry boxes.
        title = self.nameString.get().strip()
        subject = self.subjectString.get()
        examBoard = self.examBoardString.get()
        difficulty = self.difficultyString.get()
        tags = self.tagsString.get()
        # Title length check, show an error message if it's too long or too short.
        if(len(title) < 3):
            tkmb.showerror("Title error", "Quiz title is too short, it should be at least 3 characters long (currently: " + str(len(title)) + ").", parent = self.window)
            return
        if(len(title) > 70):
            tkmb.showerror("Title error", "Quiz title is too long, it should be at most 70 characters long (currently: " + str(len(title)) + ").", parent = self.window)
            return
        # Regular expression to check if the title has any invalid characters.
        quizTitleRegex = re.compile('[^a-zA-Z0-9\.\-\? ]')
        reducedTitle = quizTitleRegex.sub("", title)
        if(reducedTitle != title):
            tkmb.showerror("Title error", "Quiz title contains invalid characters, it should only contain english letters, numbers, spaces, dashes, question marks, or full stops/periods.", parent = self.window)
            return
        # Presence check on difficulty drop-down entry box.
        if(not difficulty):
            tkmb.showerror("Difficulty error", "No difficulty has been set for this quiz.", parent = self.window)
            return
        # Length check on tag entry.
        if(len(tags) > 150):
            tkmb.showerror("Tags error", "Tag list is too long, it should be at most 150 characters long (currently: " + str(len(title)) + ").", parent = self.window)
            return
        # Reformatting tags in case the user hasn't entered in the correct format, by removing all whitespace that would be adjacent to a comma.
        tagList = []
        for i in tags.split(","):
            if(i.strip() == ""):
                continue
            tagList.append(i.strip().lower())
        tags = ",".join(tagList)
        # Validating all the questions.
        questions = []
        for i in self.questions.keys():
            # For each question, get all the entered fields.
            questionText = self.questions[i][0].get()
            correctAnswer = self.questions[i][1].get()
            otherAnswers = []
            answer2 = self.questions[i][2].get()
            answer3 = self.questions[i][3].get()
            answer4 = self.questions[i][4].get()
            if(answer2):
                otherAnswers.append(answer2)
            if(answer3):
                otherAnswers.append(answer3)
            if(answer4):
                otherAnswers.append(answer4)
            hint = self.questions[i][5].get()
            help = self.questions[i][6].get()
            # Create a question object and check if it is valid.
            q = quiz.Question(-1, questionText, correctAnswer, otherAnswers, -1, hint, help)
            errorText = q.validate()
            if(errorText):
                # If it's invalid, show an error, and then return.
                tkmb.showerror("Question error", "Question (\"" + errorText + "\") has error: " + errorText, parent = self.window)
                return
            questions.append(q)
        # If there are less than 2 questions, show an error, and the return.
        if(len(questions) < 2):
            tkmb.showerror("Question error", "Quiz should have at least 2 questions.", parent = self.window)
            return
        # Get the subject and/or exam board ID from the text entry.
        subjectID = None
        examBoardID = None
        # It will only get them if the field has text in it, that isn't "None".
        if(subject):
            subjectID = self.parent.inverseSubjectDictionary.get(subject, None)
        if(subjectID != None):
            subjectID = float(subjectID)
        
        if(examBoard):
            examBoardID = self.parent.inverseExamboardDictionary.get(examBoard, None)
        if(examBoardID != None):
            examBoardID = float(examBoardID)
        
        # Check if any other quizzes have the same title. # TODO: Check if other quizzes have same hash.
        quizzesWithSameTitle = self.parent.database.execute("SELECT * FROM `Quizzes` WHERE `QuizName`=?;", title)
        if(len(quizzesWithSameTitle) > 0):
            tkmb.showerror("Quiz error", "Quiz name is already in use.", parent = self.window)
            return
        
        # Adding the quiz to the database, if all checks have passed.
        self.parent.database.execute("INSERT INTO `Quizzes` (QuizName, SubjectID, ExamboardID, AmountOfQuestions, TagList, Difficulty)" +
                                        "VALUES (?,?,?,?,?,?);", title, subjectID, examBoardID, float(len(questions)), tags, float(difficulty))
        
        # Getting the ID of the record that was just added.
        lastRecord = self.parent.database.execute("SELECT @@IDENTITY;")
        quizID = lastRecord[0][0]
        for i in questions:
            # For each question, give it the Quiz's ID, and then add it to the database.
            i.quizID = quizID
            i.addToDatabase(self.parent.database)
        # Reload the quiz list on the quiz browser to show the new quiz.
        self.parent.refreshList()
        # Exit the window upon successfully creating the quiz.
        self.window.destroy()
    
    def exit(self):
        """This function is run when the window is being closed without saving."""
        # TODO: Check if user has entered data into the fields on the window.
        if(tkmb.askyesno("Close without saving", "Are you sure you want to exit? The quiz hasn't been saved. To save, click the 'Finish Quiz' button.", parent = self.window)):
            # The line above asks if the user is sure they want to exit with a popup yes/no dialog, if so then it closes the window with the line below.
            # If the user clicks 'No', then the prompt closes and nothing else happens.
            self.window.destroy()

class QuizEditorDialog(QuizCreatorDialog):
    """This inherits the methods of QuizCreatorDialog."""
    def __init__(self, toplevel: tk.Tk, parent, quiz):
        """
        This is the quiz editor window, and this constructor method is run when creating the QuizEditorDialog object.
        
        toplevel is the tkinter object of the parent window.
        parent in the MainApp object, unless another dialog opens this window.
        """
        self.parent = parent
        self.toplevel = toplevel
        self.quiz = quiz
        # This creates the window. padx and pady here add 5 pixels padding horizontally and vertically respectively
        # This is to stop the widgets on the window from touching the edges of the window, which doesn't look that good.
        self.window = tk.Toplevel(toplevel, padx = 5, pady = 5)
        # Dimensions of the window: 500 pixels wide by 300 pixels high.
        self.window.geometry("900x600")
        # The minimum dimensions of the window, as this window is re-sizable.
        self.window.minsize(width = 600, height = 500)
        # Setting the title of the window.
        self.window.title(quiz.name + " - Edit Quiz - Quizzable")
        # This makes the self.quit method run when the window is closed without clicking the "Finish Quiz" button.
        self.window.protocol("WM_DELETE_WINDOW", self.quit)
        # Add all the widgets to the window.
        self.loadScreenElements()
        self.setupQuestionsFrame()
        # Need to rebind the "Finish Quiz" button to run the save changes method, rather than save a new quiz to the database method that was inherited.
        self.finishButton.config(command = self.update)
        # For editing a quiz, all the original quiz data needs to be re-entered.
        self.fillInExistingData()
        
        for i in self.quiz.questions:
            self.addQuestion(i)
    
    def fillInExistingData(self):
        self.nameString.set(self.quiz.name)
        if(self.quiz.subject):
            self.subjectString.set(self.parent.subjectDictionary[self.quiz.subject])
        if(self.quiz.examBoard):
            self.examBoardString.set(self.parent.examboardDictionary[self.quiz.examBoard])
        self.difficultyString.set(str(self.quiz.difficulty))
        self.tagsString.set(",".join(self.quiz.tags))
        
    def addQuestion(self, currentQuestion):
        """This generates a new row of question field entries below the last added question row."""
        myindex = self.questionIndex
        self.questionIndex += 1
        # Creating all of the text entries.
        question = tk.Entry(self.questionsFrame)
        correctAnswer = tk.Entry(self.questionsFrame)
        answer2 = tk.Entry(self.questionsFrame)
        answer3 = tk.Entry(self.questionsFrame)
        answer4 = tk.Entry(self.questionsFrame)
        hint = tk.Entry(self.questionsFrame)
        help = tk.Entry(self.questionsFrame)
        # Adding a delete button that will remove the question if the "X" button is clicked.
        deleteButton = tk.Button(self.questionsFrame, text = "X", command = lambda: self.removeQuestion(myindex))
        # Positioning all of the entries on the current question row.
        question.grid(row = self.questionIndex, column = 0, sticky = tk.W+tk.E)
        correctAnswer.grid(row = self.questionIndex, column = 1, sticky = tk.W+tk.E)
        answer2.grid(row = self.questionIndex, column = 2, sticky = tk.W+tk.E)
        answer3.grid(row = self.questionIndex, column = 3, sticky = tk.W+tk.E)
        answer4.grid(row = self.questionIndex, column = 4, sticky = tk.W+tk.E)
        hint.grid(row = self.questionIndex, column = 5, sticky = tk.W+tk.E)
        help.grid(row = self.questionIndex, column = 6, sticky = tk.W+tk.E)
        deleteButton.grid(row = self.questionIndex, column = 7)
        
        # Inserting the data from the existing quiz.
        question.insert(0, currentQuestion.question)
        correctAnswer.insert(0, currentQuestion.correctAnswer)
        answer2.insert(0, currentQuestion.otherAnswers[0])
        if(len(currentQuestion.otherAnswers) > 1):
            answer3.insert(0, currentQuestion.otherAnswers[1])
        if(len(currentQuestion.otherAnswers) > 2):
            answer4.insert(0, currentQuestion.otherAnswers[2])
        if(currentQuestion.hint):
            hint.insert(0, currentQuestion.hint)
        if(currentQuestion.help):
            help.insert(0, currentQuestion.help)
        
        # Adding the row of entries to the quiz dictionary, to keep references to the entry fields so the data inside them can be gathered when the quiz is saved.
        self.questions[myindex] = [question, correctAnswer, answer2, answer3, answer4, hint, help, deleteButton]
    
    def update(self):
        """This method updates all of the database entries, deletes questions that have been removed and adds questions that have been added."""
        import quiz
        # Get the quiz details from the entry boxes.
        title = self.nameString.get().strip()
        subject = self.subjectString.get()
        examBoard = self.examBoardString.get()
        difficulty = self.difficultyString.get()
        tags = self.tagsString.get()
        # Title length check, show an error message if it's too long or too short.
        if(len(title) < 3):
            tkmb.showerror("Title error", "Quiz title is too short, it should be at least 3 characters long (currently: " + str(len(title)) + ").", parent = self.window)
            return
        if(len(title) > 70):
            tkmb.showerror("Title error", "Quiz title is too long, it should be at most 70 characters long (currently: " + str(len(title)) + ").", parent = self.window)
            return
        # Regular expression to check if the title has any invalid characters.
        quizTitleRegex = re.compile('[^a-zA-Z0-9\.\-\? ]')
        reducedTitle = quizTitleRegex.sub("", title)
        if(reducedTitle != title):
            tkmb.showerror("Title error", "Quiz title contains invalid characters, it should only contain english letters, numbers, spaces, dashes, question marks, or full stops/periods.", parent = self.window)
            return
        # Presence check on difficulty drop-down entry box.
        if(not difficulty):
            tkmb.showerror("Difficulty error", "No difficulty has been set for this quiz.", parent = self.window)
            return
        # Length check on tag entry.
        if(len(tags) > 150):
            tkmb.showerror("Tags error", "Tag list is too long, it should be at most 150 characters long (currently: " + str(len(title)) + ").", parent = self.window)
            return
        # Reformatting tags in case the user hasn't entered in the correct format, by removing all whitespace that would be adjacent to a comma.
        tagList = []
        for i in tags.split(","):
            if(i.strip() == ""):
                continue
            tagList.append(i.strip())
        tags = ",".join(tagList)
        # Validating all the questions.
        questions = []
        for i in self.questions.keys():
            # For each question, get all the entered fields.
            questionText = self.questions[i][0].get()
            correctAnswer = self.questions[i][1].get()
            otherAnswers = []
            answer2 = self.questions[i][2].get()
            answer3 = self.questions[i][3].get()
            answer4 = self.questions[i][4].get()
            if(answer2):
                otherAnswers.append(answer2)
            if(answer3):
                otherAnswers.append(answer3)
            if(answer4):
                otherAnswers.append(answer4)
            hint = self.questions[i][5].get()
            help = self.questions[i][6].get()
            # Create a question object and check if it is valid.
            q = quiz.Question(-1, questionText, correctAnswer, otherAnswers, -1, hint, help)
            errorText = q.validate()
            if(errorText):
                # If it's invalid, show an error, and then return.
                tkmb.showerror("Question error", "Question (\"" + errorText + "\") has error: " + errorText, parent = self.window)
                return
            questions.append(q)
        # If there are less than 2 questions, show an error, and the return.
        if(len(questions) < 2):
            tkmb.showerror("Question error", "Quiz should have at least 2 questions.", parent = self.window)
            return
        # Get the subject and/or exam board ID from the text entry.
        subjectID = None
        examBoardID = None
        # It will only get them if the field has text in it, that isn't "None".
        if(subject):
            subjectID = self.parent.inverseSubjectDictionary.get(subject, None)
        if(subjectID != None):
            subjectID = float(subjectID)
        
        if(examBoard):
            examBoardID = self.parent.inverseExamboardDictionary.get(examBoard, None)
        if(examBoardID != None):
            examBoardID = float(examBoardID)
        
        # Check if any other quizzes have the same title. # TODO: Check if other quizzes have same hash.
        quizzesWithSameTitle = self.parent.database.execute("SELECT * FROM `Quizzes` WHERE `QuizName`=?;", title)
        if(len(quizzesWithSameTitle) > 0 and quizzesWithSameTitle[0][0] != self.quiz.id):
            tkmb.showerror("Quiz error", "Quiz name is already in use.", parent = self.window)
            return
        
        # Update the quiz record
        self.parent.database.execute("UPDATE `Quizzes` SET QuizName=?, SubjectID=?, ExamboardID=?, AmountOfQuestions=?, TagList=?, Difficulty=? WHERE QuizID=?;",
                                        title, subjectID, examBoardID, float(len(questions)), tags, float(difficulty), self.quiz.id)
        # Remove the old questions
        self.parent.database.execute("DELETE FROM `Questions` WHERE QuizID=?;", self.quiz.id)
        # Add the new questions in
        for i in questions:
            i.quizID = self.quiz.id
            i.addToDatabase(self.parent.database)
        
        # Reload the quiz list on the quiz browser to show the new quiz.
        self.parent.refreshList()
        # Exit the window upon successfully creating the quiz.
        self.window.destroy()
    
    def quit(self):
        """This function is run when the window is being closed without saving."""
        # TODO: Check if fields have changed.
        if(tkmb.askyesno("Close without saving", "Are you sure you want to exit? The quiz hasn't been saved. To save, click the 'Finish Quiz' button.", parent = self.window)):
            # The line above asks if the user is sure they want to exit with a popup yes/no dialog, if so then it closes the window with the line below.
            # If the user clicks 'No', then the prompt closes and nothing else happens.
            self.window.destroy()
