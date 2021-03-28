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


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = mysql.connector.connect(
            host="localhost",
            #port= "3306",
            user="root",
            password="",
            database="chatbot_db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM colleges")
            print("now should be executed")
            for row in cursor:
                dispatcher.utter_message([row.id + " " + row.college_name + "\n"])
                dispatcher.utter_message(text=str(row))
                print(row) 
            cursor.close()
            conn.close() 
        except:
            dispatcher.utter_message(text="Failed!")
        return []