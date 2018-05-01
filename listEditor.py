"""The list editor file holds the general code for list editors, as well as the more specific code for the subject and exam board list editor child classes."""

# TkInter used for GUI subroutines and classes.
import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.simpledialog as tksd
# Regular expressions are used for format checks.
import re

class ListEditor(object):
    def generateGUI(self, toplevel: tk.Tk, parent) -> None:
        """
        toplevel is the tkinter object of the parent window.
        parent in the MainApp object, unless another dialog opens this window.
        """
        self.parent = parent
        self.toplevel = toplevel
        # This creates the window. padx and pady here add 5 pixels padding horizontally and vertically respectively
        # This is to stop the widgets on the window from touching the edges of the window, which doesn't look that good.
        self.window = tk.Toplevel(toplevel, padx = 5, pady = 5)
        # This makes this window always render above the base window.
        self.window.transient(self.toplevel)
        # Dimensions of the window: 500 pixels wide by 300 pixels high.
        self.window.geometry("200x300+100+100")
        # The minimum dimensions of the window, as this window is resizable.
        self.window.minsize(width = 110, height = 100)
        # Configuring the window grid layout.
        self.window.grid_rowconfigure(0, weight = 1)
        self.window.grid_columnconfigure(0, weight = 1)
        self.window.grid_columnconfigure(1, weight = 1)
        # Creating the frame which will hold the list and its scroll bar, and be spread over two grid columns.
        self.listFrame = tk.Frame(self.window)
        # The list itself.
        self.listView = tk.Listbox(self.listFrame)
        # Its scroll bar.
        self.scrollBar = tk.Scrollbar(self.listFrame, command = self.listView.yview)
        self.listView.config(yscrollcommand = self.scrollBar.set)
        # Positioning all the elements in the frame.
        self.listView.grid(row = 0, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.scrollBar.grid(row = 0, column = 1, sticky = tk.N+tk.S)
        # Configuring the frame grid layout.
        self.listFrame.grid_columnconfigure(0, weight = 1)
        self.listFrame.grid_rowconfigure(0, weight = 1)
        # Placing the frame itself in the grid layout of the whole window.
        self.listFrame.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W+tk.E+tk.N+tk.S)
        # Creating the buttons at the bottom of the window.
        self.addNewButton = tk.Button(self.window, text = "Add new", command = self.add)
        self.removeButton = tk.Button(self.window, text = "Remove", command = self.remove)
        # Positioning the buttons.
        self.addNewButton.grid(row = 1, column = 0)
        self.removeButton.grid(row = 1, column = 1)

