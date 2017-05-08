#/usr/bin/env python3
# Author: Scott Kuhl
import sys
import re
import hashlib
import csv
import os
import time

# Read card without echoing input to terminal
from getpass import getpass

filenameDB = "swipe-db.csv"
canvasAPI = "https://mtu.instructure.com/api/v1/"
canvasToken = None
canvasCourseName = None
canvasAssignmentName = None


def playSoundFile(filename):
    """Try to play an audio file"""

    # Try to play wav file on windows.
    try:
        import winsound
        winsound.PlaySound(filename, winsound.SND_ASYNC)
        return
    except ImportError:
        pass

    # Should play wav files on mac or Linux
    import subprocess
    # afplay - macOS
    # aplay - Linux (part of ALSA)
    # play - Linux (part of sox)
    # mplayer - Linux (common media player)
    progs = [ "/usr/bin/afplay", "/usr/bin/aplay", "/usr/bin/play", "/usr/bin/mplayer" ]

    for prog in progs:
        if os.path.exists(prog):
            # Don't print stuff to stdout or stderr
            FNULL = open(os.devnull, 'w')
            subprocess.Popen([prog, filename], stdout=FNULL, stderr=FNULL)
            return

def soundSuccess():
    playSoundFile("swipe-success.wav")
    
def soundError():
    playSoundFile("swipe-error.wav")

def soundEnterName():
    playSoundFile("swipe-boing.wav")
        

def validCard(card):
    """Check if a card is 'valid'. If it is, return a hash of the card (we hash the card ourselves so we don't have to worry about storing whatever data is actually on the card). If the card is not valid, return None"""
    card = card.strip()
    #print("Card: "+card)
    #print("Card in hex: " + ":".join("{:02x}".format(ord(c)) for c in card))
    
    if re.fullmatch("[0-9]{10}", card):
        return hashlib.sha1(card.encode("ascii")).hexdigest()
    else:
        return None

def validUsername(name):
    """Check if the name that the user typed in was valid. We apply this
check so that a person swiping their card two times in a row doesn't
have their card show up as their name accidentally."""
    if validCard(name):
        return False
    if ',' in name or "?" in name or "=" in name or ";" in name or "/" in name or "^" in name or '"' in name or '@' in name:
        return False
    if len(name) < 3:
        return False
    if " " in name:
        return False
    
    return True


def waitForCard(attempts=0):
    """Prompt the user to wave their card and wait until we see a valid card."""
    if attempts == 0:
        for i in range(5):
            print()

    print("💳") # unicode card emoji
    card = getpass(prompt="Wave card now:")
    card = card.strip()

    # On Linux, there is an issue where the first card read works
    # fine, then the second card read causes getpass() to only return
    # part of the card. Here, we wait until the correct number of
    # characters are present in the input. Note that if someone types
    # something on the keyboard and then uses the card, it won't work.
    # The next time the card is used, it should work.
    while len(card) < 10:
        card = card + getpass(prompt="")
        card = card.strip()

    # Check if card is valid, get a hash of card so we don't have to
    # worry about saving the card data directly.
    hashed = validCard(card)

    # Drop the raw data of the card, we don't need it and don't want
    # it anymore.
    del card


    if hashed == None:
        print("🚫") # prohibited emoji
        print("ERROR: Invalid card. Try again.")
        soundError()
        return waitForCard(attempts+1)

    return hashed


        
def waitForName():
    """Prompt the user to enter their name. Keep prompting until we consider their name to be valid."""
    soundEnterName()

    name = ""
    while not validUsername(name):
        name = ""
        print("🤔")
        print("Type the username of the person who last swiped their card: ")
        while len(name) == 0:
            name = sys.stdin.readline()
            name = name.strip()
        name = name.lower()  # lowercase the username
        if not validUsername(name):
            print("🚫") # prohibited emoji
            print("ERROR: Enter a valid username. No punctuation.")
            soundError()


    return name

def writeDB(db):
    """Write a dictionary to our database file."""
    with open(filenameDB, "w") as csvfile:
        writer = csv.writer(csvfile)
        for k, v in db.items():
            writer.writerow([v, k])


def readDB():
    """Read our database file to construct a dictionary. The hashes of the cards are the keys and the person's name is the value."""
    if not os.path.exists(filenameDB):
        return { }
    
    with open(filenameDB, "r") as csvfile:
        rows = csv.reader(csvfile)
        if rows:
            db = { }
            for r in rows:
                if len(r)==2 and isinstance(r[0],str) and isinstance(r[1],str):
                    db[r[1]] = r[0]
            return db
        return { }


# Read existing database if it exists.
db = readDB()
print("%d cards+names in %s" % (len(db), filenameDB))

# Create a new file to store attendees in. If file exists, append to existing file.
outputFilename = time.strftime('swipe-attend-%Y%m%d.csv')
if os.path.exists(outputFilename):
    print("Appending people to the end of %s (which already exists)" % outputFilename)
else:
    print("Storing people in %s" % outputFilename)
attendees = open(outputFilename, "a")


canvasIntegrationWorks = False
try:
    print("")
    print("Verifying that Canvas integration works...")
    
    if canvasToken and canvasAPI and canvasCourseName:
        import canvas
        c = canvas.canvas(token=canvasToken, api=canvasAPI)
        courses = c.getCourses()
        courseId = c.findCourseId(courses, canvasCourseName)
        if courseId:
            print("Found course on Canvas: %s" % canvasCourseName)
        else:
            print("Can't find course '%s' on Canvas." % canvasCourseName)
        
        c.setDefaultCourseId(courseId)
        assignments = c.getAssignments()
        students = c.getStudents()
        assignmentId = c.findAssignmentId(assignments, canvasAssignmentName)
        if assignmentId:
            print("Found assignment on Canvas: %s" % canvasAssignmentName)
            canvasIntegrationWorks = True
        else:
            print("Can't find assignment '%s' in Canvas course." % canvasAssignmentName)


except:
    pass

if canvasIntegrationWorks == False:
    print("Canvas integration failed. Program will still log attendance to file (but not on Canvas). Any errors immediately above this message are OK.")



# Main program loop.
while 1:
    hashed = waitForCard()

    # Add name to database if needed
    if hashed not in db:
        print("Welcome new user.")
        name = waitForName()

        # Add user to database and write it to disk.
        db[hashed] = name
        writeDB(db)

    # Retrieve name from database
    name = db[hashed]

    # Add name into today's attendance file. Name in first column, date and time in second column.
    loggedTime = time.strftime("%X")
    attendees.write("%s,%s\n" % (name, loggedTime))
    attendees.flush()

    if canvasIntegrationWorks:
        try:
            studentId = c.findStudentId(students, name)
            if studentId:
                c.gradeSubmission(courseId=courseId, assignmentId=assignmentId, studentId=studentId, grade=1)
                # c.commentOnSubmission(courseId=courseId, assignmentId=assignmentId, studentId=studentId, comment="Our card reader software automatically marked you as present because you presented your card to me.")
            else:
                print("WARNING: We can't find you on Canvas. We have still logged your attendance into the file.")
                
        except:
            print("WARNING: Something went wrong when we tried to log on Canvas that '%s' was present" % name)
            pass
            
    print("👍") # thumbs up emoji
    print("%s, your attendance has been recorded." % name)
    soundSuccess()
