import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.label import Label

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
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

# debugging
from kivy.core.window import Window

DATABASE_NAME = 'tasks.db'
TABLE_NAME = 'tasks'

class AppLabel(Label):
    pass

class TaskDisplay(BoxLayout, Button):
    pass

class DisplayTasks(Screen):
    tasksLayout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # load each of the users tasks
        tasks = self.fetchTasks()

        # set the height according to the number of tasks
        self.tasksLayout.height = len(tasks)*100

        for task in tasks:
            taskDisplay = TaskDisplay()

            # retrieve the title
            title = task[0]
            dueDate = None

            # set the title label
            titleLabel = AppLabel(
                text=title,
                pos_hint={'right': .6, 'y': .3}
            )
            taskDisplay.add_widget(titleLabel)
            
            # retrieve the due date if it exists
            if len(task) == 3:
                dueDate = datetime.fromisoformat(task[2])
                
                # get the remaining time from today
                remainingTime = self.parseDueDate(dueDate)

                dueDateLabel = AppLabel(
                    text=remainingTime
                )
                taskDisplay.add_widget(dueDateLabel)

            self.tasksLayout.add_widget(taskDisplay)

    def fetchTasks(self) -> tuple:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        query = f'''
            SELECT title, body, datetime_due FROM {TABLE_NAME}
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

class CreateTask(Screen):
    timestampDue = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mins = 0
        self.hrs = 0
        self.days = 0

        self.dispDueTimestamp()

    def dispDueTimestamp(self) -> None:
        timestamp = '%02i:%02i:%02i' % (self.days, self.hrs, self.mins)

        self.timestampDue.text = timestamp

    # adding the due time to the total
    def addMins(self, minutes: int) -> None:
        self.mins += minutes
        self.dispDueTimestamp()

    def addHours(self, hours: int) -> None:
        self.hrs += hours
        self.dispDueTimestamp()

    def addDays(self, days: int) -> None:
        self.days += days
        self.dispDueTimestamp()

    def clearDueTimestamp(self) -> None:
        self.days = 0
        self.hrs = 0
        self.mins = 0
        self.dispDueTimestamp()

    def addTask(self, title: str, body: str) -> None:
        # validation
        if len(title) == 0:
            return

        # remove unnecessary leading and trailing whitespaces
        title = title.strip()
        body = title.strip()

        # start a connection
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        if self.days != 0 or self.hrs != 0 or self.mins != 0:
            # fetch the due date
            today = datetime.now()
            dueDate = today.replace(day=today.day + self.days, hour=today.hour + self.hrs, minute=today.minute + self.mins)

            query = f'''
                INSERT INTO {TABLE_NAME}(title, body, datetime_due)
                VALUES(?, ?, ?);
            '''
            cursor.execute(query, (title, body, dueDate))
        else:
            query = f'''
                INSERT INTO {TABLE_NAME}(title, body)
                VALUES(?, ?);
            '''
            cursor.execute(query, (title, body))

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

        # create the screen manager
        taskManager = ScreenManager()
        taskManager.add_widget(DisplayTasks(name='tasks_display'))
        taskManager.add_widget(CreateTask(name='create_task'))

        return taskManager

if __name__ == '__main__':
    ToDoApp().run()
