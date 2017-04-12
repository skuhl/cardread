# cardswipe

This program, when used with a card reader, can be used to log the usernames of people who have presented their card. Cards which don't meet the criteria hard-coded into the program are rejected. If the card hasn't been seen before, the user is asked to enter their username. A hash of the contents of their card is stored along with their name in a csv file which serves as a "database". Then, if the card is presented again, we can look up their username instead of asking the person to enter it. The usernames of people who have swiped their card (and the time that they swiped it) are stored in another csv file (the "attendance" file) with the current date in the filename. If the program is run multiple times on the same day, subsequent card swipes will be appended to the current file.

The contents of the card are never stored to disk. A hash of the card's contents is stored to disk instead.

The username must also meet some criteria (no digits, some punctuation isn't allowed). The criteria on the username prevents a person from accidentally having the contents of their card appear as their name (this mistake is easy to make since the card reader acts as a keyboard).

## Using the program
Run swipe.py with Python 3. On Linux or macOS, simply run "python3 swipe.py" on the command line. On Windows, double click swipe.py or run "python swipe.py" from the commandline (assuming Python 3 is installed and in your path).

To exit, press Ctrl+C or kill the program by closing the window. There is no risk of losing data because the program writes data to disk as soon as possible. The username is saved in the database file as soon as they type it in. Information is appended to the attendance file as soon as they present their card and the software knows the name to use.

This program is known to work with a card reader such as a Chafon 10-digit RFID card reader.
