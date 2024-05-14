#importing libraries
import os
import numpy as np
import flask
import joblib
import io
import cv2
import requests
from flask import Flask, render_template, request, Response

#creating instance of the class
app=Flask(__name__)

capture_camera = cv2.VideoCapture(0)
streaming_camera = cv2.VideoCapture(0)

#to tell flask what url shoud trigger the function index()
@app.route('/')
@app.route('/home')
def index():
    return flask.render_template('home.html')


@app.route('/upload-picture')
def uploadPicture():
    return flask.render_template('upload-picture.html')

@app.route('/final-result',methods = ['POST'])
def finalResult():
    if request.method == 'POST':   
        f = request.files['file'] 
        upload_directory = os.path.join(app.root_path, 'static')
        f.save(os.path.join(upload_directory, f.filename)) 
        return render_template("final-result.html", name = f.filename)  

def ValuePredictor(filename):
    loaded_model = joblib.load("checkpoints/model.pkl")
    result = loaded_model.predict(os.path.join(app.root_path+"/static/", filename))

    return result[0]

@app.route('/camera')
def camera():
    return flask.render_template("camera.html")

#Ref: https://parzibyte.me/blog/2021/02/10/python-acceder-camara-web-opencv-flask/ 
@app.route("/streaming_camara")
def streaming_camara():
    return Response(framesGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')

#function to get one frame of the camera using opencv(cv2)
def getFrameCamera(camera):

    isOk, frame = camera.read()

    if not isOk:
        return False, None
    
    _, bufer = cv2.imencode(".jpg", frame)
    image = bufer.tobytes()

    return True, image

#function to get frames of the camera, like streaming
def framesGenerator():
    streaming_camera = cv2.VideoCapture(0)
    while True:
        isOk, image = getFrameCamera(streaming_camera)
        if not isOk:
            break

        else:
            # Regresar la imagen en modo de respuesta HTTP
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + image + b"\r\n"

@app.route("/send_photo", methods=["GET"])
def sendPhoto():
    capture_camera = cv2.VideoCapture(0)

    isOk, frame = getFrameCamera(capture_camera)

    if not isOk:
        ConnectionAbortedError(500)
        return
    
    # Crear un archivo temporal en memoria para enviarlo como archivo adjunto
    filename = "foto.jpg"
    fileobj = io.BytesIO(frame)
    files = {'file': (filename, fileobj)}

    # Enviar la foto al método finalResult mediante una solicitud POST
    url = "http://127.0.0.1:5001/final-result"  # Reemplaza "tu_servidor" con la dirección de tu servidor
    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            capture_camera.release()
            streaming_camera.release()
            return render_template("final-result.html", name = filename)
        else:
            return f"Error al enviar la foto a finalResult(): {response.text}", 500
    except Exception as e:
        return f"Error al enviar la foto a finalResult(): {str(e)}", 500

@app.route('/result',methods = ['POST'])
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        try:
          
            to_predict_list = list(map(float, to_predict_list))
            result = ValuePredictor(to_predict_list)
            if int(result)==0:
                prediction='Iris-Setosa'
            elif int(result)==1:
                prediction='Iris-Virginica'
            elif int(result)==2:
                prediction='Iris-Versicolour'
            else:
                prediction=f'{int(result)} No-definida'
        except ValueError:
            prediction='Error en el formato de los datos'

        return render_template("result.html", prediction=prediction)


if __name__=="__main__":
    app.run(port=5001)