class SubjectEditor(ListEditor):
    def __init__(self, toplevel: tk.Tk, parent) -> None:
        """
        toplevel is the tkinter object of the parent window.
        parent in the MainApp object, unless another dialog opens this window.
        """
        # Run the parent method to create the base window, which will be modified to be tuned to be specifically for modifying subjects.
        self.generateGUI(toplevel, parent)
        # Setting the title of the window.
        self.window.title("Subject List Editor")
        # Creating the "subjectMapping", which is a list which links each index of the list to the SubjectID in the database.
        # This is necessary because when the code checks what has been selected, it finds a list index rather than a subject ID.
        self.subjectMapping = []
        for i in self.parent.inverseSubjectDictionary.keys():
            # For each subject in the database, add it to the end of the list.
            self.listView.insert(tk.END, i)
            # And, add it to the subject mapping.
            self.subjectMapping.append(self.parent.inverseSubjectDictionary[i])
    
    def add(self) -> None:
        """
        This method is called by the 'Add' button.
        It launches a dialog to ask the user for the name of the subject they are addding,
        then it creates it in the database.
        """
        # Open the dialog and ask for the name of the new subject.
        name = tksd.askstring("Add new subject", "Name:", parent = self.window)
        # If the name has not been entered, return (presence check).
        if(not (name and len(name) and len(name.strip()))):
            return
        # Remove whitespace characters from both ends of the string, if they are there.
        name = name.strip()
        # Length check.
        if(len(name) < 2):
            # If the subject name is too short, reject it and show an error message.
            tkmb.showerror("Add subject error", "Name should be longer than 1 character.")
            return
        if(len(name) > 20):
            # If the subject name is too long, reject it and show an error message.
            tkmb.showerror("Add subject error", "Name should be shorter than 20 characters (currently: " + str(len(name)) + ").")
            return
        # Regular expression to check if the name has any invalid characters.
        nameRegex = re.compile('[^a-zA-Z0-9\.\- ]')
        # Run the regular expression on the name of the subject.
        reducedName = nameRegex.sub("", name)
        if(reducedName != name):
            # If running the regular expression changes the name string, it must have invalid characters and so the format check has failed. Show an error message to the user.
            tkmb.showerror("Name error", "Name contains invalid characters, it should only contain english letters, numbers, spaces, dashes, or full stops/periods.", parent = self.window)
            return
        for i in self.parent.subjectDictionary.values():
            # Check if the subject already exists in the database.
            if(i.lower() == name.lower()):
                # If the subject already exists, show an error to the user.
                tkmb.showerror("Add subject error", "Subject already exists in the list.")
                return
        # If all the other checks pass, add the subject to the dictionary.
        self.parent.database.execute("INSERT INTO `Subjects` (SubjectName) VALUES (?);", name)
        # This gets the inserted record's id.
        lastRecord = self.parent.database.execute("SELECT @@IDENTITY;")
        id = lastRecord[0][0]
        # Add the subject to the subject dictionaries.
        self.parent.subjectDictionary[id] = name
        self.parent.inverseSubjectDictionary[name] = id
        # Then add the subject to the end of the list on screen and add it to the mapping.
        self.listView.insert(tk.END, name)
        self.subjectMapping.append(id)
        if(self.parent.state == 2):
            # Reload the quiz browser, if the user has logged in.
            self.parent.unloadQuizBrowserScreen()
            self.parent.loadQuizBrowserScreen()
    
    def remove(self) -> None:
        """
        This runs when the remove button is clicked.
        It removes the subject that is currently selected in the list.
        """
        # Get the current list selection.
        selection = self.listView.curselection()
        if(not selection):
            return
        index = selection[0]
        # If it isn't a valid index (e.g. nothing is selected), return.
        if(not(index and index >= 0 and index < len(self.subjectMapping))):
            return
        # Get the subject ID from the subject-listview list.
        subjectID = self.subjectMapping[index]
        # Unbind all quizzes that are bound to the subject being deleted.
        self.parent.database.execute("UPDATE `Quizzes` SET SubjectID = null WHERE SubjectID = ?;", float(subjectID))
        # Then delete the subject itself.
        self.parent.database.execute("DELETE FROM `Subjects` WHERE SubjectID = ?;", float(subjectID))
        # Remove the subject from the list.
        self.listView.delete(index)
        # Remove the subject from the mapping.
        del self.subjectMapping[index]
        # Remove it from the subject dictionaries.
        subjectName = self.parent.subjectDictionary[subjectID]
        del self.parent.subjectDictionary[subjectID]
        del self.parent.inverseSubjectDictionary[subjectName]
        if(self.parent.state == 2):
            # Reload the quiz browser
            self.parent.unloadQuizBrowserScreen()
            self.parent.loadQuizBrowserScreen()

