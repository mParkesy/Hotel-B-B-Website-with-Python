from flask import Flask, render_template, request, redirect, session
from time import time
from calendar import monthrange
import calendar
import os
import csv
import time
import smtplib
from flask import request
import jinja2
env = jinja2.Environment()
env.globals.update(zip=zip)

app = Flask(__name__)

# set homepage
@app.route('/')
def index():
	return render_template('index.html', title='Home')

# set where page 
@app.route('/where')
def where():
	return render_template('where.html', title='Where to find us')
	
# set places to go page
@app.route('/places')
def places():
	return render_template('places.html', title='Places to go')

# set about kingsbridge page
@app.route('/kingsbridge')
def kingsbridge():
	return render_template('kingsbridge.html', title='About Kingsbridge')	
	
# set booking page
@app.route('/booking')
def booking():
	# csv path
	bookingFile = 'static\\booking.csv'
	# get form data
	currentMonth = int(request.args.get('month'))
	year = int(request.args.get('year'))
	daysInMonth = monthrange(year, currentMonth)[1]
	# arrays to hold data
	days = []
	months = []
	years = []
	length = []
	
	if os.path.getsize(bookingFile) > 0:
		dateList = readCol(bookingFile,6)
		lengthList = readCol(bookingFile,7)	
		for line in dateList:
			#appends csv data to lists
			days.append(int(line[9:11]))
			months.append(int(line[5:7]))
			years.append(int(line[0:4]))
		for line in lengthList:
			length.append(int(line))
		return render_template('booking.html', title= 'Booking', days=daysInMonth, dates=days,
		lengths=length, cal_title=calendar.month_name[currentMonth] + " - " + str(year), monthList = months, monthArg = currentMonth, yearsList = years)		
	else:
		return render_template('booking.html', title=calendar.month_name[month])
	
# add booking from form to csv
@app.route('/makeBooking', methods=['POST'])
def makeBooking():
	# file path
	bookingFile = 'static\\booking.csv'
	#read list from csv
	bookingList = readFile(bookingFile)
	
	#get form content
	firstname = request.form['firstname']
	lastname = request.form['lastname']
	email = request.form['email']
	number =  '0' + request.form['number']
	adultsNum = request.form['adultsNum']
	childrenNum = request.form['childrenNum']
	arrival = request.form['arrival']
	length = request.form['length']
	
	#fill with form content and make last column 0
	newBooking = [firstname, lastname, email, number, adultsNum, childrenNum, arrival, length, '0']
	# append to list
	bookingList.append(newBooking)
	#write to file
	writeFile(bookingList, bookingFile)
	
	# concatenate name
	name = firstname + ' ' + lastname
	# msg to be sent
	msg = 'A booking has been made on the Wildland Cottage Website' + '\nName:  ' + name + '\nEmail: ' +email + '\nPhone Number: ' + number + '\nNumber of Adults: ' + adultsNum + '\nNumber of Children: ' + childrenNum + '\nArrival Date: ' + arrival + '\nLength of stay: ' + length
	# send email
	sendEmail(name, 'cmptest2016@gmail.com', msg)
	
	return redirect('/')

# confirm a booking
@app.route('/confirmBooking', methods=['POST'])
def confirmBooking():

	#get form content
	lineNum = int(request.form['line'])
	bookingFile = 'static\\booking.csv'
	bookingList = readFile(bookingFile)
	# make a certain lines element equal to one
	bookingList[lineNum][8] = '1'
	# write to file
	writeFile(bookingList, bookingFile)
	# get name and email
	name = bookingList[lineNum][0] + ' ' + bookingList[lineNum][1]
	email = bookingList[lineNum][2]
	# message to be emailed
	msg = 'Hello, ' + name + '\n\n' + "Your recent booking for Wildland Cottage has been confirmed. If you'd like to get in contact with us then please see our contact page: http://127.0.0.1:5000/contact " + '\n\n' + 'King Regards,' + '\n\n' + 'The Wildland Cottage Team'
	# send email
	sendEmail(name, email, msg)
		
	return redirect('admin')

# set gallery page	
@app.route('/gallery')
def gallery():
	return render_template('gallery.html', title="Gallery")

# set reviews page
@app.route('/reviews')
def reviews():
	# file path
	reviewsFile = 'static\\reviews.csv'
	# read file into list
	reviewsList= readFile(reviewsFile)
	# send reviews to page
	return render_template('reviews.html', title="Reviews", reviewsList=reviewsList)
	
# add an entry
@app.route('/addEntry', methods=['POST'])
def addEntry():
#add review to csv
	#store path	
	reviewsFile = 'static\\reviews.csv'
	reviewsList= readFile(reviewsFile)
	#get form details
	name = request.form['name']
	review = request.form['text']
	todayDate = time.strftime("%d/%m/%Y")
	# if clear is entered then make list equal to nothing
	if name == 'clear' and review == 'clear':
		reviewsList = ''
	else:
		#concatenate and add to list of lists
		newEntry = [review, name, todayDate]
		reviewsList.append(newEntry)
	# write to file
	writeFile(reviewsList, reviewsFile)
	return redirect('reviews')

# read a certain column of a file
def readCol(aFile,col):
	with open(aFile, 'r') as inFile:
		reader = csv.reader(inFile)
		reviewsList = [row[col] for row in reader]
	return reviewsList	

# set content page
@app.route('/contact')
def contact():
	return render_template('contact.html', title='Contact')	
	
# contact form submit	
@app.route('/contactForm', methods=['POST'])
def contactForm():
	# get form data
	name = request.form['name']
	email = request.form['email']
	message = request.form['message']
	# message to be emailed 
	msg = 'You have been contacted by - ' + name + '\n\n' + 'There email address is: ' + email + '\n\n' + str(message)
	# send email
	sendEmail(name, 'cmptest2016@gmail.com', msg)
	
	return render_template('contact.html', title='Contact')				
		
# send email function		
def sendEmail(name, to, msg):	
	# open email account
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.ehlo()
	# email account details
	gmail_user = 'cmptest2016@gmail.com'
	password = 'UEAiswonderful'
	# login and send email
	server.login(gmail_user, password)
	server.sendmail(gmail_user, to, msg)
	server.quit()

# read file function
def readFile(aFile):
#read in 'aFile'
	with open(aFile, 'r') as inFile:
		reader = csv.reader(inFile)
		reviewsList = [row for row in reader]
	return reviewsList	

# write to a file function
def writeFile(aList, aFile):
#write 'aList' to 'aFile'
	with open(aFile, 'w', newline='') as outFile:
		writer = csv.writer(outFile)
		writer.writerows(aList)
	return	
	
# login form
@app.route('/login', methods=['POST'])	
def login():
	# get form data
	username = request.form['username']
	password = request.form['password']
	# if admin details are correct then create a session
	if username == "admin" and password == "wildland123":
		session['username'] = username
	return redirect('admin')
	
# set admin page
@app.route('/admin')
def admin():
	# get path
	bookingFile = 'static\\booking.csv'
	# write file to list
	bookingList = readFile(bookingFile)
	return render_template('admin.html', title='Admin Page', bookingList=bookingList)	
	
@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return render_template('index.html', title="Home")
		
if __name__ == "__main__":
	# secret key for sessions
	app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
	app.run(debug = True)

	