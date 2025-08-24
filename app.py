from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from src.model import model as cancer_model

app = Flask(__name__)
app.secret_key = 'jimjimsecretjim'


questions = [
    {'name': 'Age', 'type': 'number', 'label': 'What is your age?'},
    {'name': 'Gender', 'type': 'select', 'label': 'What is your biological sex?', 'options': ['Female', 'Male']},
    {'name': 'Weight', 'type': 'number', 'label': 'What is your weight in kilograms (kg)?'},
    {'name': 'Height', 'type': 'number', 'label': 'What is your height in centimeters (cm)?'},
    {'name': 'Smoking', 'type': 'select', 'label': 'Do you currently smoke or have a history of smoking?', 'options': ['No', 'Yes']},
    {'name': 'GeneticRisk', 'type': 'select', 'label': 'Has any of your alive or dead relatives had cancer?', 'options': ['No', 'Some relatives', 'Many relatives']},
    {'name': 'PhysicalActivity', 'type': 'number', 'label': 'How many hours do you exercise per week? (e.g. 3)'},
    {'name': 'AlcoholIntake', 'type': 'number', 'label': 'How many alcoholic drinks do you have per week? (e.g. 2)'},
    {'name': 'CancerHistory', 'type': 'select', 'label': 'Have you ever been diagnosed with cancer before?', 'options': ['No', 'Yes']}
]


option_maps = {
    'Gender': {'Female': 0, 'Male': 1},
    'Smoking': {'No': 0, 'Yes': 1},
    'GeneticRisk': {'No': 0, 'Some relatives': 1, 'Many relatives': 2},
    'CancerHistory': {'No': 0, 'Yes': 1}
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/start')
def start():
    session['answers'] = {}
    return redirect(url_for('question', qid=0))

@app.route('/question/<int:qid>', methods=['GET', 'POST'])
def question(qid):
    if qid >= len(questions):
        return redirect(url_for('summary'))
    question = questions[qid]
    if request.method == 'POST':
        answer = request.form.get('answer')

        if question['type'] == 'select':
            answer_text = question['options'][int(answer)]
            session['answers'][question['name']] = answer_text
        else:
            session['answers'][question['name']] = answer
        session.modified = True
        return redirect(url_for('question', qid=qid+1))
    return render_template('question.html', question=question, qid=qid)

@app.route('/summary')
def summary():
    answers = session.get('answers', {})

    model_input = {}
    for q in questions:
        name = q['name']
        val = answers.get(name)
        if q['type'] == 'select':
            val = option_maps[name][val]
        elif q['type'] == 'number':
            val = float(val) if '.' in str(val) else int(val)
        model_input[name] = val

    weight = float(model_input.pop('Weight'))
    height_cm = float(model_input.pop('Height'))
    height_m = height_cm / 100.0
    bmi = weight / (height_m ** 2)
    model_input['BMI'] = bmi

    feature_order = ['Age','Gender','BMI','Smoking','GeneticRisk','PhysicalActivity','AlcoholIntake','CancerHistory']
    ordered_input = {k: model_input[k] for k in feature_order}
    df = pd.DataFrame([ordered_input])
    probability = cancer_model.predict(df)

    if probability is not None:
        if probability >= 80:
            color = 'red-600'
            result = f"High risk: {probability:.2f}% chance of cancer."
        elif probability >= 50:
            color = 'orange-400'
            result = f"Medium risk: {probability:.2f}% chance of cancer."
        else:
            color = 'green-600'
            result = f"Low risk: {probability:.2f}% chance of cancer."
    else:
        color = 'green-600'
        result = "Low risk: Model predicts no cancer."
    return render_template('summary.html', answers=answers, result=result, color=color)

if __name__ == '__main__':
    app.run(debug=True)