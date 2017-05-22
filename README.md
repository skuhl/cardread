# cardread

This program, when used with a card reader, logs the usernames of people who have present their card. Cards which don't meet the criteria hard-coded into the program are rejected. If the card hasn't been seen before, the user is asked to enter their username. A hash of the contents of their card is stored along with their name in a csv file which serves as a "database". Then, if the card is presented again, we can look up their username instead of asking the person to enter it. The usernames of people who have presented their card (and the time that they presented it) are stored in another csv file (the "attendance" file) with the current date in the filename. The program never deletes the attendance file. If an existing attendance file is present, new records will be appended to it.

The contents of the card are never stored to disk. A hash of the card's contents is stored to disk instead.

The username must also meet some criteria (no digits, some punctuation isn't allowed). The criteria on the username prevents a person from accidentally having the contents of their card appear as their name (this mistake is easy to make since the card reader acts as a keyboard).

## Canvas integration
You may wish to use a 1 point Canvas assignment for each expected date of attendance. cardread integrates with Canvas and can automatically give 1 point to each person in attendance when they present their card. To do this, you will need to update several things at the top of the cardread.py program:

* canvasAPI - This is the URL where the Canvas API is available. By default, it is set appropriate for Michigan Tech.
* canvasToken - A string containing a token which you can generate on your profile page on the Canvas website.
* canvasCourseName - A string containing the course name of the canvas course.
* canvasAssignmentName - A string containing the exact name of the assignment which attendance grades should be updated.

When Canvas integration is enabled, if a user enters types their username incorrectly, it not enrolled in the class, or if your Internet connection drops, the person's attendance will still be logged in the local file on your disk, but it will not update the grade on Canvas. When this happens, the file stored on disk is annotated to make it clear which attendees did not have a grade on Canvas entered. Therefore, it is always recommended that you review the local attendance file on your disk to double-check that everybody was given credit on Canvas.

## Using the program
Run cardread.py with Python 3. On Linux or macOS, simply run "python3 cardread.py" on the command line. On Windows, double click cardread.py or run "python cardread.py" from the commandline (assuming Python 3 is installed and in your path).

To exit, press Ctrl+C or kill the program by closing the window. There is no risk of losing data because the program writes data to disk as soon as possible. The username is saved in the database file as soon as they type it in. Information is appended to the attendance file as soon as they present their card and the software knows the name to use.

This program is known to work with a card reader such as a Chafon 10-digit RFID card reader.
