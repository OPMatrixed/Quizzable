# This file will handle the statistics window, which is accessed from the top menu and the quiz browser.
# This window will switch between statistics view and charts view, both of these are specified on the design document.

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont

class StatisticsDialog(object):
    def __init__(self, toplevel: tk.Tk, parent) -> None:
        """
        toplevel is the tkinter object of the parent window.
        parent in the MainApp object, unless another dialog opens this window.
        """
        self.parent = parent
        self.toplevel = toplevel
        # This creates the window. padx and pady here add 5 pixels padding horizontally and vertically respectively
        # This is to stop the widgets on the window from touching the edges of the window, which doesn't look that good.
        self.window = tk.Toplevel(toplevel, padx = 5, pady = 5)
        # Dimensions of the window: 500 pixels wide by 300 pixels high.
        self.window.geometry("800x400")
        # The minimum dimensions of the window, as this window is resizable.
        self.window.minsize(width = 600, height = 400)
        # Setting the title of the window.
        self.window.title("Statistics - Quizzable")
        # The current state of the window. Stats = 0, Charts = 1
        self.currentState = 0
        self.loadMainStats()
    
    def loadMainStats(self) -> None:
        """Configuring the grid configuration of the window, in which the elements/widgets on the window will fit into."""
        # There are 4 columns and 2 rows.
        self.window.grid_columnconfigure(0, weight = 2)
        self.window.grid_columnconfigure(1, weight = 2)
        self.window.grid_columnconfigure(2, weight = 2)
        self.window.grid_columnconfigure(3, weight = 1)
        self.window.grid_rowconfigure(0, weight = 0)
        self.window.grid_rowconfigure(1, weight = 1)
        
        # The filter comboboxes and apply button that fit on the first row.
        self.filterBySubjectComboBox = ttk.Combobox(self.window, values = ["No filter"])
        self.filterByExamBoardComboBox = ttk.Combobox(self.window, values = ["No filter"])
        self.filterByDifficultyComboBox = ttk.Combobox(self.window, values = ["No filter"])
        self.applyFiltersButton = tk.Button(self.window, text = "Apply filters", command = self.applyFilters)
        # Postitioning for the comboboxes and the button.
        self.filterBySubjectComboBox.grid(row = 0, column = 0, sticky = tk.W+tk.E)
        self.filterByExamBoardComboBox.grid(row = 0, column = 1, sticky = tk.W+tk.E)
        self.filterByDifficultyComboBox.grid(row = 0, column = 2, sticky = tk.W+tk.E)
        self.applyFiltersButton.grid(row = 0, column = 3)
        
        # For the rest of the window, I have decided to put it all in a six-column, three-row frame,
        # and this will be spread over all four columns and sit on the bottom row of the window it is sitting on.
        self.statsFrame = tk.Frame(self.window)
        
        # The grid configuration of the statistics frame. There will be 3 rows, and the first list will span over the bottom two rows. Labels on the first row.
        # There will be 6 columns, but only the ones that contain lists should expand when the window is resizes, so the scrollbar columns won't be weighted.
        self.statsFrame.grid_columnconfigure(0, weight = 1)
        self.statsFrame.grid_columnconfigure(2, weight = 1)
        self.statsFrame.grid_columnconfigure(4, weight = 1)
        self.statsFrame.grid_rowconfigure(1, weight = 1)
        self.statsFrame.grid_rowconfigure(2, minsize = 30) # Button row isn't weighted.
        
        # The labels above the columns in the statistics frame.
        self.latestResultsLabel = tk.Label(self.statsFrame, text = "Latest Results")
        self.statisticsLabel = tk.Label(self.statsFrame, text = "Statistics")
        self.quizReviewLabel = tk.Label(self.statsFrame, text = "Quizzes in need of review")
        # The lists themselves
        self.latestResultsList = tk.Listbox(self.statsFrame)
        self.statisticsList = tk.Listbox(self.statsFrame)
        self.quizReviewList = tk.Listbox(self.statsFrame)
        # Scroll bars
        self.latestResultsScroll = tk.Scrollbar(self.statsFrame, command = self.latestResultsList.yview)
        self.statisticsScroll = tk.Scrollbar(self.statsFrame, command = self.statisticsList.yview)
        self.quizReviewScroll = tk.Scrollbar(self.statsFrame, command = self.quizReviewList.yview)
        
        self.latestResultsList.config(yscrollcommand = self.latestResultsScroll.set)
        self.statisticsList.config(yscrollcommand = self.statisticsScroll.set)
        self.quizReviewList.config(yscrollcommand = self.quizReviewScroll.set)
        # Buttons
        self.viewChartsButton = tk.Button(self.statsFrame, text = "View charts", padx = 30, pady = 3, command = self.unloadMainStats)
        self.redoQuizButton = tk.Button(self.statsFrame, text = "Redo quiz", padx = 30, pady = 3)
        
        # Positioning the elements in the frame
        self.latestResultsLabel.grid(row = 0, column = 0, columnspan = 2)
        self.statisticsLabel.grid(row = 0, column = 2, columnspan = 2)
        self.quizReviewLabel.grid(row = 0, column = 4, columnspan = 2)
        self.latestResultsList.grid(row = 1, column = 0, rowspan = 2, sticky = tk.N+tk.S+tk.E+tk.W)
        self.statisticsList.grid(row = 1, column = 2, sticky = tk.N+tk.S+tk.E+tk.W)
        self.quizReviewList.grid(row = 1, column = 4, sticky = tk.N+tk.S+tk.E+tk.W)
        self.latestResultsScroll.grid(row = 1, column = 1, rowspan = 2, sticky = tk.N+tk.S)
        self.statisticsScroll.grid(row = 1, column = 3, sticky = tk.N+tk.S)
        self.quizReviewScroll.grid(row = 1, column = 5, sticky = tk.N+tk.S)
        self.viewChartsButton.grid(row = 2, column = 2, columnspan = 2)
        self.redoQuizButton.grid(row = 2, column = 4, columnspan = 2)
        
        # End of the frame.
        self.statsFrame.grid(row = 1, column = 0, columnspan = 4, sticky = tk.N+tk.S+tk.E+tk.W)
        
        self.listLatestResults()
        self.generateStatistics()
    
    def listLatestResults(self):
        """
        This gets the latest results from the database for the user and lists them on the window.
        Gets a maximum of fourty results.
        """
        # Fetch the user's last 40 results.
        resultRows = self.parent.database.execute("SELECT TOP 40 * FROM `Results` WHERE `UserID` = ? ORDER BY `DateCompleted` DESC;", float(self.parent.currentUser.id))
        for i in resultRows:
            # For each result, find the quiz name and then add it to the list.
            quizName = "Unknown quiz"
            # For loop that goes through all the quizzes to find the title of each quiz.
            for j in range(len(self.parent.allQuizzes)):
                if(self.parent.allQuizzes[j][0] == i[2]):
                    quizName = self.parent.allQuizzes[j][1]
            # Add the score, time taken and name to the latest results list box.
            self.latestResultsList.insert(tk.END, str(round(100 * i[3])) + "% - " + str(round(i[6], 1)) + "s - " + quizName)
    
    def generateStatistics(self):
        """This generates statistics on the current set of results."""
        recentResultRows = self.parent.database.execute("SELECT TOP 15 * FROM `Results` WHERE `UserID` = ? ORDER BY `DateCompleted` DESC;", float(self.parent.currentUser.id))
        allResultRows = self.parent.database.execute("SELECT * FROM `Results` WHERE `UserID` = ?;", float(self.parent.currentUser.id))
        
        if(not len(allResultRows)):
            self.statisticsList.insert(tk.END, "No data.")
            return
        
        totalDuration = 0
        totalAverageAnswerTime = 0
        totalScore = 0
        totalSecondsIntoDay = 0
        for i in recentResultRows:
            totalDuration += i[6]
            totalAverageAnswerTime += i[5]
            totalScore += i[3]
            totalSecondsIntoDay += i[4].hour * 3600 + i[4].minute * 60 + i[4].second
        
        self.statisticsList.insert(tk.END, "Averages for your last " + str(len(recentResultRows)) + " quiz attempts.")
        self.statisticsList.insert(tk.END, "Quiz duration: " + str(round(totalDuration / len(recentResultRows), 1)) + "s")
        self.statisticsList.insert(tk.END, "Time to answer: " + str(round(totalAverageAnswerTime / len(recentResultRows), 1)) + "s")
        self.statisticsList.insert(tk.END, "Score: " + str(round(100 * totalScore / len(recentResultRows))) + "%")
        averageSecondsIntoDay = int(totalSecondsIntoDay / len(recentResultRows))
        self.statisticsList.insert(tk.END, "Time of day: " + str(averageSecondsIntoDay // 3600) + ":" + str((averageSecondsIntoDay // 60) % 60))
        self.statisticsList.insert(tk.END, "")
        
        uniqueQuizzesAttempted = self.parent.database.execute("SELECT Count(*) AS `DistinctQuizzes` FROM (SELECT DISTINCT `QuizID` FROM `Results` WHERE `UserID` = ?);", float(self.parent.currentUser.id))[0][0];
        
        self.statisticsList.insert(tk.END, "All time statistics.")
        self.statisticsList.insert(tk.END, "No. of quiz attempts: " + str(len(allResultRows)))
        self.statisticsList.insert(tk.END, "No. of unique quizzes attempted: " + str(uniqueQuizzesAttempted))
        self.statisticsList.insert(tk.END, "")
        totalDuration = 0
        totalAverageAnswerTime = 0
        totalScore = 0
        for i in allResultRows:
            totalDuration += i[6]
            totalAverageAnswerTime += i[5]
            totalScore += i[3]
        
        self.statisticsList.insert(tk.END, "All time averages.")
        self.statisticsList.insert(tk.END, "Quiz duration: " + str(round(totalDuration / len(allResultRows), 1)) + "s")
        self.statisticsList.insert(tk.END, "Answer time: " + str(round(totalAverageAnswerTime / len(allResultRows), 1)) + "s")
        self.statisticsList.insert(tk.END, "Score: " + str(round(100 * totalScore / len(allResultRows))) + "%")
    
    def applyFilters(self) -> None:
        """
        This is run upon clicking the "Apply Filters" button.
        This function gets the currently selected filters from the gui and then will apply those filters to the statistics.
        """
        pass
    
    def unloadMainStats(self) -> None:
        """This unloads all the main statistics view, ready to replace it with the charts in the same window shell."""
        # Destroying the elements.
        self.filterBySubjectComboBox.destroy()
        self.filterByExamBoardComboBox.destroy()
        self.filterByDifficultyComboBox.destroy()
        self.applyFiltersButton.destroy()
        self.latestResultsLabel.destroy()
        self.statisticsLabel.destroy()
        self.quizReviewLabel.destroy()
        self.latestResultsList.destroy()
        self.statisticsList.destroy()
        self.quizReviewList.destroy()
        self.latestResultsScroll.destroy()
        self.statisticsScroll.destroy()
        self.quizReviewScroll.destroy()
        self.viewChartsButton.destroy()
        self.redoQuizButton.destroy()
        self.statsFrame.destroy()
        
        # Resetting the grid configuration.
        self.window.grid_columnconfigure(0, weight = 0)
        self.window.grid_columnconfigure(1, weight = 0)
        self.window.grid_columnconfigure(2, weight = 0)
        self.window.grid_columnconfigure(3, weight = 0)
        self.window.grid_rowconfigure(0, weight = 0)
        self.window.grid_rowconfigure(1, weight = 0)
        
        # Load the charts screen.
        self.loadCharts()
    
    def loadCharts(self) -> None:
        """This will load in the charts screen into this window upon clicking the "View charts" button."""
        # Setting up the grid configuration
        self.window.grid_columnconfigure(0, weight = 1)
        self.window.grid_rowconfigure(0, weight = 1)
        # The large header text.
        self.chartsHeaderText = tk.Label(self.window, text = "Charts view")
        
        # The canvas object, on which the charts will be drawn.
        self.chartCanvas = tk.Canvas(self.window)
        self.miscStatsLabel = tk.Label(self.window, text = "")
        self.goBackToMainStatsButton = tk.Button(self.window, text = "Return to statistics", command = self.unloadCharts)
        
        # The positioning of the elements.
        self.chartsHeaderText.grid(row = 0, column = 0)
        self.chartCanvas.grid(row = 1, column = 0)
        self.miscStatsLabel.grid(row = 0, column = 1, rowspan = 2)
        self.goBackToMainStatsButton.grid(row = 1, column = 1)
    
    def unloadCharts(self) -> None:
        """This unloads the charts and goes back to the main statistics view."""
        # Destroying the elements
        self.chartsHeaderText.destroy()
        self.chartCanvas.destroy()
        self.miscStatsLabel.destroy()
        self.goBackToMainStatsButton.destroy()
        
        # Resetting the grid configuration.
        self.window.grid_columnconfigure(0, weight = 0)
        self.window.grid_columnconfigure(1, weight = 0)
        self.window.grid_columnconfigure(2, weight = 0)
        self.window.grid_columnconfigure(3, weight = 0)
        self.window.grid_rowconfigure(0, weight = 0)
        self.window.grid_rowconfigure(1, weight = 0)
        
        # Load the statistics screen
        self.loadMainStats()
    
    def redoQuiz(self) -> None:
        """
        This is called when the user clicks the "Redo Quiz" button.
        It will open the quiz window with the currently selected quiz on this window.
        """
        pass
    
    def renderCharts(self) -> None:
        pass
