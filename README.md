# cardswipe

This program, when used with a card reader, can be used to log a list of who has swiped a card meeting a certain criteria. Cards which don't meet the criteria are rejected. If the card hasn't been seen before, the user is asked to enter their name. A hash of the contents of their card is stored along with their name in a csv file which serves as a "database". Then, if the card is swiped again, we can look up their name instead of asking the person to enter it again. The names of people who have swiped their card (and the time that they swiped it) are stored in another csv file (the "attendance" file) with the current date in the filename. If the program is run multiple times on the same day, subsequent card swipes will be appended to the current file.

The contents of the card are never stored to disk. A hash of the card's contents is stored to disk instead.

The name must also meet some criteria (no digits, some punctuation isn't allowed, must contain a space between first name and last name). The criteria on the name helps prevent a person from accidentally swiping their card at the "enter your name" prompt and having the card contents appear as their name.

To exit, press Ctrl+C or kill the program by closing the window. There is no risk of losing data based the program writes data to disk as soon as possible. The name is saved in the database file as soon as they type it in. Information is appended to the attendance file as soon as they swipe their card and the software knows the name to use.

This program is known to work with a card reader such as the Yosoo MSR90.
