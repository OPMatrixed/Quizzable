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
        self.wrongAnswers = otherAnswers
        self.id = id
        self.hint = hint
        self.help = help
        # If the question doesn't have an ID, add it to the database.
        if(id == -1):
            # As a different amount of wrong answers can be entered into records, the SQL statement should change depending on how many wrong
            # answers there are. If there is one wrong answer, don't modify the original statement.
            # If there are two or three wrong answers, add their respective column names to the SQL statement.
            answerAdditionString = ""
            if(len(self.wrongAnswers) == 3):
                answerAdditionString = " Answer3, Answer4,"
            elif(len(self.wrongAnswers) == 2):
                answerAdditionString = " Answer3,"
            # The "*self.wrongAnswers" on the following line goes through each element in the list, and passes each as a separate argument.
            self.dbm.execute("INSERT INTO Questions (QuizID, Question, CorrectAnswer, Answer2,"+answerAdditionString+" Hint, Help) VALUES (?,?,?,?,?,?)",
                    self.quizID, self.question, self.correctAnswer, self.correctAnswer, *self.wrongAnswers, self.hint, self.help)
    
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
        answers = random.shuffle(self.otherAnswers[:])
        index = random.randint(0, len(self.otherAnswers))
        answers.insert(index, self.correctAnswer)
        return answers, index

class Quiz(object):
    def __init__(self, databaseManager, name: str, tags: list, subject: int, examBoard: int, difficulty: int, questions: list = []) -> None:
        """
        Quiz object creation method, all parameters except the questions are required,
        questions can be added later through the preferred addQuestion method.
        """
        self.dbm = databaseManager
        self.name = name
        self.tags = tags
        self.subject = subject
        self.difficulty = difficulty
        self.examBoard = examBoard
        self.questions = questions
        
    def addQuestion(self, question: str, correctAnswer: str, otherAnswers: list) -> None:
        """This method adds a question to the quiz object based on the parameters given."""
        id = -1 # TODO: get id from database index.
        q  = Question(self.dbm, question, correctAnswer, otherAnswers, id)
        self.questions.append(q)
    
    def save(self) -> None:
        """This will save a quiz to the database."""
        pass # TODO
    
    # Methods below are not executed on an object, but the Quiz class itself.
    # i.e. to use these methods you wouldn't need a quiz object ( q = Quiz(args here); q.loadQuiz(other args here) - this is wrong)
    # but you still execute them on the Quiz class ( q = Quiz.loadQuiz(args here) - loadQuiz returns a Quiz object, correct way to use ).
    
    def getQuizzes() -> list: # This is not called on an object, but the class itself.
        """This will load the quizzes from the database."""
        pass # TODO
    
    def exportQuiz(self, filename: str) -> None:
        """This will export the quiz into a non-database format, probably XML, YAML or using pickle."""
        pass # TODO
    
    def importQuiz(filename: str) -> 'Quiz': # This is not called on an object, but the class itself.
        """
        This will import a quiz from outside the database (i.e. from a file), and load it as a Quiz object.
        This will save it to the database by default.
        """
        pass # TODO
