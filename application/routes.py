from crypt import methods
from ctypes import util
from application import app, dropzone
from flask import render_template, request, redirect, url_for
from .forms import QRCodeData
import secrets
import os

# OCR
import cv2
import pytesseract
from PIL import Image
import numpy as np
# pip install gTTS
from gtts import gTTS

# import utils
from . import utils

sentence = ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == 'POST':

        # file processing
        global sentence

        f = request.files.get('file')
        filename, extension = f.filename.split(".")
        generated_filename = secrets.token_hex(10) + f".{extension}"
       

        file_location = os.path.join(app.config['UPLOADED_PATH'], generated_filename)

        f.save(file_location)

        # print(file_location)

        # OCR here
        pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

        img = cv2.imread(file_location)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


        boxes = pytesseract.image_to_data(img)
        # print(boxes)
    


        for i, box in enumerate(boxes.splitlines()):
            if i == 0:
                continue

            box = box.split()
            # print(box)

            # only deal with boxes with word in it.
            if len(box) == 12:
                sentence += box[11] + " "
       
        # print(sentence)

        # delete file after you are done working with it
        os.remove(file_location)

    else:
       return render_template("upload.html", title="Home")


@app.route("/decoded", methods=["GET", "POST"])
def decoded():
    global sentence

    form =QRCodeData() 

    if request.method == "POST":
        generated_audio_filename = secrets.token_hex(10) + ".mp4"
        text_data = form.data_field.data
        translate_to = form.language.data
        # print("Data here", translate_to)

  
        translated_text = utils.translate_text(text_data, translate_to)
        print(translated_text)
        tts = gTTS(translated_text, lang=translate_to)



        file_location = os.path.join(
                            app.config['AUDIO_FILE_UPLOAD'], 
                            generated_audio_filename
                        )

        # save file as audio
        tts.save(file_location)

        return redirect("/audio_download/" + generated_audio_filename)


    form.data_field.data = sentence

    # print(lang)
    lang, _ = utils.detect_language(sentence)
    # print(lang, conf)

    # set the sentence back to defautl blank
    sentence = ""

    return render_template("decoded.html", 
                            title="Decoded", 
                            form=form, 
                            lang=utils.languages.get(lang)
                        )


@app.route("/audio_download/<string:file_name>", methods=["GET"])
def audio_file_download(file_name):
    print(file_name)

    file_location = os.path.join(
                    app.config['AUDIO_FILE_UPLOAD'], 
                    file_name
            )


    return render_template("audio_download.html", 
                            title="audio downlaod", 
                            file = file_name
                        )

