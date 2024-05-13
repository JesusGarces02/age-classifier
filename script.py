#importing libraries
import os
import numpy as np
import flask
import joblib
from flask import Flask, render_template, request

#creating instance of the class
app=Flask(__name__)

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

def ValuePredictor(to_predict_list):
    to_predict = np.array(to_predict_list).reshape(1, 4)
    loaded_model = joblib.load("checkpoints/model.pkl")
    result = loaded_model.predict(to_predict)

    return result[0]

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