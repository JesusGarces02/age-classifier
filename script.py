#importing libraries
import os
import flask
import io
import cv2
import requests
from flask import Flask, render_template, request, Response

from app.model import predict

#creating instance of the class
app = Flask(__name__)

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
        img_bytes = f.read()
        
        # Guardar la imagen en la carpeta static/images
        upload_directory = os.path.join(app.root_path, 'static/sources')
        if not os.path.exists(upload_directory):
            os.makedirs(upload_directory)
        file_path = os.path.join(upload_directory, f.filename)
        
        # Guardar la imagen usando los bytes leídos
        with open(file_path, 'wb') as image_file:
            image_file.write(img_bytes)

        prediction = predict(img_bytes)
        print(prediction)

        return render_template("final-result.html", name=f.filename, prediction=prediction)

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
    url = "http://127.0.0.1:5001/final-result"  
    try:
        response = requests.post(url, files=files)
        print('Esta es mi ${}'.format(response))
        if response.status_code == 200:
            capture_camera.release()
            streaming_camera.release()

            return response.text
        else:
            return f"Error al enviar la foto a finalResult(): {response.text}", 500
    except Exception as e:
        return f"Error al enviar la foto a finalResult(): {str(e)}", 500



if __name__=="__main__":
    app.run(port=5001)
