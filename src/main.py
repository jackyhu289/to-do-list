import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.label import Label

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button

from kivy.graphics.instructions import Canvas
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.properties import ObjectProperty

import sqlite3
import math
from datetime import datetime
from datetime import timedelta

# debugging
from kivy.core.window import Window
import pdb

DATABASE_NAME = 'tasks.db'
TABLE_NAME = 'tasks'

class BtnBehaviorLabel(ButtonBehavior, Label):
    pass

class AppLabel(Label):
    pass

class TaskDisplay(ButtonBehavior, BoxLayout):
    # edit task options on click
    def on_release(self):
        print(self)

class ManageTasks(ScreenManager):
    tasksList = ObjectProperty(None)
    datetimeDueLabel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timeLeft = None
        
        self.displayTasks()

    # Display task functionality
    def displayTasks(self) -> None:
        # load each of the users tasks
        tasks = self.fetchTasks()

        # set the window height according to the number of tasks
        self.tasksList.height = len(tasks)*100

        for task in tasks:
            taskId = task[0]
            title = task[1]
            body = task[2]

            # retrieve the due date if it exists (not NULL)
            if task[3] != None:
                dueDate = datetime.fromisoformat(task[3])
                
                self.displayTask(taskId, title, body, dueDate)
            else:
                self.displayTask(taskId, title, body)

    def displayTask(self, taskId: int, title: str, body: str, dueDate: datetime=None) -> None:
        taskDisplay = TaskDisplay()
        dispTaskAndDelOpt = BoxLayout(orientation='horizontal')

        titleLabel = AppLabel(
            text=title
        )
        dispTaskAndDelOpt.add_widget(titleLabel)

        deleteTaskIcon = BtnBehaviorLabel(
            text='×',
            font_size=36,
            size_hint_x=.2,
            color=(1, 0, 0, 1)
        )
        deleteTaskIcon.on_release = lambda: self.deleteTask(taskId)

        dispTaskAndDelOpt.add_widget(deleteTaskIcon)
        taskDisplay.add_widget(dispTaskAndDelOpt)

        # set the due date if there is an assigned due date
        if dueDate != None:
            # get the remaining time from today
            remainingTime = self.parseDueDate(dueDate)

            dueDateLabel = AppLabel(
                text=remainingTime
            )
            taskDisplay.add_widget(dueDateLabel)

        self.tasksList.add_widget(taskDisplay)

    def fetchTasks(self) -> tuple:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        query = f'''
            SELECT id, title, body, datetime_due FROM {TABLE_NAME}
        '''
        getTasks = cursor.execute(query)
        tasks = getTasks.fetchall()

        conn.close()

        return tasks

    # parses the date, returning it in the form of '7 days/minutes/... left
    def parseDueDate(self, dueDate) -> str:
        secondsLeft = (dueDate - datetime.now()).total_seconds()

        # time durations in seconds
        day = 86400
        hour = 3600
        minute = 60

        # return the time duration count depending on the highest time duration
        if secondsLeft >= day:
            return '%s days left' % math.floor(secondsLeft / day)
        if secondsLeft >= hour:
            return '%s hours left' % math.floor(secondsLeft / hour) 
        if secondsLeft >= minute:
            return '%s minutes left' % math.floor(secondsLeft / minute)
        return '%s seconds left' % math.floor(secondsLeft)

    # Create task functionality
    # Manage due date
    def dispDueDate(self):
        daysLeft = self.timeLeft['days']
        hoursLeft = self.timeLeft['hours']
        minutesLeft = self.timeLeft['minutes']

        self.datetimeDueLabel.text = '%02i:%02i:%02i' % (daysLeft, hoursLeft, minutesLeft)

    def increaseDueDatetime(self, days: int=None, hours: int=None, minutes: int=None) -> None:
        timeLeft = {
            'days': 0,
            'hours': 0,
            'minutes': 0
        }

        if self.timeLeft != None:
            timeLeft = self.timeLeft

        if days:
            timeLeft['days'] += days
        if hours:
            timeLeft['hours'] += hours
        if minutes:
            timeLeft['minutes'] += minutes

        # convert the time durations to the appropriate times. For example, 60 minutes = +1 hour
        if timeLeft['minutes'] >= 60:
            timeLeft['hours'] += timeLeft['minutes']//60
            timeLeft['minutes'] = timeLeft['minutes'] % 60
        if timeLeft['hours'] >= 24:
            timeLeft['days'] += timeLeft['hours']//24
            timeLeft['hours'] = timeLeft['hours'] % 24

        self.timeLeft = timeLeft
        self.dispDueDate()

    def resetDueDatetime(self) -> None:
        self.timeLeft = {
            'days': 0,
            'hours': 0,
            'minutes': 0
        }
        self.dispDueDate()

    def addTask(self, title: str, body: str) -> None:
        # verify the title length is greater than 0
        if len(title) == 0:
            return

        # remove unnecessary trailing and preceding whitespace
        title = title.strip()
        body = body.strip()

        # store the data into sql database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # insert due date if it exists
        if self.timeLeft['days'] != 0 or self.timeLeft['hours'] != 0 or self.timeLeft['minutes'] != 0:
            dueDatetime = datetime.now() + timedelta(
                days=self.timeLeft['days'],
                hours=self.timeLeft['hours'],
                minutes=self.timeLeft['minutes']
            )

            query = f'''
                INSERT INTO {TABLE_NAME}(title, body, datetime_due)
                VALUES(?, ?, ?)
            '''
            cursor.execute(query, (title, body, dueDatetime))
        else:
            query = f'''
                INSERT INTO {TABLE_NAME}(title, body)
                VALUES(?, ?)
            '''
            cursor.execute(query, (title, body))

        conn.commit()
        conn.close()

    # Delete task functionality
    def deleteTask(self, taskId: int) -> None:
        # remove the task from the database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        query = f'''
            DELETE FROM {TABLE_NAME}
            WHERE id = {taskId}
        '''
        cursor.execute(query)

        conn.commit()
        conn.close()

class ToDoApp(App):
    def build(self):
        Window.size = (500, 600)

        # create the database if it doesn't exist
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        query = f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(100) NOT NULL,
                body VARCHAR(1000) NOT NULL,
                datetime_due VARCHAR(100)
            );
        '''
        cursor.execute(query)

        conn.commit()
        conn.close()

        return ManageTasks()

if __name__ == '__main__':
    ToDoApp().run()
