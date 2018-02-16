import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.simpledialog as tksd

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
        self.window.grid_rowconfigure(0, weight = 1)
        self.window.grid_columnconfigure(0, weight = 1)
        self.window.grid_columnconfigure(1, weight = 1)
        self.listFrame = tk.Frame(self.window)
        self.listView = tk.Listbox(self.listFrame)
        self.scrollBar = tk.Scrollbar(self.listFrame, command = self.listView.yview)
        self.listView.config(yscrollcommand = self.scrollBar.set)
        self.listView.grid(row = 0, column = 0, sticky = tk.W+tk.E+tk.N+tk.S)
        self.scrollBar.grid(row = 0, column = 1, sticky = tk.N+tk.S)
        self.listFrame.grid_columnconfigure(0, weight = 1)
        self.listFrame.grid_rowconfigure(0, weight = 1)
        self.listFrame.grid(row = 0, column = 0, columnspan = 2, sticky = tk.W+tk.E+tk.N+tk.S)
        self.addNewButton = tk.Button(self.window, text = "Add new", command = self.add)
        self.removeButton = tk.Button(self.window, text = "Remove", command = self.remove)
        self.addNewButton.grid(row = 1, column = 0)
        self.removeButton.grid(row = 1, column = 1)

class SubjectEditor(ListEditor):
    def __init__(self, toplevel: tk.Tk, parent):
        self.generateGUI(toplevel, parent)
        # Setting the title of the window.
        self.window.title("Subject List Editor")
        self.subjectMapping = []
        for i in self.parent.inverseSubjectDictionary.keys():
            self.listView.insert(tk.END, i)
            self.subjectMapping.append(self.parent.inverseSubjectDictionary[i])
    
    def add(self):
        name = tksd.askstring("Add new subject", "Name:", parent = self.window).strip()
        if(name and len(name)):
            if(len(name) < 2):
                tkmb.showerror("Add subject error", "Name should be longer than 1 character.")
                return
            if(len(name) > 20):
                tkmb.showerror("Add subject error", "Name should be shorter than 20 characters (currently: " + str(len(name)) + ").")
                return
            # TODO: Check against regex, allowed: alphabet, numbers, spaces and hyphens.
            for i in self.parent.subjectDictionary.values():
                if(i.lower() == name.lower()):
                    tkmb.showerror("Add subject error", "Subject already exists in the list.")
                    return
            self.parent.database.execute("INSERT INTO `Subjects` (SubjectName) VALUES (?);", name)
            # This gets the inserted record's id.
            lastRecord = self.parent.database.execute("SELECT @@IDENTITY;")
            id = lastRecord[0][0]
            
            self.parent.subjectDictionary[id] = name
            self.parent.inverseSubjectDictionary[name] = id
            
            self.listView.insert(tk.END, name)
            self.subjectMapping.append(id)
    
    def remove(self):
        index = self.listView.curselection()
        if(index and index >= 0 and index < len(self.subjectMapping)):
            subjectID = self.subjectMapping[index]

class ExamBoardEditor(ListEditor):
    def __init__(self, toplevel: tk.Tk, parent):
        self.generateGUI(toplevel, parent)
        # Setting the title of the window.
        self.window.title("Exam Board List Editor")
        self.examBoardMapping = []
        for i in self.parent.examboardDictionary.values():
            self.listView.insert(tk.END, i)
            self.examBoardMapping.append(self.parent.inverseExamboardDictionary[i])

    def add(self):
        name = tksd.askstring("Add new exam board", "Name:", parent = self.window).strip()
        if(name and len(name)):
            if(len(name) < 2):
                tkmb.showerror("Add exam board error", "Name should be longer than 1 character.")
            if(len(name) > 20):
                tkmb.showerror("Add exam board error", "Name should be shorter than 20 characters (currently: " + str(len(name)) + ").")
            # TODO: Check against regex, allowed: alphabet, numbers, spaces and hyphens.
            for i in self.parent.examboardDictionary.values():
                if(i.lower() == name.lower()):
                    tkmb.showerror("Add exam board error", "Exam board already exists in the list.")
                    return
            self.parent.database.execute("INSERT INTO `Examboards` (EName) VALUES (?);", name)
            # This gets the inserted record's id.
            lastRecord = self.parent.database.execute("SELECT @@IDENTITY;")
            id = lastRecord[0][0]
            
            self.parent.examboardDictionary[id] = name
            self.parent.inverseExamboardDictionary[name] = id
            
            self.listView.insert(tk.END, name)
            self.examBoardMapping.append(id)
    
    def remove(self):
        pass
