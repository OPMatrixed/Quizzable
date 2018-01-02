"""
This file contains both the Question and Quiz classes.
The Question class holds the data on a question that has been taken from the database or imported,
and the Quiz class holds the Question objects and handles saving and loading to and from the database,
as well as importing and exporting quizzes into a non-database format.
"""

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
        # If the question doesn't have an ID, add it to the database.
        if(id == -1):
            # As a different amount of wrong answers can be entered into records, the SQL statement should change depending on how many wrong
            # answers there are. If there is one wrong answer, don't modify the original statement.
            # If there are two or three wrong answers, add their respective column names to the SQL statement.
            answerAdditionString = ""
            if(len(self.otherAnswers) == 3):
                answerAdditionString = " Answer3, Answer4,"
            elif(len(self.otherAnswers) == 2):
                answerAdditionString = " Answer3,"
            # The "*self.otherAnswers" on the following line goes through each element in the list, and passes each as a separate argument.
            self.dbm.execute("INSERT INTO Questions (QuizID, Question, CorrectAnswer, Answer2,"+answerAdditionString+" Hint, Help) VALUES (?,?,?,?,?,?)",
                    self.quizID, self.question, self.correctAnswer, self.correctAnswer, *self.otherAnswers, self.hint, self.help)
    
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
        # The [:] part creates a copy of the otherAnswers list, without shuffling the Question object's actual list in-line
        answers = self.otherAnswers[:]
        random.shuffle(answers)
        index = random.randint(0, len(self.otherAnswers))
        answers.insert(index, self.correctAnswer)
        return answers, index
    
    def getQuestionFromDatabaseRecord(record: tuple): # This is not called on an object, but the class itself.
        """This will take a record from the database as a tuple and return a Question object from the data it is given."""
        # The following lines get each of the required data fields to make a Question object.
        questionID = record[0]
        quizID = record[1]
        question = record[2]
        correctAnswer = record[3]
        otherAnswers = [i for i in record[4:7] if i] # This creates a list of the other answers, but won't include the answers that are null in the database (i.e. if there are only 1 or 2 other answers).
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
    
    def save(self) -> None:
        """This will save a quiz to the database."""
        pass # TODO
    
    def exportQuiz(self, filename: str) -> None:
        """This will export the quiz into a non-database format, probably XML, YAML or using pickle."""
        pass # TODO
    
    # Methods below are not executed on an object, but the Quiz class itself.
    # i.e. to use these methods you wouldn't need a quiz object ( q = Quiz(args here); q.loadQuiz(other args here) - this is wrong)
    # but you still execute them on the Quiz class ( q = Quiz.loadQuiz(args here) - loadQuiz returns a Quiz object, correct way to use ).
    
    def getQuizzes() -> list: # This is not called on an object, but the class itself.
        """This will load the quizzes from the database."""
        pass # TODO
    
    def getQuiz(id: int, database) -> 'Quiz': # This is not called on an object, but the class itself.
        """This will load a quiz given a quiz ID, and return it as a Quiz object."""
        rows = database.execute("SELECT * FROM `Quizzes` WHERE `QuizID`=?;", id)
        if(rows): # This checks if the 'rows' list is not empty. This uses the property that empty lists in python are treated as false by if and while statements, and non-empty lists are true.
            record = rows[0]
            questionRows = database.execute("SELECT * FROM `Questions` WHERE `QuizID`=?;", id)
            questionList = [Question.getQuestionFromDatabaseRecord(i) for i in questionRows] # This turns all the question records to a list of question objects.
            title = record[1]
            subjectID = record[2]
            examboardID = record[3]
            amountOfQuestions = record[4]
            if(len(questionList) != amountOfQuestions):
                raise Error("The number of questions in the quiz found doesn't match the expected amount of questions for that quiz.")
            tags = record[5].split(",") if record[5] else [] # This will generate a list of tags (they are comma-separated), and if there are no tags it will be an empty list.
            difficulty = record[6]
            return Quiz(database, id, title, tags, subjectID, examboardID, difficulty, questionList) # This creates the quiz object and returns it.
        else:
            raise IndexError("No quiz found at the given id.")
    
    def importQuiz(filename: str) -> 'Quiz': # This is not called on an object, but the class itself.
        """
        This will import a quiz from outside the database (i.e. from a file), and load it as a Quiz object.
        This will save it to the database by default.
        """
        pass # TODO
