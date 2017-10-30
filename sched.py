#!/usr/bin/env python

"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import cookielib, urllib2, urllib, time, hashlib
from random import randrange
from bs4 import BeautifulSoup

#Login Credentials
#EDIT HERE
user = "1766385"
password = "Password1"
challengeQuestion1 = "What is your Mother's maiden name?"
challengeResponse1 = "ANSWER"
challengeQuestion2 = "What was your childhood pet's name?"
challengeResponse2 = "ANSWER"
challengeQuestion3 = "In what city were you born?"
challengeResponse3 = "ANSWER"
#END EDIT

cj = cookielib.CookieJar()
browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

#Fetch initial login page to set initial session cookies
browser.open("https://ltsrv.myloweslife.com/wfc/logonWithUID?ESS=true")

#Set Login Data
ssoPostData = urllib.urlencode({
"USER":user, 
"PASSWORD":password, 
"loginButton2":"Login", 
"smagentname":"sbCCIdBcl0La7HYJX0ciPcHOD2e2F3lvtg7KPJrbNFIw3MvNAeRG/YO03X+D16sI", 
"target":"https://ltsrv.myloweslife.com/wfc/logonWithUID?&TARGET=%26ESS%3Dtrue"
})

#Send login request
ssoResults = browser.open("https://lius.myloweslife.com/siteminderagent/forms/login_sso.fcc", ssoPostData)

challengeHTML = ssoResults.read()
challengeSoup = BeautifulSoup(challengeHTML)

#Find and store challenge token
challengeTokenAttribute = challengeSoup.find(attrs={"name":"ChallengeToken"})
challengeToken = challengeTokenAttribute['value']

#Find and store challenge question
challengeQuestionAttribute = challengeSoup.find(attrs={"align":"right"})
challengeQuestion = challengeQuestionAttribute.text
challengeQuestion = challengeQuestion.strip()

if challengeQuestion == challengeQuestion1:
	challengeResponse = challengeResponse1
if challengeQuestion == challengeQuestion2:
	challengeResponse = challengeResponse2
if challengeQuestion == challengeQuestion3:
	challengeResponse = challengeResponse3

challengePostData = urllib.urlencode({
"ChallengeToken":challengeToken, 
"LSACHALLENGETOKEN":"null", 
"RESPONSE":challengeQuestion + "|" + challengeResponse, 
"RESPONSE0":challengeResponse, 
"smagentname":"$SM$iPgFL0jsCR1TqDpWKAr9r3rnWM5UqRxbCoD9T2X/qegKsi/Qpwk/Oi2u1lXulYlk", 
"SMAUTHREASON":"27", 
"target":"$SM$HTTPS://lius.myloweslife.com/wamapps/disclaimers/wfcDisclaimer.jsp?ORIG_TRGT=https://ltsrv.myloweslife.com/wfc/applications/calendar/show.do?&calId=3&pid=715015&ts=1392785704284", 
"loginButton2":"Submit"
})

browser.open("https://lius.myloweslife.com/SmKBAuth/LoginEnrollmentForms/SmKBAuthChallenge.fcc", challengePostData)

disclaimerPostData = urllib.urlencode({
"DISCLAIMER_RESPONSE":"Yes", 
"loginButton1.x":str(randrange(3,86)), 
"loginButton1.y":str(randrange(2,25))
})

browser.open("https://lius.myloweslife.com/wamapps/disclaimers/wfcDisclaimer.jsp?ORIG_TRGT=https://ltsrv.myloweslife.com/wfc/applications/calendar/show.do?&calId=3&pid=715015&ts=1392785704284", 
disclaimerPostData)

calendarResults = browser.open("https://ltsrv.myloweslife.com/wfc/applications/calendar/show.do?calId=3&pid=715015&ts=1392785704284")

calendarHTML = calendarResults.read()
calendarSoup = BeautifulSoup(calendarHTML)

#Get Employee ID for Day Details
employeeID = calendarSoup.find(id="value(SelEmpId)")["value"]
employeeID

#Write iCalendar headers / time-zone
print """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Chris Perez//Kronos Sync//EN
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:America/Los_Angeles
X-LIC-LOCATION:America/Los_Angeles
BEGIN:DAYLIGHT
TZOFFSETFROM:-0800
TZOFFSETTO:-0700
TZNAME:PDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0700
TZOFFSETTO:-0800
TZNAME:PST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE"""

caltable1 = calendarSoup.find("table", class_="caltable1")

rows = caltable1.findAll('tr')
for row in rows:
	columns = row.find_all('td')
	for column in columns:

		#date is the only column with title attribute
		if column.has_attr('title'):

			date = column.get("title")

			#ftbold gets rid of "Late In", "Short Break", etc.
			divs = column.find_all("div", class_="ftbold")

			for div in divs:
				times = div.text

				#Fixes AM and PM
				times = times.replace("a"," am")
				times = times.replace("p"," pm")
				
				#Removes superfluous transfer notifier (now handled below)
				times = times.replace("(X)","")
				
				#Sets subject field with scheduled department
				dayDetailHTML = browser.open("https://ltsrv.myloweslife.com/wfc/applications/calendar/html/dayDetail.jsp?calId=3&id=0&empId="
				+ employeeID + "&selectedDates=" + date)
				dayDetailSoup = BeautifulSoup(dayDetailHTML)
				dayDetailDivs = dayDetailSoup.find_all("div", class_="caldayItem1")
				dayDetailDiv = dayDetailDivs[-1]
				dayDetailString = dayDetailDiv.text
				subject = dayDetailString.split("/")[-1]
				subject = subject.strip()
				
				#Separates Start Time and End Time
				startEndTime = times.split(" - ")
				startTime = startEndTime[0]
				endTime = startEndTime[1]
								

				#Remove problematic white space
				startTime = startTime .strip()
				endTime = endTime.strip()
				
				#Separate / Add minutes (e.g. :15, :30, :00) to start time
				if len(startTime) == 7:
					startTime = startTime[:2] + ":" + startTime[2:]
				elif len(startTime) == 6:
					startTime = startTime[:1] + ":" + startTime[1:]
				else:
					startTime = startTime.replace(" ", ":00 ")
		
				#Separate / Add minutes (e.g. :15, :30, :00) to end time
				if len(endTime) == 7:
					endTime = endTime[:2] + ":" + endTime[2:]
				elif len(endTime) == 6:
					endTime = endTime[:1] + ":" + endTime[1:]
				else:
					endTime = endTime.replace(" ", ":00 ")
				
				#Convert start and end times to python datetime tuples
				startTimeTuple = time.strptime(date + " " + startTime, "%m/%d/%Y %I:%M %p")
				endTimeTuple = time.strptime(date + " " + endTime, "%m/%d/%Y %I:%M %p")

				#Write iCalendar rows
				print "BEGIN:VEVENT"
				print "DTSTAMP:" + time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + "Z"
				print "DTSTART;TZID=America/Los_Angeles:" + time.strftime("%Y%m%dT%H%M%S", startTimeTuple)
				print "DTEND;TZID=America/Los_Angeles:" + time.strftime("%Y%m%dT%H%M%S", endTimeTuple)
				print "UID:" + hashlib.md5(date).hexdigest() + "@cf.ftp.sh" 
				print "SUMMARY:" + subject
				print "END:VEVENT"
print "END:VCALENDAR"
