import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.label import Label

from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.behaviors import ButtonBehavior

import sqlite3

class AddTaskLabel(ButtonBehavior, Label):
    pass

class DisplayTasks(Screen):
    pass

class CreateTask(Screen):
    pass

class ListTasks():
    pass

class ToDoApp(App):
    def build(self):
        # create the database if it doesn't exist
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        query = '''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(100) NOT NULL,
                body VARCHAR(1000) NOT NULL,
                date_created VARCHAR(10) NOT NULL
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
