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
		username_session = escape(session['inputUsername'])
		return render_template('homepage.html', session_user_name=username_session)
	return redirect(url_for('login'))

@app.route('/myprofile',methods=['GET','POST'])
def myprofile():
	print(session['inputUsername'])
	args=[session['inputUsername']]
	query="SELECT PhoneNoDetails.Phone_no,T.Email_add,T.uname from PhoneNoDetails inner join (SELECT Login.Email as Email_add,User.Name as uname from Login inner join User on User.Email=Login.Email where Login.Username=\"args[0]\") T on Email_add=Email;"
	cur.execute(query)
	#cur.callproc('get_user_data',args)
	name=1
	email=1
	phnno1=1
	phnno2="Not available"
	i=0
	data=cur.fetchall()
	for row in data:
		print(row[0])
		if i==1:
			phnno2=row[2]
		name=row[0]
		email=row[1]
		if i==0:
			phnno1=row[2]
		i=i+1	

	return render_template('myprofile.html',name=name,email=email,phnno1=phnno1,phnno2=phnno2)


@app.route("/form", methods=['GET','POST'])
def login():
	error = None

	if 'inputUsername' in session:
		return redirect(url_for('getHomepage'))

	if request.method == 'POST':
		username_form  = request.form['inputUsername']
		password_form  = request.form['inputPassword']
		cur.execute("SELECT COUNT(1) FROM Login WHERE Username = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
		if cur.fetchone()[0]:
			cur.execute("SELECT Password FROM Login WHERE Username = %s;", [username_form]) # FETCH THE HASHED PASSWORD
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

@app.route("/signup", methods = ['GET', 'POST'])
def signup():

	error = []
	success = None

	if request.method == 'POST':
		name_form = request.form['inputName']
		email_form  = request.form['inputEmail']
		username_form  = request.form['inputUsername']
		password_form  = request.form['inputPassword']
		password2_form  = request.form['inputPassword2']
		phonenumber1_form  = request.form['inputPhonenumber1']

		phonenumber2_form  = None
		flag  = int(0)
		if (request.form['inputPhonenumber2']):
			phonenumber2_form = request.form['inputPhonenumber2']

		if password_form!=password2_form:
			error.append("Passwords do not match")
			flag = 1
		cur.execute("SELECT COUNT(1) FROM Login WHERE Username = %s;", [username_form]) # CHECKS IF USERNAME EXSIST

		if cur.fetchone()[0]:
			error.append("Username already exists")
			flag = 1

		cur.execute("SELECT COUNT(1) FROM Login WHERE Email = %s;", [email_form]) # CHECKS IF USERNAME EXSIST

		if cur.fetchone()[0]:
			error.append("Email already exists")
			flag = 1

		if phonenumber2_form is not None:
			if phonenumber1_form==phonenumber2_form:
				error.append("Phone numbers are same.")
				flag = 1

		if not flag:
			cur.execute("INSERT INTO User VALUES (%s,%s,%s)", [email_form, name_form, '0'])
			cur.execute("INSERT INTO Login VALUES (%s, %s, %s)", [email_form, password_form, username_form])

			cur.execute("INSERT INTO PhoneNoDetails VALUES (%s,%s)", [email_form, phonenumber1_form])

			if phonenumber2_form is not None:
				cur.execute("INSERT INTO PhoneNoDetails VALUES (%s,%s)", [email_form, phonenumber2_form])

			success = "Signup successfull. Please go to login page."

	print(error)
	print(success)
	mydb.commit()
	return render_template('signup.html', error=error, success=success)


# mydb.close()
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.run(debug=True)
