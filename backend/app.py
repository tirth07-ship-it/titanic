from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import json
import os

app = Flask(__name__)
CORS(app)

# Load model and stats
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'titanic_model.pkl')
STATS_PATH = os.path.join(os.path.dirname(__file__), 'model', 'stats.json')

model = joblib.load(MODEL_PATH)
with open(STATS_PATH) as f:
    model_stats = json.load(f)




@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        pclass = int(data['pclass'])
        sex = 1 if data['sex'] == 'male' else 0
        age = float(data['age'])
        sibsp = int(data['sibsp'])
        parch = int(data['parch'])
        fare = float(data['fare'])
        embarked_map = {'S': 0, 'C': 1, 'Q': 2}
        embarked = embarked_map.get(data['embarked'], 0)

        import pandas as pd
        feature_names = ['Pclass', 'Sex_encoded', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked_encoded']
        features = pd.DataFrame([[pclass, sex, age, sibsp, parch, fare, embarked]], columns=feature_names)
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]

        survival_prob = round(float(probability[1]) * 100, 1)
        death_prob = round(float(probability[0]) * 100, 1)

        return jsonify({
            'survived': int(prediction),
            'survival_probability': survival_prob,
            'death_probability': death_prob,
            'message': 'SURVIVED' if prediction == 1 else 'DID NOT SURVIVE'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/stats')
def stats():
    return jsonify(model_stats)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
