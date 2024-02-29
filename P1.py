import warnings
import pyttsx3
import speech_recognition as sr
import psycopg2 as ps

conn = ps.connect("###")

cursor = conn.cursor()

warnings.filterwarnings("ignore")

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def talk(audio):
    engine.say(audio)
    engine.runAndWait()
    
def rec_audio():
    recog = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Listening...")
        audio = recog.listen(source)
        
    data1 = " "
    
    try:
        # data = recog.recognize_vosk(audio)
        data1 = recog.recognize_google(audio)
        # print("Google said:" + data1)
        # print("You said: " + data)
        
    except sr.UnknownValueError:
        return ""
        print("Assistant could not understand")
        
    except sr.RequestError as ex:
        return ""
        print("Request Error from Google Speech Recognition" + ex)
        
    return data1

# Starting Phase

talk("Hello! What would you like to do today?     Say 1 to Schedule an appointment     Say 2 to Cancel an appointment     Say 3 to Reschedule an appointment")

text_01 = rec_audio()

import openai

def keys(para, tex):
    openai.api_key = "###"

    t_02 = tex + "Give me only " + para + " from the above sentence"
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": t_02}])
    return completion.choices[0].message.content


from datetime import datetime
import datetime
from datetime import datetime
def schedule():
    cursor.execute("SELECT * FROM appointments WHERE is_booked = False AND slots >= NOW()")
    available_slots = cursor.fetchall()
    talk("Hello! I have the following availability : ")
    for slot in available_slots:
        t1 = slot[3]
        formatted_date = t1.strftime("%d %B %I%p")
        talk(formatted_date)
    talk(" When would you like to come in?")
    book_app = rec_audio()
    
    time_01 = keys("time and date", book_app)
    print_time = time_01
    
    time_01 = "2024 " + str(time_01)
    time_01 = time_01.replace("st", "").replace("nd", "").replace("rd", "").replace("th", "").replace(".", "").replace(",", "").replace("at", "")
    
    dt = datetime.strptime(time_01, "%Y %B %d %I:%M %p")
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    dt = str(dt) + "+00"
    
    cursor.execute(f"SELECT COUNT(*) FROM appointments WHERE slots = '{dt}'")
    result = cursor.fetchone()
    
    if result[0] > 0:
        str1 = "Okay great! I booked an appointment for " + print_time +  " Can I get your phone number and Name? "
        talk(str1)
        info_patient = rec_audio()
        name = keys("name", info_patient)
        name = name.lower()
        phone_number = keys("number", info_patient)
        phone_number = phone_number.replace(" ", "")
        
        cursor.execute("UPDATE appointments SET name = %s, phone_number = %s, is_booked = %s WHERE slots = %s", (name, phone_number, True, dt))
        conn.commit()
        
        talk("Done")
    else:
        talk("The slot is not available. Please choose another slot.")
    
    
    
def cancel():
    talk("Can I know your name?")
    cancel_app = rec_audio()
    name_01 = keys("name", cancel_app)
    name_01 = name_01.lower()
    
    cursor.execute(f"SELECT COUNT(*) FROM appointments WHERE name = '{name_01}'")
    result = cursor.fetchone()
    
    if result[0] > 0:
        
        cursor.execute(f"SELECT slots FROM appointments WHERE name = '{name_01}'")
        dt = cursor.fetchone()
        
        if dt:
            cursor.execute(f"DELETE FROM appointments WHERE name = '{name_01}'")
            cursor.execute("INSERT INTO appointments (slots, is_booked) VALUES (%s, %s)", (dt[0], False))
            conn.commit()
            talk("Okay see you soon!")
        else:
            talk("You have no appointments")
            
    else :
        talk("I am sorry! I could not find your name in the database")



def reschedule():
    talk("Can I know your name?")
    res_app = rec_audio()
    name_01 = keys("name", res_app)
    name_01 = name_01.lower()
    
    talk("Can I know your slot?")
    res_app = rec_audio()
    time_01 = keys("time and date", res_app)
    
    time_01 = "2024 " + str(time_01)
    time_01 = time_01.replace("st", "").replace("nd", "").replace("rd", "").replace("th", "").replace(".", "").replace(",", "").replace("at", "")
   
    dt = datetime.strptime(time_01, "%Y %B %d %I:%M %p")
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    
    
    
    cursor.execute(f"SELECT COUNT(*) FROM appointments WHERE slots = '{dt}'")
    result = cursor.fetchone()
    if result[0] > 0:
        
        cursor.execute(f"SELECT name FROM appointments WHERE slots = '{dt}'")
        name = cursor.fetchone()[0]
        name = name.lower()
        cursor.execute(f"SELECT phone_number FROM appointments WHERE slots = '{dt}'")
        number = cursor.fetchone()[0]
        
        if name == name_01:
            
            cursor.execute(f"UPDATE appointments SET name = NULL, phone_number = NULL, is_booked = False WHERE slots = '{dt}'")
            conn.commit()
            cursor.execute("SELECT * FROM appointments WHERE is_booked = False AND slots != %s AND slots >= NOW()", (dt,))
            
            available_slots = cursor.fetchall()
            talk("Hello! I have the following availability : ")
            for slot in available_slots:
                t1 = slot[3]
                formatted_date = t1.strftime("%d %B %I%p")
                talk(formatted_date)
                
            talk(" When would you like to come in?")     
            book_app = rec_audio()
            
            
            time_01 = keys("time and date", book_app)
            print_time = time_01
            time_01 = "2024 " + str(time_01)
            time_01 = time_01.replace("st", "").replace("nd", "").replace("rd", "").replace("th", "").replace(".", "").replace(",", "").replace("at", "")
            
            dt = datetime.strptime(time_01, "%Y %B %d %I:%M %p")
            dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(f"SELECT COUNT(*) FROM appointments WHERE slots = '{dt}'")
            result = cursor.fetchone()
            
            if result[0] > 0:
                talk("Okay great! I booked an appointment for " + print_time)
                
                cursor.execute("UPDATE appointments SET name = %s, phone_number = %s, is_booked = %s WHERE slots = %s", (name, number, True, dt))
                conn.commit()
                
                talk("Done")
            else:
                talk("The slot is not available. Please choose another slot.")
        else:
            talk("You are illegal")
    else:
        talk("Okay! Thank You!")


openai.api_key = "###"
t_02 = text_01 + " Tell me which word is present one, two or three in above sentence pls give me only that word as an answer"
completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": t_02}])
text_03 = completion.choices[0].message.content

if text_03 == "one":
    schedule()
elif text_03 == "two":
    cancel()
else:
    reschedule()
