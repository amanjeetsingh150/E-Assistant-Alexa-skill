from __future__ import print_function
from firebase import firebase
import json
import copy
import datetime
import pytz
from datetime import datetime
	
firebase=firebase.FirebaseApplication('https://calci-b1a59.firebaseio.com',None)
first_student=""
students_list=[]
final_list=[]
flag=0
index=0
days=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

def build_speechlet_response(title,output,reprompt_text,should_end_session):
        return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
        }

def build_response(session_attributes, speechlet_response):
        return {
                'version':'1.0',
                'sessionAttributes':session_attributes,
                'response':speechlet_response
                }

def get_help(intent,session):
        card_title="Help"
        speech_output="You can ask me to take attendance of your class."
        should_end_session=False
        return build_response({}, build_speechlet_response(
               card_title, speech_output, speech_output, should_end_session))
                        
def continue_attendance(intent,session):
        card_title="Continue Attendance"
        session_attributes={}
        should_end_session=False
        speech_output=""
        speech=""
        value=str(intent['slots']['presence']['value'])
        print(value)
        if value == "present":
            print('push present to firebase')
            print("Flag: "+str(flag))
            if flag==1:
                result=firebase.patch('/students/0',{'name': first_student, 'state': 'present'})
                speech="Marked present."
            else:
                global index
                result=firebase.patch('/students/'+str(index),{'name': first_student, 'state': 'present'})
                print("Hey")
                print(index)
                speech="Marked present."
        elif value == "absent":
            print('push Absent to firebase')
            print("Flag:"+str(flag))
            if flag==1:
                result=firebase.patch('/students/0',{'name': first_student, 'state': 'absent'})
                speech="Marked absent."
            else:
                global index
                result=firebase.patch('/students/'+str(index),{'name': first_student, 'state': 'absent'})
                print("Hey")
                print(index)
                speech="Marked absent."
        print(len(students_list))
        if len(students_list)==1:
            should_end_session=True
            session_attributes={}
            speech_output="Attendance Done."
        else:
            students_list.pop(0)
            print(students_list[0])
            speech_output=speech+" "+students_list[0]['name']
            global first_student
            first_student=students_list[0]['name']
            global final_list
            print("Hello Two")
            print(final_list)
            index=final_list.index(students_list[0])
            print("Index defined")
            print(index)
            global flag
            flag=0
            
        return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, speech_output,should_end_session))

def handle_session_end_request():
        card_title = "Thank you for ptaking attendance."
        speech_output = "Thank you for taking attendance."
        should_end_session = True
        return build_response({}, build_speechlet_response(  
                card_title, speech_output, None, should_end_session))

def schedule_teacher(intent,session):
        card_title="Schedule"
        session_attributes={}
        should_end_session=False
        speech_output=""
        print(intent['slots'])
        print('value' in intent['slots']['days'])
        if('value' in intent['slots']['days']):
            value=str(intent['slots']['days']['value'])
            schedule_result=firebase.get('/schedule',None)
            value=value.lower()
            if(value in schedule_result):
                teacher_classes=schedule_result[value]
                print(len(teacher_classes))
                speech_output="You have "+str(len(teacher_classes))+" classes on "+value+". "
                for x in teacher_classes:
                    speech_output+=x['subject']+' with '+x['klass']+' from '+x['time']+'.'+' '
                should_end_session=True    
            else:
                speech_output="You do not have any class on this day."
                should_end_session=True
        else:
            tz = pytz.timezone('Asia/Kolkata')
            current_time=datetime.now(tz).time()
            current_day_no=datetime.today().weekday()
            current_day=days[current_day_no]
            print(current_time.hour)
            if(current_time.hour>12):
                current_time=current_time.hour-12
            else:
                current_time=current_time.hour
            print("Current Time "+str(current_time))    
            schedule_result=firebase.get('/schedule',None)
            classes=schedule_result[current_day]
            hours=[]
            minutes=[]
            for x in classes:
                s=datetime.strptime(x['time'], "%I:%M %p")
                hours.append(s.hour)
                minutes.append(s.minute)
            hours.append(current_time)
            print(hours)
            hours.sort()
            print(hours)
            class_time=""
            m=hours.index(current_time)
            if(m<len(hours)-1):
                m=m+1
                class_time=str(hours[m])
                for x in classes:
                    s=datetime.strptime(x['time'], "%I:%M %p")
                    if(str(s.hour)==class_time):
                        speech_output="Your next class is at "+x['time']+' of '+x['subject']+' with '+x['klass']+' .'
                        should_end_session=True
                        break
            elif(m==len(hours)-1):
                speech_output="No class"+" "+str(current_time)+' .'
                should_end_session=True
        return build_response(session_attributes, build_speechlet_response(
               card_title, speech_output, speech_output, should_end_session))

