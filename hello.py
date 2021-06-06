from flask import Flask, request, jsonify, abort, redirect, url_for, render_template, send_file
from flask.json import jsonify
from markupsafe import escape
import statistics
import joblib
import numpy as np
import pandas as pd

# model load
knn = joblib.load('knn.joblib')
# container app instance
app = Flask(__name__)

# returns specified надпись on the creen
@app.route("/")
def hello_world():
    print(3*3)
    return "<h1>Hello, my amazing sexy Serj!<h1>"

#ф-я, показывающая введенное имя
@app.route('/user/<username>') 
def show_user_profile(username):
    username = int(username) * int(username)
    # show the user profile for that user
    return f'User {escape(username)}'

#ф-ия при вводе /avg/числа_чз_запятую счиатющая их mean
@app.route('/avg/<nums>') 
def avg(nums):
    nums = nums.split(',')
    nums = [float(num) for num in nums]
    nums_mean = statistics.mean(nums)
    print(nums_mean)
    return str(nums_mean)

#knn ml model function
def knn_ml(input):
    params = input.split(',')
    params = [float(param) for param in params] 

    params = np.array(params).reshape(1, -1)
    predict = knn.predict(params)
    return predict

#ф-ия для определения типа цветка
@app.route('/iris/<params>') 
def iris(params):

    predict = knn_ml(params)

    #flowers = {'Setosa': 1, 'Versicolor': 2, 'Virginica': 3}
    if predict == 1:
        return '<img src="https://upload.wikimedia.org/wikipedia/commons/5/56/Kosaciec_szczecinkowaty_Iris_setosa.jpg" width="400" height="500" alt="Setosa">'
    elif predict == 2:
        return '<img src="https://upload.wikimedia.org/wikipedia/commons/4/41/Iris_versicolor_3.jpg" width="400" height="500" alt="Versicolor">'
    else:
        return '<img src="https://upload.wikimedia.org/wikipedia/commons/9/9f/Iris_virginica.jpg" width="400" height="500" alt="Virginica">'


#ф-ия для показа картинки угаданного цветка с сайта
@app.route('/show_image') 
def show_image():
    return '<img src="static/setosa.jpg" width="400" height="500" alt="Setosa">'

# сообщение о неправильном вводе, используется в redirect(url_for('bad_request')
@app.route('/badrequest400') 
def bad_request():
    return abort(400)

#читаем json с вебсайта и возвращаем его контент
# подзапрос, позволяющей другой машине подключиться к моему серверу
@app.route('/iris_post', methods=['POST'])
def add_message():
    content = request.get_json()
    print(content)
    # applying our ml function to json the file input
    try:
        predict = knn_ml(content['flower'])
        predict = {'class':str(predict[0])}
    except:
        return redirect(url_for('bad_request')) #перенаправляем при ошибке на новый урл, связь c функ-й def bad_request()

    return jsonify(predict)


#создаем форму для заполнения на фласк

from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os

# сделаем сикрет ки для фласк
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

# класс с эл-ами, которые предстают на главном экране
class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()]) #эл-т ввода Имени в окошко
    file = FileField() #эл-т загрузки формы
# аппликейшен формы 
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    form = MyForm()
    if form.validate_on_submit():

        f = form.file.data # var containing uploaded file
        filename = form.name.data + '.csv' # можно вложить файл с любым расширением
        # f.save(os.path.join( # сохраняет вложенную форму в папку проекта с введенным именем
        #     filename
        # ))
        df = pd.read_csv(f, header=None)
        print(df.head())

        predict = knn_ml(df)
        result = pd.DataFrame(predict)
        result.to_csv(filename, index=False)

        return send_file(filename, mimetype='text/csv', attachment_filename=filename, as_attachment=True)
    return render_template('submit.html', form=form)

# an app for uploading files
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename + 'uploaded')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'file uploaded'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''