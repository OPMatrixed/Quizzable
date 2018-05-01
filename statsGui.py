"""
This file will handle the statistics window, which is accessed from the top menu and the quiz browser.
This window will switch between statistics view and charts view, both of these are specified on the design document.
"""

# TkInter is used for GUI subroutines and classes.
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmb
# Maths module was used for rounding and power functions.
import math as maths

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
        # Dimensions of the window: 900 pixels wide by 500 pixels high.
        self.window.geometry("920x500")
        # The minimum dimensions of the window, as this window is resizable.
        self.window.minsize(width = 600, height = 400)
        # Setting the title of the window.
        self.window.title("Statistics - Quizzable")
        # The current state of the window. Stats = 0, Charts = 1
        self.currentState = 0
        # Load the main statistics view.
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
        # The subjects and exam boards for the drop-down must be fetched from the application dictionaries.
        self.filterBySubjectComboBox = ttk.Combobox(self.window, state = "readonly", values = ["No filter"] + [i for i in self.parent.subjectDictionary.values()])
        self.filterByExamBoardComboBox = ttk.Combobox(self.window, state = "readonly", values = ["No filter"] + [i for i in self.parent.examboardDictionary.values()])
        # The options for the difficulty drop-down are hard coded because the user can't create their own difficulty levels.
        self.filterByDifficultyComboBox = ttk.Combobox(self.window, state = "readonly", values = ["No filter", "1", "2", "3", "4", "5"])
        # Creating the button that applies the selected filters.
        self.applyFiltersButton = tk.Button(self.window, text = "Apply filters", command = self.applyFilters)
        # Postitioning for the comboboxes and the button.
        self.filterBySubjectComboBox.grid(row = 0, column = 0, sticky = tk.W + tk.E)
        self.filterByExamBoardComboBox.grid(row = 0, column = 1, sticky = tk.W + tk.E)
        self.filterByDifficultyComboBox.grid(row = 0, column = 2, sticky = tk.W + tk.E)
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
        # The scroll bars for the lists
        self.latestResultsScroll = tk.Scrollbar(self.statsFrame, command = self.latestResultsList.yview)
        self.statisticsScroll = tk.Scrollbar(self.statsFrame, command = self.statisticsList.yview)
        self.quizReviewScroll = tk.Scrollbar(self.statsFrame, command = self.quizReviewList.yview)
        # Binding the lists to the scroll bar, in case the user uses the scroll wheel, then the scroll bar must have its position updated.
        self.latestResultsList.config(yscrollcommand = self.latestResultsScroll.set)
        self.statisticsList.config(yscrollcommand = self.statisticsScroll.set)
        self.quizReviewList.config(yscrollcommand = self.quizReviewScroll.set)
        # Buttons for viewing the charts view and redoing quizzes.
        self.viewChartsButton = tk.Button(self.statsFrame, text = "View charts", padx = 30, pady = 3, command = self.unloadMainStats)
        self.redoQuizButton = tk.Button(self.statsFrame, text = "Redo quiz", padx = 30, pady = 3, command = self.redoQuiz)
        
        # Positioning the elements in the frame
        self.latestResultsLabel.grid(row = 0, column = 0, columnspan = 2)
        self.statisticsLabel.grid(row = 0, column = 2, columnspan = 2)
        self.quizReviewLabel.grid(row = 0, column = 4, columnspan = 2)
        # The lists use sticky = , because they must take up as much space as they can within their grid cell.
        self.latestResultsList.grid(row = 1, column = 0, rowspan = 2, sticky = tk.N+tk.S+tk.E+tk.W)
        self.statisticsList.grid(row = 1, column = 2, sticky = tk.N+tk.S+tk.E+tk.W)
        self.quizReviewList.grid(row = 1, column = 4, sticky = tk.N+tk.S+tk.E+tk.W)
        # The scroll bars must take as much vertical space as they can take within their row(s).
        self.latestResultsScroll.grid(row = 1, column = 1, rowspan = 2, sticky = tk.N+tk.S)
        self.statisticsScroll.grid(row = 1, column = 3, sticky = tk.N+tk.S)
        self.quizReviewScroll.grid(row = 1, column = 5, sticky = tk.N+tk.S)
        # The positioning of the view charts and redo quiz buttons.
        self.viewChartsButton.grid(row = 2, column = 2, columnspan = 2)
        self.redoQuizButton.grid(row = 2, column = 4, columnspan = 2)
        
        # End of the frame.
        self.statsFrame.grid(row = 1, column = 0, columnspan = 4, sticky = tk.N+tk.S+tk.E+tk.W)
        
        # Get all the results for the currently selected user, and the recent results.
        self.currentRecentResults = self.parent.database.execute("SELECT TOP 15 * FROM `Results` WHERE `UserID` = ? ORDER BY `DateCompleted` DESC;", float(self.parent.currentUser.id))
        self.currentResults = self.parent.database.execute("SELECT * FROM `Results` WHERE `UserID` = ? ORDER BY `DateCompleted` DESC;", float(self.parent.currentUser.id))
        # Then list the user's latest results.
        self.listLatestResults()
        # And generate statistiscs on the results found above.
        self.generateStatistics()
        # Then list all the quizzes which require re-doing.
        self.listQuizzesToRedo()
    
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
            timeInSeconds = i[6]
            # Format the time taken to complete the quiz.
            timeTakenString = (str(round(timeInSeconds // 60)) + "m " if timeInSeconds >= 60 else "") + (str(round((maths.ceil(timeInSeconds * 10) / 10) % 60, 1)) + "s" if round((maths.ceil(timeInSeconds * 10) / 10) % 60, 1) else "")
            # Add it to the visual list.
            self.latestResultsList.insert(tk.END, str(round(100 * i[3])) + "% - " + timeTakenString + " - " + quizName)
    
    def listQuizzesToRedo(self):
        """This lists the quizzes which have less than a 60% average score over the last three attempts."""
        quizAverages = {}
        self.reviewList = []
        for i in self.currentResults:
            # For each result that has been fetched from the database.
            if(i[2] in quizAverages.keys()):
                if(len(quizAverages[i[2]]) < 3):
                    # Put the last three results in a two dimensional list.
                    quizAverages[i[2]].append(i[3])
            else:
                # If the quiz hasn't been seen by this loop before, create a new list.
                quizAverages[i[2]] = [i[3]]
        for i in quizAverages.keys():
            # For each quiz that has results recorded
            if(sum(quizAverages[i]) / len(quizAverages[i]) < 0.6):
                # If the average over the last three attempts at that quiz is less than 60%
                for j in range(len(self.parent.allQuizzes)):
                    # Find the name of that quiz.
                    if(self.parent.allQuizzes[j][0] == i):
                        quizName = self.parent.allQuizzes[j][1]
                # Then add it to the list of quizzes needing redoing.
                self.quizReviewList.insert(tk.END, quizName + " (Last 3 average: "
                        + str(round(100 * sum(quizAverages[i]) / len(quizAverages[i]))) + "%)")
                # Then add it to the internal list, used by the redo button that launches based on the selected list element's index.
                self.reviewList.append(i)
    
    def generateStatistics(self):
        """This generates statistics on the current set of results."""
        # Remove any previously generated statistics
        self.statisticsList.delete(0, tk.END)
        
        if(not len(self.currentResults)):
            # To prevent division by zero errors, if there isn't any results, don't generate statistics by returning.
            self.statisticsList.insert(tk.END, "No data.")
            return
        
        # Creating total variables, which will be divided to work out averages.
        totalDuration = 0
        totalAverageAnswerTime = 0
        totalScore = 0
        totalSecondsIntoDay = 0
        for i in self.currentRecentResults:
            # For each recent result, add the variables to the totals.
            totalDuration += i[6]
            totalAverageAnswerTime += i[5]
            totalScore += i[3]
            # The fifth column is a datetime, converting it into seconds into the day is straighforward.
            totalSecondsIntoDay += i[4].hour * 3600 + i[4].minute * 60 + i[4].second
        # Add the statistics to the 'list' in the GUI.
        self.statisticsList.insert(tk.END, "Averages for your last " + str(len(self.currentRecentResults)) + " quiz attempts.")
        self.statisticsList.insert(tk.END, "Quiz duration: " + str(round(totalDuration / len(self.currentRecentResults), 1)) + "s")
        self.statisticsList.insert(tk.END, "Time to answer: " + str(round(totalAverageAnswerTime / len(self.currentRecentResults), 1)) + "s")
        # Score is calculated as a percentage.
        self.statisticsList.insert(tk.END, "Score: " + str(round(100 * totalScore / len(self.currentRecentResults))) + "%")
        averageSecondsIntoDay = int(totalSecondsIntoDay / len(self.currentRecentResults))
        # Hours into the day can be worked out by SecondsIntoDay DIV 3600 using integer division.
        # Minutes after that hour of the day can be worked out by SecondsIntoDay DIV 60 (integer division, to work out the minutes into the day),
        # then that result MOD 60 is the number of minutes into the hour it is.
        self.statisticsList.insert(tk.END, "Time of day: " + str(averageSecondsIntoDay // 3600) + ":" + str((averageSecondsIntoDay // 60) % 60))
        self.statisticsList.insert(tk.END, "")
        # Adding all-time statistics for the user.
        # Adding the statistics to the end of the list in the GUI.
        self.statisticsList.insert(tk.END, "All time statistics.")
        self.statisticsList.insert(tk.END, "No. of quiz attempts: " + str(len(self.currentResults)))
        self.statisticsList.insert(tk.END, "")
        # Resetting the variables to be used to calculate all-time averages.
        # Average time isn't calculated for all-time, as it probably won't be any more interesting than the recent average time.
        totalDuration = 0
        totalAverageAnswerTime = 0
        totalScore = 0
        for i in self.currentResults:
            # For each result, add its variables to the totals.
            totalDuration += i[6]
            totalAverageAnswerTime += i[5]
            totalScore += i[3]
        # Then add the all-time averages to the statistics list on the GUI.
        self.statisticsList.insert(tk.END, "All time averages.")
        self.statisticsList.insert(tk.END, "Quiz duration: " + str(round(totalDuration / len(self.currentResults), 1)) + "s")
        self.statisticsList.insert(tk.END, "Answer time: " + str(round(totalAverageAnswerTime / len(self.currentResults), 1)) + "s")
        self.statisticsList.insert(tk.END, "Score: " + str(round(100 * totalScore / len(self.currentResults))) + "%")
    
    def applyFilters(self) -> None:
        """
        This is run upon clicking the "Apply Filters" button.
        This function gets the currently selected filters from the GUI and then will apply those filters to the statistics.
        """
        # Get the text from the filter combo-boxes.
        subjectFilter = self.filterBySubjectComboBox.get()
        examBoardFilter = self.filterByExamBoardComboBox.get()
        difficultyFilter = self.filterByDifficultyComboBox.get()
        # Create lists for generating an SQL statement which filters by the filters which have been set.
        # It can't filter by all three filters all the time, most of the time only one or two of the filters will be set.
        sqlStatementClauses = []
        sqlStatementParameters = [float(self.parent.currentUser.id)]
        if(subjectFilter and subjectFilter != "No filter"):
            # If the subject filter has had a subject selected, find the subject ID
            # and then add it to the SQL statement in the WHERE clause.
            subjectID = self.parent.inverseSubjectDictionary[subjectFilter]
            sqlStatementClauses.append("`SubjectID` = ?")
            sqlStatementParameters.append(float(subjectID))
        if(examBoardFilter and examBoardFilter != "No filter"):
            # If the exam board filter has had an exam board selected, do the same as the subject filter.
            examBoardID = self.parent.inverseExamboardDictionary[examBoardFilter]
            sqlStatementClauses.append("`ExamboardID` = ?")
            sqlStatementParameters.append(float(examBoardID))
        if(difficultyFilter and difficultyFilter != "No filter"):
            # If the difficulty filter has had a difficulty selected, do the same as the other filters.
            difficulty = int(difficultyFilter)
            sqlStatementClauses.append("`Difficulty` = ?")
            sqlStatementParameters.append(float(difficulty))
        if(len(sqlStatementClauses)):
            # If a filter has been selected, generate the SQL statement.
            self.currentResults = self.parent.database.execute("SELECT * FROM `Results` WHERE `UserID` = ? AND `QuizID` IN (SELECT `QuizID` FROM `Quizzes` WHERE " + " AND ".join(sqlStatementClauses) + ") ORDER BY `DateCompleted` DESC;", *sqlStatementParameters)
            self.currentRecentResults = self.parent.database.execute("SELECT TOP 15 * FROM `Results` WHERE `UserID` = ? AND `QuizID` IN (SELECT `QuizID` FROM `Quizzes` WHERE " + " AND ".join(sqlStatementClauses) + ") ORDER BY `DateCompleted` DESC;", *sqlStatementParameters)
        else:
            # If no filter has been selected, run the basic SQL statement.
            self.currentResults = self.parent.database.execute("SELECT * FROM `Results` WHERE `UserID` = ? ORDER BY `DateCompleted` DESC;", float(self.parent.currentUser.id))
            self.currentRecentResults = self.parent.database.execute("SELECT TOP 15 * FROM `Results` WHERE `UserID` = ? ORDER BY `DateCompleted` DESC;", float(self.parent.currentUser.id))
        # Re-generate statistics based on the results from the last query.
        self.generateStatistics()
    
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
        self.renderCharts()
    
    def loadCharts(self) -> None:
        """This will load in the charts screen into this window upon clicking the "View charts" button."""
        # Setting up the grid configuration
        self.window.grid_columnconfigure(0, weight = 1)
        self.window.grid_rowconfigure(0, weight = 1)
        self.window.grid_rowconfigure(1, weight = 1)
        # The large header text.
        self.chartsHeaderText = tk.Label(self.window, text = "Charts view, based off of last applied filters.")
        
        self.canvasWidth = 800
        self.canvasHeight = 400
        # The canvas object, on which the charts will be drawn.
        self.chartCanvas = tk.Canvas(self.window, width = self.canvasWidth, height = self.canvasHeight, bg = "white")
        self.miscStatsLabel = tk.Label(self.window, text = "")
        self.goBackToMainStatsButton = tk.Button(self.window, text = "Return to statistics", command = self.unloadCharts)
        
        # The positioning of the elements.
        self.chartsHeaderText.grid(row = 0, column = 0)
        self.chartCanvas.grid(row = 1, column = 0)
        self.miscStatsLabel.grid(row = 0, column = 1, rowspan = 2)
        self.goBackToMainStatsButton.grid(row = 1, column = 1)
    
    def generateChartData(self) -> list:
        """
        This generates the data used by the charts.
        Returns a list,
        the first element is a list containing the number of results that fall in each percentage band from 0-9% to 90-99% and finally 100%
        The second element is the all-time score average.
        """
        scoreBands = [0] * 11 # Create a list for each of the score bands.
        totalScore = 0
        for i in self.currentResults:
            # For each result, add one to the scoreBands list to the element which corresponds to the result's percentage band.
            scoreBands[maths.floor(i[3] * 10)] += 1
            # Add the score to the total score.
            totalScore += i[3]
        # Then return the scoreBands list and the all-time average score.
        return scoreBands, totalScore / len(self.currentResults)
    
    def linearlyInterpolateColours(colour1: list, colour2: list, ratio: float) -> list:
        """
        This function takes two RGB colours and linearly interpolates the colours depending on the ratio argument.
        A ratio of 0 would return colour1.
        A ratio of 1 would return colour2.
        A ratio of 0.5 would return the average of colour1 and colour2.
        A ratio of 0.2 would return a colour much closer to colour1 than colour2.
        """
        # Find the difference in each of the RGB values of the colours.
        colourDifference = [colour2[i] - colour1[i] for i in range(3)]
        # Linearly interpolate between the colours RGB values depending on the ratio.
        return [round(colourDifference[i] * ratio + colour1[i]) for i in range(3)]
    
    def renderCharts(self) -> None:
        """Draws the shapes required to draw charts on the charts view."""
        # Log to the console that charts are beginning to render.
        print("Rendering charts")
        if(len(self.currentResults) == 0):
            # If there are no results, show a message and cancel method execution.
            self.chartCanvas.create_text(100, 10, text = "No data to generate charts with.")
            return
        # Get the data for the charts.
        scoreBands, averageScore = self.generateChartData()
        # The score band chart.
        barWidth = 30 # The width in pixels of each bar.
        barGap = 10 # The gap size in pixels between each bar.
        # Show the title of the chart.
        self.chartCanvas.create_text(55 + 5.5*(barWidth + barGap), 10, text = "Amount of quizzes completed in given percentage score bands")
        # Work out the band with the highest amount of results, this will be used for working out how to scale the chart.
        topBand = maths.ceil(max(scoreBands)/10) * 10
        # Create the axes.
        self.chartCanvas.create_line(50, 10, 50, self.canvasHeight - 45) # Vertical
        self.chartCanvas.create_line(50, self.canvasHeight - 45, 60 + 11*(barWidth+barGap), self.canvasHeight - 45) # Horizontal
        
        for i in range(11):
            # On the vertical axis, put the scale in terms of number of quizzes.
            self.chartCanvas.create_text(25, 15 + i * (self.canvasHeight - 65)/10, text = str(round((1 - i/10)*topBand)))
        
        for i in range(11):
            # For each percentage band:
            # Work out the height and colour each bar should be. 0-9% gets a strong red and 100% gets a strong green.
            height = scoreBands[i] / topBand
            fillColour = "#%02x%02x%02x" % tuple(StatisticsDialog.linearlyInterpolateColours([220, 20, 60], [0, 238, 118], i/10))
            # Draw the bar, using multiple mathematical expressions to work out the coordinates of the corners of the rectangle.
            self.chartCanvas.create_rectangle(60 + i*(barWidth+barGap), 9 + (1 - height) * (self.canvasHeight - 55), 60 + barWidth + i*(barWidth+barGap), self.canvasHeight - 45, fill = fillColour)
            # Work out what text should be placed below the bar.
            barText = str(10*i) + "-\n" + str(10*(1+i)-1) + "%"
            if(i == 10):
                # If it is the last bar, just set the text to "100%".
                barText = "100%"
            # Place the text beneath the bar.
            self.chartCanvas.create_text(60 + barWidth/2 + i*(barWidth+barGap), self.canvasHeight - 29, text = barText, justify = tk.CENTER)
        
        # The pie chart.
        # Show the chart title.
        self.chartCanvas.create_text(self.canvasWidth - 150, 40, text = "All time questions correct")
        # Work out how many degrees the correct answer (green) arc should encompass, out of the 360 degrees in a circle.
        arcDegrees = 360 * averageScore
        # Convert it to radians to be used in trigonometic functions, for calculating where the text should be placed.
        arcRadians = arcDegrees * maths.pi / 180
        # Draw the red arc (% of wrong answers).
        self.chartCanvas.create_arc((self.canvasWidth - 275, 90, self.canvasWidth - 25, 340), fill = "red", start = 90, extent = 360 - arcDegrees)
        # Draw the green arc (% of correct answers).
        self.chartCanvas.create_arc((self.canvasWidth - 275, 90, self.canvasWidth - 25, 340), fill = "green", start = 450 - arcDegrees, extent = arcDegrees)
        # Put the percentage of correct answers as text in the middle of the green arc.
        self.chartCanvas.create_text(self.canvasWidth - 150 + 75 * maths.cos((arcRadians - maths.pi) / 2), 215 + 75 * maths.sin((arcRadians - maths.pi) / 2), text = "Correct\n" + str(round(averageScore * 100)) + "%", justify = tk.CENTER)
        # Put the percentage of incorrect answers as text in the middle of the red arc.
        self.chartCanvas.create_text(self.canvasWidth - 150 + 75 * maths.cos((maths.pi + arcRadians) / 2), 215 + 75 * maths.sin((maths.pi + arcRadians) / 2), text = "Incorrect\n" + str(round((1 - averageScore) * 100)) + "%", justify = tk.CENTER)
    
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
        # Import the quiz and quizGui files from the application's base directory.
        import quiz, quizGui
        if(not self.quizReviewList.curselection()):
            # If no quiz has been selected, show an error message.
            tkmb.showerror("Redo quiz", "No quiz selected, please select a quiz from the right-most list.", parent = self.window)
            return
        # Get the currently selected list index.
        index = self.quizReviewList.curselection()[0]
        # Find the quiz ID for the selected list index.
        quizID = self.reviewList[index]
        # This loads the quiz from the database, the method .getQuiz() returns a Quiz object.
        quizObj = quiz.Quiz.getQuiz(quizID, self.parent.database)
        # This then launches the window, passing the loaded quiz as an argument.
        quizGui.ActiveQuizDialog(self.parent.tk, self.parent, quizObj, self.parent.currentUser)
