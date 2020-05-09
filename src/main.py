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

import sqlite3

# debugging
from kivy.core.window import Window

DATABASE_NAME = 'tasks.db'
TABLE_NAME = 'tasks'

def createTaskTable(cursor):
    query = f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            body VARCHAR(1000) NOT NULL,
            datetime_due VARCHAR(10)
        );
    '''
    cursor.execute(query)

class AppLabel(Label):
    pass

class TaskBG(Canvas):
    pass

class DisplayTasks(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # load each of the users tasks
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        query = f'''
            SELECT title, body FROM {TABLE_NAME}
        '''
        getTasks = cursor.execute(query)
        tasks = getTasks.fetchall()

        conn.close()

        for task in tasks:
            # retrieve the titles
            title = task[0]
            dueDate = None
            
            # retrieve the due date if it exists
            if len(task) == 3:
                dueDate = task[2]

            # dynamically display each task

class CreateTask(Screen):
    def addTask(self, title, body, dueTimestamp=None):
        # start a connection
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

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
        
        createTaskTable(cursor)

        # create the screen manager
        taskManager = ScreenManager()
        taskManager.add_widget(DisplayTasks(name='tasks_display'))
        taskManager.add_widget(CreateTask(name='create_task'))

        conn.commit()
        conn.close()

        return taskManager

if __name__ == '__main__':
    ToDoApp().run()
