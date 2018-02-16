"""
This file contains both the Question and Quiz classes.
The Question class holds the data on a question that has been taken from the database or imported,
and the Quiz class holds the Question objects and handles saving and loading to and from the database,
as well as importing and exporting quizzes into a non-database format.
"""

import xml.etree.ElementTree as et

class Question(object):
    def __init__(self, quizID: int, question: str, correctAnswer: str, otherAnswers: list, id: int, hint: str, help: str) -> None:
        """This is the Question object creation method, and it expects all arguments listed above."""
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
        Quiz object creation method, all parameters except the questions are required,
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
    
    def exportQuiz(self, filename: str) -> None:
        """This will export the quiz into a non-database format, probably XML, YAML or using pickle."""
        pass # TODO
    
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
        This will import a quiz from outside the database (i.e. from a file), and load it as a Quiz object.
        This will save it to the database by default.
        """
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
        if(subject):
            subject = subject.text
            for i in parent.inverseSubjectDictionary.keys():
                if(subject.lower() == i.lower()):
                    subjectID = parent.inverseSubjectDictionary[i]
        examBoard = metadata.find("examBoardName")
        examBoardID = -1
        if(examBoard):
            examBoard = examBoard.text
            for i in parent.inverseExamboardDictionary.keys():
                if(examBoard.lower() == i.lower()):
                    examBoardID = parent.inverseExamboardDictionary[i]
        tags = []
        tagsElement = metadata.find("tags")
        if(tagsElement):
            for i in tagsElement.findall("tag"):
                if(i and i.text):
                    tags.append(i.text)
        # TODO: Load the questions
        