def make_list(intent,session):
    card_title="Make List"
    session_attributes={}
    should_end_session=True
    speech_output=""
    class_name=intent['slots']['class']['value']
    class_name=class_name.lower()
    list_name=intent['slots']['list']['value']
    students=firebase.get('/lists/'+class_name,None)
    speech_output=list_name+' value for '+students[0]['name']+'is .'
    return build_response(session_attributes, build_speechlet_response(
               card_title, speech_output, speech_output, should_end_session))
    
    
def on_intent(intent_request, session):
        """ Called when the user specifies an intent for this skill """
        print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

        intent = intent_request['intent']
        intent_name = intent_request['intent']['name']

        #Dispatch to your skill's intent handlers
        if intent_name=="StartAttendance":
                return start_attendance(intent,session)
        if intent_name=="ContinueAttendance":
                return continue_attendance(intent,session)
        if intent_name=="ScheduleIntent":
            return schedule_teacher(intent,session)
        if intent_name=="MakeListIntent":
            return make_list(intent,session)
        elif intent_name=="AMAZON.HelpIntent":
                return get_help(intent,session)
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
                return handle_session_end_request()
        else:
                raise ValueError("Invalid intent")

def start_attendance(intent,session):
        card_title="Start Attendance"
        session_attributes={}
        should_end_session=False
        speech_output=""
        result = firebase.get('/students', None)
        global students_list
        students_list=result
        print(result[0]['name'])
        student=result[0]['name']
        global first_student
        first_student=student
        global final_list
        final_list=copy.copy(result)
        print("Hello")
        print(final_list)
        speech_output="I am starting attendance. "+student
        print(speech_output)
        global flag
        flag=1
        return build_response(session_attributes, build_speechlet_response(
               card_title, speech_output, speech_output, should_end_session))

def on_session_ended(session_ended_request,session):
        """ Called when the user ends the session.
        Is not called when the skill returns should_end_session=true
        """
        print("on_session_ended requestId=" + session_ended_request['requestId'] +
              ", sessionId=" + session['sessionId'])
        # add cleanup logic here

def on_session_started(session_started_request, session):
        #Call on session start
        
        print("on_session_started requestId=" + session_started_request['requestId']
              + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def get_welcome_response():
        card_title="Welcome to Teacher Helper"
        should_end_session=False
        session_attributes={}
        speech_output="Welcome to Teacher Helper."\
                       "You can ask me to take attendance of class."
        reprompt_text=speech_output
        return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


        
def lambda_handler(event,context):
        print("event.session.application.applicationId="+
              event['session']['application']['applicationId'])

        if event['session']['new']:
                on_session_started({'requestId': event['request']['requestId']},
                                   event['session'])

        if event['request']['type']=="LaunchRequest":
                return on_launch(event['request'], event['session'])
        elif event['request']['type']=="IntentRequest":
                return on_intent(event['request'], event['session'])
        elif event['request']['type']=="SessionEndedRequest":
                return on_session_ended(event['request'], event['session'])


        

