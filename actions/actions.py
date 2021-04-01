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
            
            query="""SELECT major_name FROM majors JOIN tawjihibranch ON tawjihibranch.major_id = majors.id AND tawjihibranch.branch = %s OR tawjihibranch.branch = 'جميع الفروع' WHERE min_gpa <=%s   """
            mycursor.execute(query,(branch_tawjihi,mark_branch,))
            result= mycursor.fetchall()
            for major in result:
                fill_slot = '{"major" : "' + re.sub("[(',;)]", "",str(major)) + '"}'
                Majors_array.append({
                    "title": re.sub("[(',;)]", "", str(major)),
                    "payload": f"/choose_major{fill_slot}"
                })
                # Majors_array.append(str(major))
            dispatcher.utter_message(
                text="التخصصات التي يمكنك التسجيل بها حسب معدلك و فرعك التوجيهي هي التخصصات التالية ", buttons=Majors_array)
            mycursor.close()
            conn.close()
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
            dispatcher.utter_message("Failed")
        return[]

class MajorDeatil(Action):
    def name(self) -> Text:
        return "action_major_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = mysql.connector.connect(host="localhost",
                                           port="3306",
                                           user="root",
                                           password="",
                                           database="chatbot_db")
            mycursors = conn.cursor()
            major_need = tracker.get_slot("major")
            mycursors.execute("""SELECT * FROM majors where major_name = %s""",(major_need, ))
            result = mycursors.fetchall()
            final_result = " "

            # for d in result:
            #     fill_slot = '{"major" : "' + re.sub("[(',;)]", "",
            #                                         str(d)) + '"}'
            #     buttonss.append({
            #         "title": re.sub("[(',;)]", "", str(d)),
            #         "payload": f"/choose_major{fill_slot}"
            #     })text=f"{final_result}"
            dispatcher.utter_message(json_message = result)
            mycursors.close()
            conn.close()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
            dispatcher.utter_message("Failed")
        return []
