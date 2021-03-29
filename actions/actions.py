# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk.events import SlotSet

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector
import traceback
import re
Colleges_array = []
class ActionColleges(Action):

    def name(self) -> Text:
        return "action_colleges"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = mysql.connector.connect(host="localhost",port= "3306",user="root",password="",database="chatbot_db")
            mycursor = conn.cursor()
            mycursor.execute("SELECT college_name FROM colleges")
            result = mycursor.fetchall()
            buttonss =[]
            for d in result:
                Colleges_array.append(re.sub("[(',;)]","",str(d)))
                fill_slot = '{"colleges" : "' + re.sub("[(',;)]","",str(d)) + '"}'
                buttonss.append({"title": re.sub("[(',;)]","",str(d)), "payload": f"/choose_college{fill_slot}"})
            dispatcher.utter_message(text="هذه هي الكليات المتوفرة في جامعة بوليتكنك فلسطين: \n اذا كنت ترغب بمعرفة المزيد عن كلية معينة اختر من خلال الازرار التالية.", buttons=buttonss)
            mycursor.close()
            conn.close() 
        except:
            dispatcher.utter_message("Failed")
        return []  


class CollegeMajor(Action):

    def name(self) -> Text:
        return "action_college_major"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = mysql.connector.connect(host="localhost",port= "3306",user="root",password="",database="chatbot_db")
            mycursors = conn.cursor()
            College = tracker.get_slot("colleges")
            index_of_college = Colleges_array.index(College) + 1
            mycursors.execute("""SELECT major_name FROM majors where college_id = %s""", (index_of_college,))
            result = mycursors.fetchall()
            buttonss =[]
            for d in result:
                fill_slot = '{"major" : "' + re.sub("[(',;)]","",str(d)) + '"}'
                buttonss.append({"title": re.sub("[(',;)]","",str(d)), "payload": f"/choose_major{fill_slot}"})
            dispatcher.utter_message(text=f"هذه هي التخصصات المتوفرة في '{College}' في جامعة بوليتكنك فلسطين \n اذا كنت ترغب بمعرفة المزيد عن تخصص معين اختر من خلال الازرار التالية.", buttons=buttonss)
            mycursors.close()
            conn.close() 

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
            dispatcher.utter_message("Failed")
        return [] 