import speech_recognition as sr
import wikipedia
import pyttsx3
import threading
import subprocess,os,sys,re
import time
from newsapi import NewsApiClient
import numpy as np
from PIL import Image
import pytesseract
import cv2

medicines = []
cam = cv2.VideoCapture(0)

api = NewsApiClient(api_key='4a52e685c95049fda718a7b094df1643')

ones = ["", "one ","two ","three ","four ", "five ", "six ","seven ","eight ","nine ","ten ","eleven ","twelve ", "thirteen ", "fourteen ", "fifteen ","sixteen ","seventeen ", "eighteen ","nineteen "]

twenties = ["","","twenty ","thirty ","forty ", "fifty ","sixty ","seventy ","eighty ","ninety "]

thousands = ["","thousand ","million ", "billion ", "trillion ", "quadrillion ", "quintillion ", "sextillion ", "septillion ","octillion ", "nonillion ", "decillion ", "undecillion ", "duodecillion ", "tredecillion ", "quattuordecillion ", "quindecillion", "sexdecillion ", "septendecillion ", "octodecillion ", "novemdecillion ", "vigintillion "]


def read(engine):
    ret_val,img = cam.read()
    scale_factor = 3

    img = cv2.bitwise_not(img)
    cv2.imwrite("helping.png", img)

    img = cv2.imread('helping.png', cv2.IMREAD_GRAYSCALE)
    
    ret,img = cv2.threshold(img,125,255,cv2.THRESH_BINARY)
    img = cv2.resize(img,None,fx=scale_factor, fy=scale_factor, interpolation = cv2.INTER_CUBIC)
    tts("This is what it says",engine)
    kernel = np.ones((5,5),np.float32)/25
    img = cv2.filter2D(img,-1,kernel)
    cv2.medianBlur(img,3)
    cv2.imwrite("helping.png", img)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Mugilan\AppData\Local\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(Image.open("helping.png"))
    print(text)
    tts(text,engine)

    
def num999(n):
    c = n % 10 # singles digit
    b = ((n % 100) - c) / 10 # tens digit
    a = ((n % 1000) - (b * 10) - c) / 100 # hundreds digit
    t = ""
    h = ""
    if a != 0 and b == 0 and c == 0:
        t = ones[a] + "hundred "
    elif a != 0:
        t = ones[a] + "hundred and "
    if b <= 1:
        h = ones[n%100]
    elif b > 1:
        h = twenties[b] + ones[c]
    st = t + h
    return st

def num2word(num):
    if num == 0: return 'zero'
    i = 3
    n = str(num)
    word = ""
    k = 0
    while(i == 3):
        nw = n[-i:]
        n = n[:-i]
        if int(nw) == 0:
            word = num999(int(nw)) + thousands[int(nw)] + word
        else:
            word = num999(int(nw)) + thousands[k] + word
        if n == '':
            i = i+1
        k += 1
    return word[:-1]

def recognize_speech_from_mic(recognizer, microphone,engine,state):

    passed = False

    while passed == False:

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        response = {
            "success": True,
            "error": None,
            "transcription": None
        }
        

        try:
            response["transcription"] = recognizer.recognize_google(audio)
            passed = True
        except:
            if state == True:
                passed = False
            else:
                print("standalone")

    print("ready",response["transcription"])

    if response["transcription"]:
        try:
            engine.endLoop()
            print("Stopping")
        except:
            pass

    return response["transcription"]

def wikipedian(query,engine,recognizer,microphone):

    tts("Searching for "+query,engine)
    result = wikipedia.summary(query)
    tts("Here is what I have found",engine)
    t1 = threading.Thread(target=tts, args=(result,engine))
    t2 = threading.Thread(target=recognize_speech_from_mic, args=(recognizer, microphone,engine,True))

    t2.start()
    t1.start()

    t2.join()
    t1.join()


def tts(text,engine):

    engine.say(text)
    engine.runAndWait()

def medicine_list_add(number,item,engine):
    string = "I've added " + str(number) + item
    medicines.append(str(number)+" "+item)
    tts(string,engine)

def medicine_list_remove(number,item,engine):
    string = "I've removed " + str(number) + item
    try:
        medicines.remove(str(number)+" "+item)
        tts(string,engine)
    except:
        tts("There is no such item in your list",engine)

def sos(engine):
    tts("Help is on the way",engine)

def news(engine):
    tts("Here are the current headlines",engine)
    articlesD = api.get_top_headlines(sources='bbc-news')
    for i in range(0,3):
        tts(articlesD['articles'][i]['title'],engine)
        time.sleep(0.2)

def main():

    engine = pyttsx3.init()
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    adding = re.compile(r'extend (\S+) (\w+)$')
    removing = re.compile(r'remove (\S+) (\w+)$')
    plex = re.compile(r'^""')
    plex2 = re.compile(r'^""')

    while True:
        print("Wait up to 2 seconds before speaking")
        speech = recognize_speech_from_mic(recognizer, microphone,engine,False)
        speech = speech.lower()
        print(speech)
        if(True):
            if (speech.find("search wikipedia for") > -1 ):
                index = speech.find("search wikipedia for") + 21
                wikipedian(speech[index:],engine,recognizer,microphone)
            elif(speech.find("tell me my list")>-1):
                if medicines == []:
                    tts("There is nothing in your list",engine)
                else:
                    for medicine in medicines:
                        tts(medicine,engine)
                        time.sleep(0.3)
            elif(re.search(adding,speech)):
                amount = re.search(adding,speech).group(1)
                try:
                    amount = int(amount)
                    amount = num2word(amount)
                except:
                    amount = amount
                medicine_list_add(amount,re.search(adding,speech).group(2),engine)
            elif(re.search(removing,speech)):
                amount = re.search(removing,speech).group(1)
                try:
                    amount = int(amount)
                    amount = num2word(amount)
                except:
                    amount = amount
                medicine_list_remove(amount,re.search(removing,speech).group(2),engine)
            elif(speech.find("i need help")>-1):
                sos(engine)
            elif(speech.find("tell me the news")>-1):
                news(engine)
            elif(speech.find("read this")>-1):
                read(engine)
            else:
                tts("Sorry I couldn't catch that",engine)
                print("null")
        else:
            pass

if __name__ == '__main__':
    main()
