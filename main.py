from flask import Flask, render_template , redirect , request , session ,flash , send_from_directory
import os
import json
import csv
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from function_final import predict_responses , predict_responses_randon_qa
import random
# from Flaskaginate import Pagination

app = Flask(__name__)
app.secret_key = 'any_random_string'

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/questions')
def question():
    with open('questions.json' , 'r') as file:
           files= json.load(file)    
    return render_template('question.html', questions = files['questions'])

def save_answer(answer):
    with open('answer.csv' , 'a' , newline='') as csvfile:
        
        fieldnames = ['name','q1', 'q2', 'q3', 'q4', 'q5' , 'q6' , 'q7' , 'q8', 'q9' , 'q10' , 'q11' , 'q12' , 'q13', 'q14' , 'q15' , 'q16' , 'q17','q18','q19','q20','q21','q22','q23','q24','q25','q26','q27','q28','q29','q30','q31','q32','q33','q34','q35']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(answer)
    return True


@app.route('/get_answers' , methods = ['POST'])
def answer():
    if request.method == 'POST':
        name = request.form['name']
        answer = {}
        answer.update({'name' : name})
        
        for _ in range(1,36):
           index = f'q{_}'
           ans = request.form[index]
           ans = {index : ans}
           answer.update(ans)
        if answer != '':        
            try:
                save_answer(answer)
                flash('You have successfully contributed the data')
            except:
                print("An exception occurred")
        return redirect('/')    
    return redirect('/')


@app.route('/recomm' , methods = ['GET','POST'])
def recomm_system():
    with open('questions.json' , 'r') as file:
           files= json.load(file)

    twenty_questions_only = files['questions']    
    for i in range(5):
        twenty_questions_only.pop(random.randint(0 ,len(twenty_questions_only) -1))
    return render_template('recomm_system.html',questions = twenty_questions_only)

@app.route('/predict_answer' , methods = ['GET','POST'])
def predict_answer():
    if request.method == 'POST':
       answer = get_yes_no_ans()
       answer_to_list_for_prediction = []
      
       for i in range(1,31):
           answer_to_list_for_prediction.append(answer[f'q{i}'])
       result = predict_responses(answer_to_list_for_prediction)
       formated_result = {}

       for i in range(0,5):
           formated_result.update({f'q2{i+1}' : ('yes' if result[i] == 1 else 'no')})      
       final_result = {**answer, **formated_result}
       
       save_answer(final_result)
       session['result'] = final_result       
       return render_template('result_y_n.html' , data = final_result , questions = get_questions())
    return redirect('/recomm')

# this is the route that returns the answer from random question asked
@app.route('/predict_answer_random' , methods = ['GET','POST'])
def predict_answer_random():
    if request.method == 'POST':
       answer = get_yes_no_ans()
       name = answer['name']    
       output = predict_responses_randon_qa(answer)
       final_result = {**answer, **output}
       final_result.update({'name' : name})
       save_answer(final_result)
       session['result'] = final_result 
       return render_template('predicted_output.html' , all_data = final_result , predicted_answer = output , questions = get_questions())
    return redirect('/recomm')

@app.route('/save_predict' , methods = ['GET','POST'])
def save_predict_answer():
    try:
        output = session['result']
        flash('You have successfully save the data')
        return redirect('/')
    except Exception:
        return redirect('/')
    
def get_yes_no_ans(answer_till_question = 35):
    name = request.form['name']
    answer = {}
    answer.update({'name' : name})
    for _ in range(1,answer_till_question + 1):
        try:
            index = f'q{_}'
            ans = request.form[index]
            ans = {index : ans}
            answer.update(ans)
        except Exception as e:
            continue
    return answer


def get_questions():
    with open('questions.json' , 'r') as file:
           files= json.load(file)
    return files['questions']


@app.route('/admin' , methods = ['GET','POST'])
def admin():
    if session.get('logged_in') == True:
        with open('answer.csv' , 'r' ) as csvfile:
            data = csv.reader(csvfile)
            header = next(data)
            list_data = list(data)
            reversed_list = list_data[::-1]

        page_size = 10  # Number of rows per page
        page_number = 1
        paginated_rows = paginate_data(reversed_list, page_size, page_number)

        with open('message.csv' , 'r' ) as csvfile:
            data2 = csv.reader(csvfile)
            header2 = next(data2)
            list_data2 = list(data2)
            reversed_list2 = list_data2[::-1]
            ten_messages = paginate_data(reversed_list2, page_size, page_number)

        return render_template('admin.html' , data = paginated_rows,messages = ten_messages)
    return redirect('/admin_login')

# pagination logic
def paginate_data(data, page_size, page_number):
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    return data[start_index:end_index]

@app.route('/send_message' , methods = ['GET','POST'])
def send_message():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        save_message = {
            'name': name,
            'email':email,
            'message':message
        }
        with open('message.csv' , 'a' , newline='') as csvfile:
            fieldnames = ['name','email' , 'message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(save_message)
            flash('Message Send Successfully')
    return redirect('/')


@app.route('/admin_login' , methods = ['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['name']
        pwd = request.form['password']
        if username == 'admin' and pwd == 'admin':
            session['logged_in'] = True
            return redirect('/admin')
    return render_template('admin_login.html')

@app.route('/admin_logout' , methods = ['GET','POST'])
def admin_logout():
    session['logged_in'] = False
    return redirect('/')

@app.route('/download_csv' , methods = ['GET','POST'])
def download_csv():
    location = os.path.join(r'C:\Users\newar\OneDrive\Desktop\final Project')

    return send_from_directory(location,'answer.csv')

if __name__ == '__main__':
     app.run(host="0.0.0.0",port = 80, debug = True,threaded = True)