"""
This file contains both the Question and Quiz classes.
The Question class holds the data on a question that has been taken from the database or imported,
and the Quiz class holds the Question objects and handles saving and loading to and from the database,
as well as importing and exporting quizzes into a non-database format.
"""

# This is used to parse the XML quiz files.
import xml.etree.ElementTree as et
# Regular expressions are used for validating quizzes being imported.
import re
# For showing import/export messages
import tkinter.messagebox as tkmb

class Question(object):
    def __init__(self, quizID: int, question: str, correctAnswer: str, otherAnswers: list, id: int, hint: str, help: str) -> None:
        """This is the Question constructor, and it expects all arguments listed above."""
        self.quizID = quizID
        self.question = question
        self.correctAnswer = correctAnswer
        self.otherAnswers = otherAnswers
        self.id = id
        self.hint = hint
        self.help = help
    
    def validate(self):
        """
        Running this function validates whether all of the variables are correct and ready to use and/or store in the database.
        If something goes wrong, it returns a string containing an error message of the first error it encountered.
        If all the checks pass, it doesn't return anything.
        """
        # Type checks
        if(not isinstance(self.question, str)):
            return "Question is not a string."
        if(not isinstance(self.correctAnswer, str)):
            return "Correct answer is not a string."
        if(not isinstance(self.hint, str)):
            return "Hint is not a string."
        if(not isinstance(self.help, str)):
            return "Help is not a string."
        if(not isinstance(self.otherAnswers, list)):
            return "Other answers is not a list."
        # Presence and length checks on the question string
        if(not self.question):
            return "No question entered."
        if(len(self.question) < 4):
            return "Question less than 4 characters."
        if(len(self.question) > 300):
            return "Question longer than 300 characters."
        # Presenece and length checks on the correct answer string
        if(not self.correctAnswer):
            return "No correct answer."
        if(len(self.correctAnswer) > 150):
            return "Correct answer is longer than 150 characters."
        # Checks on the other answer strings
        if(not self.otherAnswers):
            return "No wrong answers."
        if(len(self.otherAnswers) > 3):
            return "Too many other answers."
        for i in range(len(self.otherAnswers)):
            # Looping through all the other answer strings.
            if(not isinstance(self.otherAnswers[i], str)):
                return "Wrong answer " + str(i + 1) + " is not a string."
            if(not self.otherAnswers[i]):
                return "No wrong answer no. " + str(i + 1)
            if(len(self.otherAnswers[i]) > 150):
                return "Wrong answer no. " + str(i + 1) + " is too long."
            if(self.otherAnswers[i] == self.correctAnswer):
                return "Wrong answer no. " + str(i + 1) + " is the same as the correct answer."
        # Length check on hint/help variables, and these variables can be empty strings.
        if(len(self.hint) > 400):
            return "Hint is longer than 400 characters."
        if(len(self.help) > 2000):
            return "Help is longer than 2000 characters."
        # If it reaches here, all the checks have passed and the function returns nothing.
    
    def getShuffledAnswers(self) -> list:
        """
        Returns a shuffled set of answers, along with the correct answer's index.
        It does this by shuffling the list of wrong answers,
        then getting a random number between 0 and the amount of wrong answers
        and it then inserts the correct answer at that index in the shuffled wrong answers,
        pushing the item originally at that index and all after it back 1 index.
        It then returns a list of answers and the correct answer's index in that list.
        """
        import random
        # The [:] part creates a copy of the otherAnswers list, without it it would just create a reference to the self.otherAnswers list.
        answers = self.otherAnswers[:]
        # random.shuffle changes the list in-line, as passing the answers list as a parameter just passes a reference to the subroutine.
        random.shuffle(answers)
        index = random.randint(0, len(self.otherAnswers))
        # This adds the correct answer to the answers list, at the position of the value of 'index'
        answers.insert(index, self.correctAnswer)
        return answers, index
    
    def addToDatabase(self, database) -> None:
        # As a different amount of wrong answers can be entered into records, the SQL statement should change depending on how many wrong
        # answers there are. If there is one wrong answer, don't modify the original statement.
        # If there are two or three wrong answers, add their respective column names to the SQL statement.
        check = self.validate()
        if(check):
            # If the validation of the question fails, don't save to the database, instead raise an error.
            raise ValueError("Question: " + check)
        if(len(self.otherAnswers) == 3):
            # If there are 4 answers
            database.execute("INSERT INTO Questions (QuizID, Question, CorrectAnswer, Answer2, Answer3, Answer4, Hint, Help) VALUES (?,?,?,?,?,?,?,?)",
                float(self.quizID), self.question, self.correctAnswer, self.otherAnswers[0], self.otherAnswers[1], self.otherAnswers[2], self.hint, self.help)
        elif(len(self.otherAnswers) == 2):
            # If there are 3 answers
            database.execute("INSERT INTO Questions (QuizID, Question, CorrectAnswer, Answer2, Answer3, Hint, Help) VALUES (?,?,?,?,?,?,?)",
                float(self.quizID), self.question, self.correctAnswer, self.otherAnswers[0], self.otherAnswers[1], self.hint, self.help)
        else:
            # If there are only 2 answers
            database.execute("INSERT INTO Questions (QuizID, Question, CorrectAnswer, Answer2, Hint, Help) VALUES (?,?,?,?,?,?)",
                float(self.quizID), self.question, self.correctAnswer, self.otherAnswers[0], self.hint, self.help)
        # Gets the last changed record from the database and gets its ID.
        lastRecord = database.execute("SELECT @@IDENTITY;")
        self.id = lastRecord[0][0]
    
    def getQuestionFromDatabaseRecord(record: tuple) -> 'Question': # This is not called on an object, but the class itself.
        """This will take a record from the database as a tuple and return a Question object from the data it is given."""
        # The following lines get each of the required data fields to make a Question object.
        questionID = record[0]
        quizID = record[1]
        question = record[2]
        correctAnswer = record[3]
        # This creates a list of the other answers, but won't include the answers that are null in the database (i.e. if there are only 1 or 2 other answers).
        otherAnswers = [i for i in record[4:7] if i]
        hint = record[7]
        help = record[8]
        return Question(quizID, question, correctAnswer, otherAnswers, questionID, hint, help) # This generates the Question object and returns it.

