import pyttsx3


import speech_recognition as sr

engine = pyttsx3.init('sapi5')
def speak(audio):
    print('Computer: ' + audio)
    engine.say(audio)
    engine.runAndWait()
def myCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language='en-in')
        print('User: ' + query + '\n')

    except sr.UnknownValueError:
        speak('Sorry sir! I didn\'t get that! Try typing the command!')
        query = str(input('Command: '))

    return query
