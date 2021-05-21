from typing import Any, Text, Dict, List
from rasa_sdk.events import AllSlotsReset, SlotSet, EventType, UserUtteranceReverted, SessionStarted, ActionExecuted
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction


import mysql.connector
import re

Colleges_array = []
Majors_array = []

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SessionStarted(), ActionExecuted("action_welcome")]

        
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
            buttons = []
            for d in result:
                Colleges_array.append(re.sub("[(',;)]", "", str(d)))
                fill_slot = '{"colleges" : "' + re.sub("[(',;)]", "",
                                                       str(d)) + '"}'
                buttons.append({
                    "title": re.sub("[(',;)]", "", str(d)),
                    "payload": f"/choose_college{fill_slot}"
                })
            dispatcher.utter_message(
                text=
                "هذه هي الكليات المتوفرة في جامعة بوليتكنك فلسطين: \n اذا كنت ترغب بمعرفة المزيد عن كلية معينة اختر من خلال الازرار التالية.",
                buttons=buttons)
            mycursor.close()
            conn.close()
        except:
            dispatcher.utter_message(text="حدث خطأ أثناء احضار الكليات, يرجى زيارة الرابط التالي: https://ppu.edu/p/ar/Colleges-Deanships")
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
            dispatcher.utter_message(text="حدث خطأ أثناء احضار الكليات, يرجى زيارة الرابط التالي: https://ppu.edu/p/ar/Colleges-Deanships")
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
        slot_value = tracker.get_slot("branch_of_tawjihi")
        if not slot_value:
            dispatcher.utter_message(text="أدخل فرعك في الثانوية العامة ")
            return {"branch_of_tawjihi": None,}
        else:
            return {"branch_of_tawjihi": slot_value}

    def validate_mark_of_branch(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_value = float(tracker.get_slot("mark_of_branch"))
        if slot_value < 50 :
            dispatcher.utter_message(text=" أعد إدخال معدلك بشكل صحيح رجاءً")
            return {"mark_of_branch": None}
        elif slot_value > 100 :
            dispatcher.utter_message(text=" أعد إدخال معدلك بشكل صحيح رجاءً")
            return {"mark_of_branch": None}
        else:
            return {"mark_of_branch": slot_value}

    def validate_program(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_value = tracker.get_slot("program")
        if not slot_value:
            return {
                "program": None,
            }
        else:
            return {"program": slot_value}

class ActionSubmitExpectedMajor(Action):
    def name(self) -> Text:
        return "action_tawjihi_branch_and_mark"
    
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
            prog=tracker.get_slot("program")
            
            query="""SELECT major_name FROM majors JOIN tawjihibranch ON tawjihibranch.major_id = majors.id AND (tawjihibranch.branch = %s OR tawjihibranch.branch = 'جميع الفروع' ) WHERE min_gpa <=%s  AND program = %s """
            mycursor.execute(query,(branch_tawjihi,mark_branch,prog,))
            result= mycursor.fetchall()
            if result:
                for major in result:
                    fill_slot = '{"major" : "' + re.sub("[(',;)]", "",str(major)) + '"}'
                    Majors_array.append({
                        "title": re.sub("[(',;)]", "", str(major)),
                        "payload": f"/choose_major{fill_slot}"
                    })
                dispatcher.utter_message(text=" التخصصات التي يمكنك التسجيل بها حسب معدلك و فرعك التوجيهي هي التخصصات التالية:\n ملاحظة: حصول الطالب على الحد الأدنى المطلوب لمعدل الثانوية لا يني بالضرورة القبول في التخصص المطلوب و إنما يهضع الطالب للتنافس مع الطلبة الراغبين في الالتحاق بأي تخصص ", buttons=Majors_array)
            else:
                dispatcher.utter_message(text=f"نأسف لعدم استيفائك شروط القبول لاي من التخصصات التابعة لبرنامج {prog} ")

            mycursor.close()
            conn.close()
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
            dispatcher.utter_message(text="متأسف لقد حدث خطأ أثناء احضار التخصصات , في للوقت الحالي يمكنك زيارة الرابط التالي لمعرفة المزيد: https://dar.ppu.edu/ar/programs")
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
            major_selected = tracker.get_slot("major")
            mycursors.execute("""SELECT * FROM majors where major_name = %s""",(major_selected, ))
            result = list(mycursors.fetchall())
            dispatcher.utter_message(text = f"تخصص {result[0][2]} : يبلغ سعر الساعة لهذا التخصص {result[0][3]} ديناراً و بإجمالي {result[0][4]} ساعة  موزعة على  {result[0][5]} سنوات, و يبلغ الحد الادنى لمعدلات القبول لهذا التخصص {result[0][6]} , بالإضافة إلى أن قيمة القسط للفصل الأول تبلغ {result[0][8]} للطلبة الذين استوفوا شروط التسجيل, أما بالنسبة للنظام الموازي فقيمة القسط تبلغ القسط الأصلي مضروبا ب2 ")
            mycursors.close()
            conn.close()
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
            dispatcher.utter_message(text="حدث خطأ في عملية تجهيز معلومات التخصص المطلوب, أرجو زيارة الرابط التالي: https://dar.ppu.edu/ar/programs")
        return []