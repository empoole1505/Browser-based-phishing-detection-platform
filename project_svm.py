#!/home/ethan/miniconda3/bin/python3
import sys, os, time, json, struct, select, joblib
import tkinter as tk
import pyscreenshot
import pytesseract as tess
from PIL import Image


os.environ['DISPLAY'] = ':0'
os.environ['XAUTHORITY'] = '/home/ethan/.Xauthority'
LOG_FILE = "/home/ethan/Desktop/svm_debug.log"

def log_error(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} - {message}\n")


try:
    clf = joblib.load('/home/ethan/Desktop/wellysai.pkl')
    vectorizer = joblib.load('/home/ethan/Desktop/vectorizer.pkl')
except Exception as e:
    log_error(f"error": "loading dataset {e}")
    sys.exit(1)


root = tk.Tk() #prepeares GUI
root.withdraw() #hides rest of window so only the GUI is displayed

def draw_scopes(x, y): #draws 4 blue boxes that outline the area of where a screen capture is to take place
    L = tk.Toplevel(root) #closes automatic window borders to only display the GUI
    L.overrideredirect(True) 
    L.geometry(f"30x30+{x}+{y}") #size of blue boxes is set to 30x30 at x and y coordinates
    L.attributes("-topmost", True) # GUI is set to appear at front most part of screen (windows that may be open)
    L.attributes("-type", "splash") #window is hidden from task bar
    L.config(bg='blue') #colour of boxes set to blue
    return L

L1, L2, L3, L4 = draw_scopes(628, 268), draw_scopes(1899, 268), draw_scopes(628, 1033), draw_scopes(1899, 1033) #boxes are placed in coordinates
root.update() #boxes display


def send_message(message):
    try:
        content = json.dumps(message).encode('utf-8')
        sys.stdout.buffer.write(struct.pack('I', len(content)))
        sys.stdout.buffer.write(content)
        sys.stdout.buffer.flush()
    except Exception as e:
        log_error(f"error in connecting to chrome extension {e}")

def scanandml():
    time.sleep(0.2) #wait 0.2 seconds to not run too early and cause an error
    try:
        img = pyscreenshot.grab(bbox=(628, 268, 1899, 1033)) #screenshot at these coordnates andassign to img variable
        text = tess.image_to_string(img).strip() # image is converted into a string of text (blank white space is removed)
        
        if text: #if text has been detected


            text_tfidf = vectorizer.transform([text]) #vectorise text using TFIDF
            prediction = clf.predict(text_tfidf)[0] #ml model will make a prediction by using the vectorised text as input data for ml model
            

            result_str = "This email is likely safe" if str(prediction) == "0" else "This email is likely phishing" #if prediction is 1 it is likely phishing if 0 likely benign
            send_message({"text": result_str}) #result is sent to the chrome extension to be displayed
            log_error(f"{text[:20]}Prediction: {result_str}") #result is displayed in log
        else:
            send_message({"text": "error in finding an email to scan"}) # if text has not been detected report it to the error log
    except Exception as e:
        log_error(f"Scan failed {e}") #if an unexpected error occurs it is logged

def listen(): #listens for messages from the browser extension
    if select.select([sys.stdin], [], [], 0)[0]:
        try:
            raw_length = sys.stdin.buffer.read(4)
            if raw_length:
                length = struct.unpack('I', raw_length)[0]
                message = json.loads(sys.stdin.buffer.read(length).decode('utf-8'))
                if message.get("action") == "scan": #if message recieved is the scan button which occurs when the button is clicked
                    scanandml() #run the function that performs screen capture, OCR and the ml model which also outputs result to the extension
        except:
            sys.exit(0)
    root.after(100, listen)

root.after(100, listen)
root.mainloop()