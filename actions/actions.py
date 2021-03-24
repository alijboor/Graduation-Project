# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector
import traceback
import pyodbc 

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            conn= pyodbc.connect('Driver={SQL Server};'
            'Server=MaherSalamin\SQLEXPRESS;'
            'Database=chatbot_db;'
            'Trusted_Connection=yes;')
            dispatcher.utter_message("trying to connect")
            cursor=conn.cursor()
            #msg= '''SELECT * FROM chatbot_db.dbo.Colleges'''
            
            cursor.execute('SELECT * FROM chatbot_db.dbo.Colleges')
            #dispatcher.utter_message(cursor)
            dispatcher.utter_message("query should be done1111")
            for row in cursor:
                #dispatcher.utter_message([row.id + " " + row.college_name + "\n"])
                dispatcher.utter_message(text=str(row))
                print(row)
        except:
            dispatcher.utter_message("Failed")

        return []

    #     return []

    #def submit(self,dispatcher,tracker,domain):
        