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


def playSoundFile(filename):
    """Try to play an audio file"""

    # Try to play wav file on windows.
    try:
        import winsound
        winsound.PlaySound(filename, winsound.SND_ASYNC|winsound.SND_NOSTOP)
        return
    except ImportError:
        pass

    # Should play wav files on mac or Linux
    import subprocess
    progs = [ "/usr/bin/afplay", "/usr/bin/play", "/usr/bin/ffplay", "/usr/bin/mplayer" ]

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
        

def hasNumbers(inputString):
    """Return true if string contains one or more digits"""
    return any(char.isdigit() for char in inputString)

def validCard(card):
    """Check if a card is 'valid'. If it is, return a hash of the card (we hash the card ourselves so we don't have to worry about storing whatever data is actually on the card. If the card is not valid, return None"""
    card = card.strip()
    #print("Card: "+card)
    #print("Card in hex: " + ":".join("{:02x}".format(ord(c)) for c in card))
    
    cardLen = len(card)

    if re.fullmatch(";.{16}=.{20}\?", card):
        return hashlib.sha1(card.encode("ascii")).hexdigest()
    else:
        return None

def validName(name):
    """Check if the name that the user typed in was valid. We apply this
check so that a person swiping their card two times in a row doesn't
have their card show up as their name accidentally."""
    if validCard(name):
        return False
    if ',' in name or "?" in name or "=" in name or ";" in name or "/" in name or "^" in name:
        return False
    if len(name) < 3:
        return False
    if " " not in name:
        return False
    if hasNumbers(name):
        return False
    
    return True


def waitForCard(attempts=0):
    """Prompt the user to swipe their card until we see a valid card."""
    if attempts == 0:
        for i in range(5):
            print()

    print("💳") # unicode card emoji
    card = getpass(prompt="Swipe card now:")
    card = card.strip()

    # On Linux, there is an issue where the first card swipe works
    # fine, then the second card swipe causes getpass() to only return
    # part of the card. Here, we wait until the correct number of
    # characters are present in the input. Note that if someone types
    # something on the keyboard and then swipes the card, that swipe
    # won't work. The next swipe should work, however.
    while len(card) < 39:
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
        print("ERROR: Invalid card. Swipe again. Use gold magnetic strip.")
        soundError()
        return waitForCard(attempts+1)

    return hashed


        
def waitForName():
    """Prompt the user to enter their name. Keep prompting until we consider their name to be valid."""
    soundEnterName()

    name = ""
    while not validName(name):
        name = ""
        print("🤔")
        print("Type name (of person who last swiped their card): ")
        while len(name) == 0:
            name = sys.stdin.readline()
            name = name.strip()
        if not validName(name):
            print("🚫") # prohibited emoji
            print("ERROR: Enter a valid first and last name (separated by a space). No punctuation or numbers.")
            soundError()


    return name

def writeDB(db):
    """Write a dictionary to our database file."""
    with open("swipe-db.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        for k, v in db.items():
            writer.writerow([v, k])


def readDB():
    """Read our database file to construct a dictionary. The hashes of the cards are the keys and the person's name is the value."""
    if not os.path.exists("swipe-db.csv"):
        return { }
    
    with open("swipe-db.csv", "r") as csvfile:
        rows = csv.reader(csvfile)
        if rows:
            db = { }
            for r in rows:
                db[r[1]] = r[0]
            return db
        return { }


db = readDB()
print("%d cards+names in swipe-db.csv" % len(db))

outputFilename = time.strftime('swipe-attend-%Y%m%d.csv')
if os.path.exists(outputFilename):
    print("Appending people to the end of %s (which already exists)" % outputFilename)
else:
    print("Storing people in %s" % outputFilename)
attendees = open(outputFilename, "a")

while 1:
    hex = waitForCard()

    # Add name to database if needed
    if hex not in db:
        print("Welcome new user.")
        name = waitForName()
        
        db[hex] = name
        writeDB(db)

    name = db[hex]

    # Add name into today's attendance
    attendees.write("%s,%s%s" % (name, time.strftime("%-I:%M:%S%p"), os.linesep))
    attendees.flush()
    print("👍") # thumbs up emoji
    print("%s, your attendance has been recorded." % name)
    soundSuccess()
