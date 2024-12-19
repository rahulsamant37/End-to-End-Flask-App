from flask import Flask,render_template,request
import os
import numpy as np
import pandas as pd
from src.datascience import logger
from src.datascience.pipeline.prediction_pipeline import PredictionPipeline

app=Flask(__name__)

@app.route('/',methods=['GET'])# route to display the home page
def homepage():
    return "Welcome to Flask App!"

@app.route('/Model',methods=['GET'])
def model_main():
    return render_template('index.html')

@app.route('/train',methods=['GET'])
def train_model():
    os.system("python main.py")
    return "Model Trained Successfully"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get values from the form
        data = [
            float(request.form['sepal_length']),
            float(request.form['sepal_width']),
            float(request.form['petal_length']),
            float(request.form['petal_width']),

        ]
        
        data = np.array(data).reshape(1, 4)

        # Make prediction
        obj = PredictionPipeline()
        prediction = obj.predict(data)
        
        return render_template('results.html', result=str(prediction))
    except Exception as e:
        return "Something is Wrong!"

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8080)