import os
import json
import datetime
import requests
import pyttsx3
import pyaudio
from vosk import Model, KaldiRecognizer

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0 - мужской голос, 1 - женский

BASE_URL = "https://date.nager.at/api/v3/publicholidays"
DEFAULT_YEAR = datetime.datetime.now().year
DEFAULT_COUNTRY = "RU" 

def speak(text):
    print(f"Ассистент: {text}")
    engine.say(text)
    engine.runAndWait()

def get_holidays(year=DEFAULT_YEAR, country_code=DEFAULT_COUNTRY):
    try:
        response = requests.get(f"{BASE_URL}/{year}/{country_code}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        speak("Произошла ошибка при запросе к API. Пожалуйста, проверьте подключение к интернету.")
        return None

def list_holidays(holidays):
    """Озвучивание названий праздников"""
    if not holidays:
        speak("Нет данных о праздниках.")
        return
    
    speak("Список праздников:")
    for holiday in holidays:
        speak(holiday['localName'])

def save_holidays_names(holidays):
    """Сохранение названий праздников в файл"""
    if not holidays:
        speak("Нет данных для сохранения.")
        return
    
    with open("holidays_names.txt", "w", encoding="utf-8") as f:
        for holiday in holidays:
            f.write(f"{holiday['localName']}\n")
    speak("Названия праздников сохранены в файл holidays_names.txt")

def save_holidays_with_dates(holidays):
    if not holidays:
        speak("Нет данных для сохранения.")
        return
    
    with open("holidays_with_dates.txt", "w", encoding="utf-8") as f:
        for holiday in holidays:
            f.write(f"{holiday['date']} - {holiday['localName']}\n")
    speak("Даты и названия праздников сохранены в файл holidays_with_dates.txt")

def find_nearest_holiday(holidays):
    if not holidays:
        speak("Нет данных о праздниках.")
        return
    
    today = datetime.datetime.now().date()
    nearest_holiday = None
    min_delta = datetime.timedelta(days=365)
    
    for holiday in holidays:
        holiday_date = datetime.datetime.strptime(holiday['date'], "%Y-%m-%d").date()
        
        if holiday_date >= today:
            delta = holiday_date - today
            if delta < min_delta:
                min_delta = delta
                nearest_holiday = holiday
    
    if nearest_holiday:
        speak(f"Ближайший праздник: {nearest_holiday['localName']}, {nearest_holiday['date']}")
    else:
        speak("В этом году больше не будет праздников.")

def count_holidays(holidays):
    if not holidays:
        speak("Нет данных о праздниках.")
        return
    
    speak(f"Количество праздников в году: {len(holidays)}")

def recognize_speech():
    model = Model("vosk-model-small-ru-0.22")
    recognizer = KaldiRecognizer(model, 16000)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()
    
    speak("Слушаю вашу команду...")
    
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if result['text']:
                return result['text']
    
    stream.stop_stream()
    stream.close()
    p.terminate()

def main():
    speak("Привет! Я голосовой ассистент для работы с публичными праздниками.")
    
    while True:
        try:
            command = recognize_speech().lower()
            print(f"Вы сказали: {command}")
            
            if "перечислить" in command:
                holidays = get_holidays()
                list_holidays(holidays)
            elif "сохранить" in command:
                holidays = get_holidays()
                save_holidays_names(holidays)
            elif "даты" in command:
                holidays = get_holidays()
                save_holidays_with_dates(holidays)
            elif "ближайший" in command:
                holidays = get_holidays()
                find_nearest_holiday(holidays)
            elif "количество" in command:
                holidays = get_holidays()
                count_holidays(holidays)
            elif "выход" in command or "стоп" in command:
                speak("До свидания!")
                break
            else:
                speak("Я не понял команду. Пожалуйста, повторите.")
                
        except Exception as e:
            print(f"Ошибка: {e}")
            speak("Произошла ошибка. Пожалуйста, повторите команду.")

if __name__ == "__main__":
    if not os.path.exists("vosk-model-small-ru-0.22"):
        speak("Для работы программы необходимо скачать модель распознавания речи Vosk для русского языка.")
    else:
        main()