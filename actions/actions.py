from typing import Any, Text, Dict, List
from rasa_sdk.events import AllSlotsReset, SlotSet, EventType
#from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction

import mysql.connector
import re

Colleges_array = []
Majors_array = []


class ActionColleges(Action):
    def name(self) -> Text:
        return "action_colleges"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = mysql.connector.connect(host="localhost",
                                           port="3306",
                                           user="root",
                                           password="",
                                           database="chatbot_db")
            mycursor = conn.cursor()
            mycursor.execute("SELECT college_name FROM colleges")
            result = mycursor.fetchall()
            buttonss = []
            for d in result:
                Colleges_array.append(re.sub("[(',;)]", "", str(d)))
                fill_slot = '{"colleges" : "' + re.sub("[(',;)]", "",
                                                       str(d)) + '"}'
                buttonss.append({
                    "title": re.sub("[(',;)]", "", str(d)),
                    "payload": f"/choose_college{fill_slot}"
                })
            dispatcher.utter_message(
                text=
                "هذه هي الكليات المتوفرة في جامعة بوليتكنك فلسطين: \n اذا كنت ترغب بمعرفة المزيد عن كلية معينة اختر من خلال الازرار التالية.",
                buttons=buttonss)
            mycursor.close()
            conn.close()
        except:
            dispatcher.utter_message("Failed to get colleges names")
        return []


class CollegeMajor(Action):
    def name(self) -> Text:
        return "action_college_major"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = mysql.connector.connect(host="localhost",
                                           port="3306",
                                           user="root",
                                           password="",
                                           database="chatbot_db")
            mycursors = conn.cursor()
            College = tracker.get_slot("colleges")
            index_of_college = Colleges_array.index(College) + 1
            mycursors.execute(
                """SELECT major_name FROM majors where college_id = %s""",
                (index_of_college, ))
            result = mycursors.fetchall()
            buttonss = []
            for d in result:
                fill_slot = '{"major" : "' + re.sub("[(',;)]", "",
                                                    str(d)) + '"}'
                buttonss.append({
                    "title": re.sub("[(',;)]", "", str(d)),
                    "payload": f"/choose_major{fill_slot}"
                })
            dispatcher.utter_message(
                text=
                f"هذه هي التخصصات المتوفرة في '{College}' في جامعة بوليتكنك فلسطين \n اذا كنت ترغب بمعرفة المزيد عن تخصص معين اختر من خلال الازرار التالية.",
                buttons=buttonss)
            mycursors.close()
            conn.close()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
            dispatcher.utter_message("Failed")
        return []


class ValidateExpectedMajorForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_expected_major_form"

    def validate_branch_of_tawjihi(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not slot_value:
            return {
                "branch_of_tawjihi": None,
            }
        else:
            return {"branch_of_tawjihi": slot_value}

    def validate_mark_of_branch(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not slot_value:
            return {
                "mark_of_branch": None,
            }
        else:
            return {"mark_of_branch": slot_value}

class ActionSubmitExpectedMajor(Action):
    def name(self) -> Text:
        return "ask_tawjihi_branch_and_mark"
    def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        try:
            conn = mysql.connector.connect(host="localhost",
                                           port="3306",
                                           user="root",
                                           password="",
                                           database="chatbot_db")
            mycursor = conn.cursor()
            branch_tawjihi=tracker.get_slot("branch_of_tawjihi")
            mark_branch=tracker.get_slot("mark_of_branch")

    #     SELECT major_name FROM majors WHERE id = (
    #     SELECT major_id FROM major_branch_tawjihi WHERE branch_tawjihi_id = (
    #     SELECT id FROM tawjihi_branches WHERE name LIKE "علمي"
    # ))
            
            query="""SELECT major_name FROM majors WHERE tawjihi_branch=%s AND min_gpa <=%s   """
            # كويري عشان يحول اسم الفرع لرقم
            query1='SELECT id FROM tawjihi_branches WHERE name LIKE %s'
            # كويري عشان يجيب كل الأي دي للتخصصات يلي بقبلن الفرع اللي حولتو لرقم من الكويري1
            query2 ='SELECT major_id FROM major_branch_tawjihi WHERE branch_tawjihi_id'
            # كويري عشان تجيب أسماء التخصصات عن طريق الأي دي من الكويري2
            # طبعا الاشي يلي بعد الآند بكون جاي من الكويري2 بس مش عارف كيف دجيبو
            query3='SELECT major_name FROM majors WHERE min_gpa <= %s AND major_id = major_branch_tawjihi.major_id'

            #عدل هاي برظو وسوي اللي بدك اياه فيها

            mycursor.execute(query,(branch_tawjihi,mark_branch,))
            result= mycursor.fetchall()
            print(result)
            for major in result:
                Majors_array.append(str(major))
            dispatcher.utter_message(
                text="التخصصات التي يمكنك التسجيل بها حسب معدلك و فرعك التوجيهي هي التخصصات التالية ", array=Majors_array
            )
            mycursor.close()
            conn.close()
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
            dispatcher.utter_message("Failed")
        return[]