class Quiz(object):
    def __init__(self, databaseManager, id: int, name: str, tags: list, subject: int, examBoard: int, difficulty: int, questions: list = []) -> None:
        """
        Quiz object constructor, all parameters except the questions are required,
        questions can be added later through the preferred addQuestion method.
        """
        self.dbm = databaseManager
        self.id = id
        self.name = name
        self.tags = tags
        self.subject = subject
        self.difficulty = difficulty
        self.examBoard = examBoard
        self.questions = questions
    
    def exportQuiz(self, parent, filename: str) -> None:
        """This will export the quiz into an XML file."""
        root = et.Element("quiz")
        meta = et.SubElement(root, "meta")
        et.SubElement(meta, "title").text = self.name
        if(self.subject and self.subject != -1):
            et.SubElement(meta, "subjectName").text = parent.subjectDictionary[self.subject]
        if(self.examBoard and self.examBoard != -1):
            et.SubElement(meta, "examBoardName").text = parent.examboardDictionary[self.examBoard]
        et.SubElement(meta, "difficulty").text = str(self.difficulty)
        for i in self.questions:
            question = et.SubElement(root, "question")
            et.SubElement(question, "qtext").text = i.question
            et.SubElement(question, "correctanswer").text = i.correctAnswer
            for j in i.otherAnswers:
                et.SubElement(question, "wronganswer").text = j
            et.SubElement(question, "hint").text = i.hint
            et.SubElement(question, "help").text = i.help
        def prettify(element, indent = "    "):
            queue = [(0, element)]  # (level, element)
            while queue:
                level, element = queue.pop(0)
                children = [(level + 1, child) for child in list(element)]
                if children:
                    element.text = "\n" + indent * (level + 1)  # for child open
                if queue:
                    element.tail = "\n" + indent * queue[0][0]  # for sibling open
                else:
                    element.tail = "\n" + indent * (level - 1)  # for parent close
                queue[0:0] = children  # prepend so children come before siblings
        prettify(root)
        print(str(et.tostring(root))[2:-1].replace("\\n", "\n"))
        file = open(filename, "w")
        file.write(str(et.tostring(root))[2:-1].replace("\\n", "\n"))
        file.close()
        tkmb.showinfo("Export Quiz", "Quiz successfully exported to XML, saved to: " + filename)
    
    # Methods below are not executed on an object, but the Quiz class itself.
    # i.e. to use these methods you wouldn't need a Quiz object ( q = Quiz(args here); q.getQuiz(other args here) - this is wrong)
    # but you still execute them on the Quiz class ( q = Quiz.getQuiz(args here) - getQuiz returns a Quiz object, correct way to use ).
    
    def getQuiz(id: int, database) -> 'Quiz': # This is not called on an object, but the class itself.
        """This will load a quiz given a quiz ID, and return it as a Quiz object."""
        # Queries the database to find the quiz record which is to be loaded.
        rows = database.execute("SELECT * FROM `Quizzes` WHERE `QuizID`=?;", float(id))
        # This checks if the 'rows' list is not empty. This uses the property that empty lists in python are treated as false by if and while statements, and non-empty lists are true.
        if(rows):
            # Goes through each field in the record and returns a Quiz object
            record = rows[0]
            questionRows = database.execute("SELECT * FROM `Questions` WHERE `QuizID`=?;", float(id))
            questionList = [Question.getQuestionFromDatabaseRecord(i) for i in questionRows] # This turns all the question records to a list of question objects.
            title = record[1]
            subjectID = record[2]
            examboardID = record[3]
            amountOfQuestions = record[4]
            if(len(questionList) != amountOfQuestions):
                raise Exception("The number of questions in the quiz found doesn't match the expected amount of questions for that quiz.")
            tags = record[5].split(",") if record[5] else [] # This will generate a list of tags (they are comma-separated), and if there are no tags it will be an empty list.
            difficulty = record[6]
            return Quiz(database, id, title, tags, subjectID, examboardID, difficulty, questionList) # This creates the quiz object and returns it.
        else:
            raise IndexError("No quiz found at the given id.")
    
    def importQuiz(parent, filename: str) -> 'Quiz': # This is not called on an object, but the class itself.
        """
        This will import a quiz from an XML file and load it as a Quiz object.
        It will save it to the database by default.
        """ # TODO: Run all validation checks
        tree = None
        root = None
        metadata = None
        title = None
        difficulty = None
        try:
            tree = et.parse(filename)
            root = tree.getroot()
            metadata = root.find("meta")
            title = metadata.find("title").text
            difficulty = metadata.find("difficulty").text
        except AttributeError:
            return "Invalid XML."
        subject = metadata.find("subjectName")
        subjectID = -1
        if(subject != None):
            subject = subject.text
            found = False
            for i in parent.inverseSubjectDictionary.keys():
                if(subject.lower() == i.lower()):
                    subjectID = parent.inverseSubjectDictionary[i]
                    found = True
                    break
            if(not found):
                parent.database.execute("INSERT INTO `Subjects` (SubjectName) VALUES (?);", subject)
                # This gets the inserted record's id.
                subjectID = parent.database.execute("SELECT @@IDENTITY;")[0][0]
                parent.subjectDictionary[subjectID] = subject
                parent.inverseSubjectDictionary[subject] = subjectID
                print("Subject: " + subject + " added.")
        
        examBoard = metadata.find("examBoardName")
        examBoardID = -1
        if(examBoard != None):
            examBoard = examBoard.text
            found = False
            for i in parent.inverseExamboardDictionary.keys():
                if(examBoard.lower() == i.lower()):
                    examBoardID = parent.inverseExamboardDictionary[i]
                    found = True
                    break
            if(not found):
                parent.database.execute("INSERT INTO `Examboards` (EName) VALUES (?);", examBoard)
                # This gets the inserted record's id.
                examBoardID = parent.database.execute("SELECT @@IDENTITY;")[0][0]
                parent.examboardDictionary[examBoardID] = examBoard
                parent.inverseExamboardDictionary[examBoard] = examBoardID
                print("Exam board: " + examBoard + " added.")
        
        tags = []
        tagsElement = metadata.find("tags")
        if(tagsElement != None):
            for i in tagsElement.findall("tag"):
                if(i != None and i.text.strip()):
                    tags.append(i.text.strip())
        questions = root.findall("question")
        questionList = []
        for i in questions:
            try:
                qtext = i.find("qtext").text
                correctAnswer = i.find("correctanswer").text
                wrongAnswers = [j.text for j in i.findall("wronganswer")]
            except AttributeError:
                return "Invalid question XML."
            hintElement = i.find("hint")
            helpElement = i.find("help")
            hint = hintElement.text if hintElement != None and hintElement.text else ""
            help = helpElement.text if helpElement != None and helpElement.text else ""
            question = Question(-1, qtext, correctAnswer, wrongAnswers, -1, hint, help)
            if(question.validate()):
                tkmb.showerror("Question error", "Question \"" + qtext + "\": " + question.validate(), parent = parent.tk)
                return
            questionList.append(question)
        
        # VALIDATION
        if(len(title) < 3):
            tkmb.showerror("Title error", "Quiz title is too short, it should be at least 3 characters long (currently: " + str(len(title)) + ").", parent = parent.tk)
            return
        if(len(title) > 70):
            tkmb.showerror("Title error", "Quiz title is too long, it should be at most 70 characters long (currently: " + str(len(title)) + ").", parent = parent.tk)
            return
        # Regular expression to check if the title has any invalid characters.
        quizTitleRegex = re.compile('[^a-zA-Z0-9\.\-\? ]')
        reducedTitle = quizTitleRegex.sub("", title)
        if(reducedTitle != title):
            tkmb.showerror("Title error", "Quiz title contains invalid characters, it should only contain english letters, numbers, spaces, dashes, question marks, or full stops/periods.", parent = parent.tk)
            return
        # Presence check on difficulty drop-down entry box.
        if(not difficulty):
            tkmb.showerror("Difficulty error", "No difficulty has been set for this quiz.", parent = parent.tk)
            return
        # Length check on tag entry.
        if(len(",".join(tags)) > 150):
            tkmb.showerror("Tags error", "Tag list is too long, it should be at most 150 characters long (currently: " + str(len(title)) + ").", parent = parent.tk)
            return
        
        # Adding the quiz to the database, if all checks have passed.
        parent.database.execute("INSERT INTO `Quizzes` (QuizName, SubjectID, ExamboardID, AmountOfQuestions, TagList, Difficulty)" +
                                        "VALUES (?,?,?,?,?,?);", title, float(subjectID) if subjectID != -1 else None, float(examBoardID) if examBoardID != -1 else None, float(len(questions)), ",".join(tags), float(difficulty))
        
        # Getting the ID of the record that was just added.
        lastRecord = parent.database.execute("SELECT @@IDENTITY;")
        quizID = lastRecord[0][0]
        for i in questionList:
            # For each question, give it the Quiz's ID, and then add it to the database.
            i.quizID = quizID
            i.addToDatabase(parent.database)
        tkmb.showinfo("Quiz import", "Quiz \"" + title + "\" has been successfully imported.", parent = parent.tk)
        parent.refreshList()
