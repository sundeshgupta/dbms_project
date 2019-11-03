from flask import Flask, render_template, request, url_for, send_file, session, redirect, escape
import matplotlib
import matplotlib.pyplot as plt
import os
from io import BytesIO
import numpy as np
import mysql.connector
PEOPLE_FOLDER='/home/sundesh/Desktop/dbms_project/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER']=PEOPLE_FOLDER


mydb = mysql.connector.connect(host="localhost", user="aniket", password="pass", database = "dbms_project")

cur = mydb.cursor()

@app.route('/')
def main():
	if 'inputUsername' in session:
		username_session = escape(session['inputUsername']).capitalize()
		return render_template('homepage.html', session_user_name=username_session)
	return redirect(url_for('login'))


@app.route("/form", methods=['GET','POST'])
def login():
	error = None

	if 'inputUsername' in session:
		return redirect(url_for('getHomepage'))

	if request.method == 'POST':
		username_form  = request.form['inputUsername']
		password_form  = request.form['inputPassword']
		cur.execute("SELECT COUNT(1) FROM check_login WHERE username = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
		if cur.fetchone()[0]:
			cur.execute("SELECT password FROM check_login WHERE username = %s;", [username_form]) # FETCH THE HASHED PASSWORD
			for row in cur.fetchall():
				if password_form == row[0]:
					session['inputUsername'] = request.form['inputUsername']
					return redirect(url_for('main'))
				else:
					error = "Invalid Credential"
		else:
			error = "Invalid Credential"
	return render_template('form.html', error=error)

@app.route("/homepage", methods=['GET','POST'])
def getHomepage():
	return(render_template('homepage.html'))

@app.route('/logout')
def logout():
    session.pop('inputUsername', None)
    return redirect(url_for('main'))

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.run(debug=True)
