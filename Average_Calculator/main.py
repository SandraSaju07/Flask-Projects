from flask import Flask,redirect,url_for,render_template,request

app = Flask(__name__)   # Creating WSGI Application

@app.route('/')
def marksheet():
    return render_template('index.html')

@app.route('/success/<int:score>')
def passed(score):
    Output = {"Score":score,"Result":"Passed"}
    return render_template('result.html',output=Output)

@app.route('/fail/<int:score>')
def failed(score):
    Output = {"Score":score,"Result":"Failed"}
    return render_template('result.html',output=Output)

@app.route('/submit',methods=['POST','GET'])
def submit():
    average,result = 0,""
    if request.method == 'POST':
        statistics = float(request.form['statistics'])
        maths = float(request.form['maths'])
        datascience = float(request.form['datascience'])
        python = float(request.form['python'])
        average += (statistics + maths + datascience + python) / 4
    if average >= 60:
        result = "passed"
    else:
        result = "failed"
    return redirect(url_for(result,score = average))

if __name__ == '__main__':
    app.run(debug=True)