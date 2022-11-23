from flask import Flask, jsonify
from flask import request, Response
# from marshmallow import Schema, fields
import dill, statistics
import sklearn

import pandas as pd
import numpy as np

model1 = dill.load(open('saved_models/module_1/svc_98.41.pkl', 'rb'))
model2 = dill.load(open('saved_models/module_2/3_features/knn1_AdjR2_0.79.pkl', 'rb'))

app = Flask(__name__)


@app.route('/getNPK', methods=['POST'])
def getNPK():
    rainfall = float(request.args.get('water_level'))
    pH_Val = float(request.args.get('ph'))
    soil_moist = float(request.args.get('soil_moisture'))

    N_val, P_val, K_val = model2.predict([[rainfall, pH_Val, soil_moist]])[0]

    N_val = round(N_val, 2)
    P_val = round(P_val, 2)
    K_val = round(K_val, 2)

    return jsonify({'N': N_val, 'P': P_val, 'K': K_val})


@app.route('/getCrop', methods=['POST'])
def getCrop():
    temp = pd.DataFrame()
    # print(request.args.get('pincode'))

    if not (request.args.get('pincode') is None):
        print('Cond 1 executed')
        base_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
        area_code = str(request.args.get('pincode'))
        api_secret = 'PWVW6BHSHN68KYTA99RLNNDBF'
        metri = '?unitGroup=metric&include=days&key='
        req_type = '&contentType=csv'
        df = pd.read_csv(base_url + area_code + metri + api_secret + req_type)
        
        temp['temperature'] = df['temp']
        temp['humidity'] = df['humidity']
        temp['ph'] = int(request.args.get('ph'))
        temp['rainfall'] = df['precip']
        temp['soil_moisture'] = int(request.args.get('soil_moisture'))
        recmnd = statistics.mode(model1.predict(np.array(temp)))
    else:
        print('Cond 2 executed')
        print(request.args.get('temperature'))
        print(request.args.get('humidity'))
        print(request.args.get('ph'))
        print(request.args.get('water_level'))
        print(request.args.get('soil_moisture'))

        temp = [float(request.args.get('temperature')), float(request.args.get('humidity')),
                float(request.args.get('ph')), float(request.args.get('water_level')),
                float(request.args.get('soil_moisture'))]
        recmnd = statistics.mode(model1.predict(np.array([temp])))

        """        
        temp['temperature'] = list(request.args.get('temperature'))
        temp['humidity'] = list(request.args.get('humidity'))
        temp['ph'] = list(request.args.get('ph'))
        temp['rainfall'] = list(request.args.get('water_level'))
        temp['soil_moisture'] = list(request.args.get('soil_moisture'))
        """
    print(temp)
    print(recmnd)

    if (recmnd == "rice" or recmnd == "blackgram" or recmnd == "pomegranate" or recmnd == "papaya"
            or recmnd == "cotton" or recmnd == "orange" or recmnd == "coffee" or recmnd == "chickpea"
            or recmnd == "mothbeans" or recmnd == "pigeonpeas" or recmnd == "jute" or recmnd == "mungbean"
            or recmnd == "lentil" or recmnd == "maize" or recmnd == "apple"):
        cropStatement = recmnd.capitalize() + " should be harvested. It's a Kharif crop, so it must be sown at the beginning of the rainy season e.g between April and May."
    elif (
            recmnd == "muskmelon" or recmnd == "kidneybeans" or recmnd == "coconut" or recmnd == "grapes" or recmnd == "banana"):
        cropStatement = recmnd.capitalize() + " should be harvested. It's a Rabi crop, so it must be sown at the end of monsoon and beginning of winter season e.g between September and October."
    elif (recmnd == "watermelon"):
        cropStatement = recmnd.capitalize() + " should be harvested. It's a Zaid Crop, so it must be sown between the Kharif and rabi season i.e between March and June."
    elif (recmnd == "mango"):
        cropStatement = recmnd.capitalize() + " should be harvested. It's a cash crop and also perennial. So you can grow it anytime."

    return jsonify({'crop': recmnd, 'recommendation': cropStatement})


if __name__ == '__main__':
    app.run(debug=True)
