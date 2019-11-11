from flask import Flask, render_template, request, url_for, send_file, session, redirect, escape
import matplotlib
import matplotlib.pyplot as plt
import os
from io import BytesIO
import numpy as np
import mysql.connector
PEOPLE_FOLDER='/home/sundesh/Desktop/dbms_project/'
GUEST = "guest12345678910"
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


@app.route("/form", methods=['GET','POST'])
def login():
	error = None

	if 'inputUsername' in session:
		return redirect(url_for('getHomepage'))

	if request.method == 'POST':
		if (request.form['btn']=="Login as guest"):
			session['inputUsername'] = GUEST
			return redirect(url_for('main'))
		elif (request.form['inputUsername'] and request.form['inputPassword']):
			print(request.form['inputUsername'])
			print(request.form['inputPassword'])
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
		else:
			error = "Empty Field"
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

	mydb.commit()
	return render_template('signup.html', error=error, success=success)

@app.route('/myprofile',methods=['GET','POST'])
def myprofile():
	if (session['inputUsername'])==GUEST:
		return render_template('homepage.html', myprofile_guest = "This feature is not available for guest user!")
	args=(session['inputUsername'],)
	cur.callproc('get_user_data',args)
	uname=session['inputUsername']
	name="1"
	email="s"
	phnno1=1
	phnno2="Not available"
	i=0
	for res in cur.stored_results():
		result = res.fetchall()
	for row in result:
		if i==1:
			phnno2=row[0]
		email=row[1]
		name=row[2]
		if i==0:
			phnno1=row[0]
		i=i+1
	return render_template('myprofile.html',uname=uname,name=name,email=email,phnno1=phnno1,phnno2=phnno2)


@app.route("/CourseFilter",methods=['GET','POST'])
def filterCourse():
	coursecode=request.form['course_selected']
	query="SELECT ArticlePage.Title, ArticlePage.Article_id from CourseMaterial inner join ArticlePage on ArticlePage.Article_id=CourseMaterial.Article_id where Course_code=%s;"
	cur.execute(query,[coursecode])
	data=cur.fetchall()
	cur.execute("select Description from Course where Course_code=%s",[coursecode])
	description=cur.fetchall()

	return render_template('CourseFilter.html',data=data,coursecode=coursecode,description=description[0][0])

@app.route("/TagFilter",methods=['GET','POST'])
def filterTag():
	tags=request.form.getlist('tag_selected')

	query="SELECT ArticlePage.Title,ArticlePage.Article_id,count(distinct TaggedTopics.Tag_id) C from TaggedTopics inner join ArticlePage on ArticlePage.Article_id=TaggedTopics.Article_id where Tag_id in (SELECT Tag.Tag_id from Tag inner join TaggedTopics on Tag.Tag_id=TaggedTopics.Tag_id where Tag.Name in ( "

	i=0
	string = []
	for tag in tags:
		if i==len(tags)-1:
			query = query + " %s "
		else:
			query = query + " %s, "
		i=i+1
		string.append(tag)
	query = query + ")) GROUP BY ArticlePage.Article_id HAVING C="+str(len(tags))+" ;"
	print(query)
	print(string)
	cur.execute(query,string)
	data=cur.fetchall()

	return render_template('TagFilter.html',data=data,tagsizezero = "This feature is not available for guest user!")


@app.route("/addArticle.html", methods = ['GET', 'POST'])
def addArticle():
	if (session['inputUsername'])==GUEST:
		return render_template('homepage.html', myprofile_guest = "This feature is not available for guest user!")

	if request.method == 'POST':
		inputTitle = request.form['inputTitle']
		inputCourse = request.form['inputCourse']
		inputTag = request.form.getlist('inputTag')
		inputCode = request.form['inputCode']

		args = (session['inputUsername'], )
		cur.callproc('get_email_from_username', args)
		for res in cur.stored_results():
			result = res.fetchall()
		print(result)
		cur.execute("INSERT INTO ArticlePage(Title, Creation_date, Contributor_email) VALUES (%s, %s, %s)", [inputTitle, "2019-01-01", result[0][0]])

		cur.callproc('get_max_article_id')

		for res in cur.stored_results():
			inputArticle_id = res.fetchall()
		print(inputCourse)
		if inputCourse!="select_course":
			cur.execute("INSERT INTO CourseMaterial VALUES (%s, %s)", [inputCourse, inputArticle_id[0][0]])

		if inputTag!="select_tags":
			for tags in inputTag:

				cur.callproc('get_tag_id_from_tag_name', (tags,))

				for res in cur.stored_results():
					inputTag_id = res.fetchall()

				print(tags, inputTag_id)

				cur.execute("INSERT INTO TaggedTopics VALUES (%s, %s)", [inputTag_id[0][0], inputArticle_id[0][0]])
		if inputTitle:
			mydb.commit()
		with open("./static/files/"+str(inputArticle_id[0][0])+".txt", "w") as text_file:
			print(inputCode, file=text_file)

		return redirect(url_for('addArticle'))

	return render_template('addArticle.html')

class Comment:
	"""docstring for Comment."""

	def __init__(self, id):
		self.id = id
		self.text = None
		self.children = []

		cur.execute("SELECT Description from Comment where Comment_id = %s;", [self.id])
		self.text = cur.fetchone()[0];

		cur.execute("SELECT Comment_id from CommentFor where CommentFor_id = %s;", [self.id])

		children = cur.fetchall();
		for child in children:
			self.children.append(Comment(child[0]))
	def __str__(self):
		return str(self.id)+str(self.text)+ str(self.children)

# print(Comment(100))


@app.route("/viewArticle.html",methods=['GET','POST'])
def viewArticle():
	data = None
	articleComments = None
	if request.method == 'POST':
		inputArticle_id = request.form['inputArticleTitle']
		with open ("./static/files/"+str(inputArticle_id)+".txt", "r") as text_file:
			data = text_file.read()

		print(inputArticle_id)
		cur.execute("SELECT Comment_id from ContainsComment where Article_id = %s;", [inputArticle_id])
		articleComments_id = cur.fetchall()
		articleComments = []
		for id in articleComments_id:
			articleComments.append(Comment(id[0]))


	print(len(articleComments))

	return render_template('viewArticle.html', data = data, comments = articleComments)


@app.route("/myArticleFilter.html",methods=['GET','POST'])
def myArticleFilter():

	args = (session['inputUsername'], )
	cur.callproc('get_email_from_username', args)
	for res in cur.stored_results():
		inputEmail = res.fetchall()
	inputEmail = inputEmail[0][0]
	query="SELECT ArticlePage.Title, ArticlePage.Article_id from ArticlePage where Contributor_email = %s"
	cur.execute(query,[inputEmail])
	data=cur.fetchall()
	print(data)
	print(session['inputUsername'])
	return render_template('myArticleFilter.html',data=data,inputUsername=session['inputUsername'])


# mydb.close()
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.run(debug=True)