class ExamBoardEditor(ListEditor):
    def __init__(self, toplevel: tk.Tk, parent) -> None:
        """
        toplevel is the tkinter object of the parent window.
        parent in the MainApp object, unless another dialog opens this window.
        """
        # Run the parent method to create the base window, which will be modified to be tuned to be specifically for modifying subjects.
        self.generateGUI(toplevel, parent)
        # Setting the title of the window.
        self.window.title("Exam Board List Editor")
        # Creating the "examBoardMapping", which is a list which links each index of the list to the ExamBoardID in the database.
        # This is necessary because when the code checks what has been selected, it finds a list index rather than an exam board ID.
        self.examBoardMapping = []
        for i in self.parent.examboardDictionary.values():
            # For every exam board in the database, add it to the on screen list.
            self.listView.insert(tk.END, i)
            # And, add it to the exam board mapping.
            self.examBoardMapping.append(self.parent.inverseExamboardDictionary[i])

    def add(self) -> None:
        """
        This method is called by the 'Add' button.
        It launches a dialog to ask the user for the name of the exam board they are addding,
        then it creates it in the database.
        """
        # Open the dialog and ask for the name of the new exam board.
        name = tksd.askstring("Add new exam board", "Name:", parent = self.window)
        # If the name has not been entered, return (presence check).
        if(not (name and len(name) and len(name.strip()))):
            return
        # Remove whitespace characters from both ends of the string, if they are there.
        name = name.strip()
        # Length check, show an error message if too short or too long.
        if(len(name) < 2):
            tkmb.showerror("Add exam board error", "Name should be longer than 1 character.")
        if(len(name) > 20):
            tkmb.showerror("Add exam board error", "Name should be shorter than 20 characters (currently: " + str(len(name)) + ").")
        # Regular expression to check if the name has any invalid characters.
        nameRegex = re.compile('[^a-zA-Z0-9\.\- ]')
        # Run the regular expression on the name of the subject.
        reducedName = nameRegex.sub("", name)
        if(reducedName != name):
            # If running the regular expression changes the name string, it must have invalid characters and so the format check has failed. Show an error message to the user.
            tkmb.showerror("Name error", "Name contains invalid characters, it should only contain english letters, numbers, spaces, dashes, or full stops/periods.", parent = self.window)
            return
        for i in self.parent.examboardDictionary.values():
            # Check if the exam board already exists in the database.
            if(i.lower() == name.lower()):
                # If the exam board already exists, then show an error message.
                tkmb.showerror("Add exam board error", "Exam board already exists in the list.")
                return
        # If all the other checks pass, add the exam board to the dictionary.
        self.parent.database.execute("INSERT INTO `Examboards` (EName) VALUES (?);", name)
        # This gets the inserted record's id.
        lastRecord = self.parent.database.execute("SELECT @@IDENTITY;")
        id = lastRecord[0][0]
        # Add the exam board to the exam board dictionaries.
        self.parent.examboardDictionary[id] = name
        self.parent.inverseExamboardDictionary[name] = id
        # Then add it to the end of the list and to the exam board mapping.
        self.listView.insert(tk.END, name)
        self.examBoardMapping.append(id)
        if(self.parent.state == 2):
            # Reload the quiz browser
            self.parent.unloadQuizBrowserScreen()
            self.parent.loadQuizBrowserScreen()
    
    def remove(self) -> None:
        """
        This runs when the remove button is clicked.
        It removes the exam board that is currently selected in the list.
        """
        # Get the current list selection.
        selection = self.listView.curselection()
        if(not selection):
            return
        index = selection[0]
        # If it isn't a valid index (e.g. nothing is selected), return.
        if(not(index and index >= 0 and index < len(self.examBoardMapping))):
            return
        # Get the exam board ID from the exam board-listview list.
        examBoardID = self.examBoardMapping[index]
        # Unbind all quizzes that are bound to the exam board being deleted.
        self.parent.database.execute("UPDATE `Quizzes` SET ExamboardID = null WHERE ExamboardID = ?;", float(examBoardID))
        # Then delete the exam board itself.
        self.parent.database.execute("DELETE FROM `Examboards` WHERE ExamboardID = ?;", float(examBoardID))
        # Remove the exam board from the list.
        self.listView.delete(index)
        # Remove the exam board from the mapping.
        del self.examBoardMapping[index]
        # Remove it from the exam board dictionaries.
        examBoardName = self.parent.examboardDictionary[examBoardID]
        del self.parent.examboardDictionary[examBoardID]
        del self.parent.inverseExamboardDictionary[examBoardName]
        if(self.parent.state == 2):
            # Reload the quiz browser
            self.parent.unloadQuizBrowserScreen()
            self.parent.loadQuizBrowserScreen()
