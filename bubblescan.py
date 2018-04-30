#!/usr/bin/env python3

# Author: Scott Kuhl
from wand.image import Image
from wand.color import Color
import numpy as np
import glob


# === Coordinates ===
#
# Open avg.tif created by the extract script in an image editor which
# puts the 0,0 coordinate in the upper left corner of the image (such
# as GIMP). Then, imagine a grid being laid down that puts each bubble
# in its own cell. The first pair of numbers in these arrays is the
# position of the upper left corner of that grid (i.e., a point to the
# upper-left corner of the upper-left bubble). The second pair of
# numbers is the lower right corner of that grid (i.e., the
# lower-right corner of the lower-right bubble). The last two numbers
# are the number of columns in the grid and the number of rows in the
# grid.

#                upper left,  lower right, cols, rows
ansCoords =      [ 105, 68,   175, 703,    6,    50 ]
usernameCoords = [ 199, 151,  330, 605,    11,   26+10 ]
lastCoords =     [ 341, 151,  472, 479,    11,   26 ]
keyCoords =      [ 228, 99,   295, 112,    5,    1 ]


# === points ===
#
# How many points are each question worth? The length of this list
# only needs to match the length of the number of answers provided in
# the key.
points = [ 1 ] * 50  # make a list of 50 ones for an exam with 50 1pt questions with: [ 1 ] * 50


# === ignorePixels ===
#
# If this is set to 1, then a single black pixel
# in the thresholded image will be ignored. Also, two 50% gray pixels
# will be ignored (because the total darkness would sum to match a
# single pixel). Increase this number to prevent the software from
# detecting an occasional stray smudge as an answer. Decrease the
# value to detect faint smudges as answers. It is recommended that you
# set this to as small of a value as you can without incorrectly
# identifying smudges as answers.
#
# Note: If there are multiple bubbles marked for a single question, we
# use the one that sums to the darkest value. Therefore, if there is a
# good mark and a faint smudge for an alternative answer, this
# software will detect the good mark. This variable will impact
# questions where there is no answer and we read a smudge as an
# answer.
ignorePixels = 2.5




# Code follows. You should not need to make changes beyond this point.

class Exam:
    filename = None
    lastname = None
    username = None

    # A list of answers provided on the exam
    answers = None

    # Number of correct answers (ignoring point values)
    correctCount = 0
    # A list of the correct answers (to be compared with Exam.answers)
    correctAnswers = None

    totalPoints = 0

def pixel(image, x, y):
    return image[x][y];

def countWhite(image, minX,maxX,minY,maxY):
    Xr = range(minX, maxX+1)
    Yr = range(minY, maxY+1)
    count = 0;
    #print("counting %d %d %d %d" % (minX, maxX, minY, maxY))
    for x in Xr:
        for y in Yr:
            # negate pixel so filled in bubbles are bright.
            negatedPixel = 255-pixel(image,x,y)
            # Sum brightness of all pixels (gray pixels are added into sum).
            count = count+negatedPixel

    #print("returning %d" % count)
    #print(count)
    if count < 255*ignorePixels:
        return 0
    return count;

def layGrid(image, coord):
    """Given an image, the upper left corner, and lower left corner of an area on the image, the numbers of rows and columns in the area, return a 2D array showing how many white pixels are in the area."""

    upperLeftX = coord[0]
    upperLeftY = coord[1]
    lrX = coord[2]
    lrY = coord[3]
    cols = coord[4]
    rows = coord[5]
    
    # Calculate as float to prevent rounding errors in positioning of boxes
    boxWidth = (lrX-upperLeftX)/float(cols)
    boxHeight = (lrY-upperLeftY)/float(rows)
    grid = np.zeros((cols,rows), dtype='uint32')
    
    for r in range(rows):
        for c in range(cols):
            localULX=int(round(upperLeftX+c*boxWidth))
            localULY=int(round(upperLeftY+r*boxHeight))
            grid[c][r] = countWhite(image, localULX, localULX+int(round(boxWidth)), localULY, localULY+int(round(boxHeight)))
    return grid


def largestColsInGrid(grid):
    """Given a grid (2D array), in each row find the column with the largest value. This is useful when one question has multiple choices arranged in a row."""
    largestCol=[ -1 for i in range(grid.shape[1]) ]
    for r in range(grid.shape[1]):
        maxVal = 0
        for c in range(grid.shape[0]):
            if grid[c][r] > maxVal:
                maxVal = grid[c][r]
                largestCol[r] = c
    return largestCol

def largestRowsInGrid(grid):
    """Given a grid (2D array), in each column find the row with the largest value. This is useful when one question has multiple choices arranged in a column."""
    largestRow=[ -1 for i in range(grid.shape[0]) ]
    for c in range(grid.shape[0]):
        maxVal = 0
        for r in range(grid.shape[1]):
            if grid[c][r] > maxVal:
                maxVal = grid[c][r]
                largestRow[c] = r
    return largestRow


def indexToLetterNumber(i):
    if i<0:
        return " "
    if i >= 26 and i < 36:
        return str(i-26)
    else:
        return chr(i+65)



def readExam(filename):
    print("Processing %s" % filename)
    #tif = TIFF.open(filename, mode='r')
    #image = tif.read_image()
    
    image = Image(filename=filename)
    img_buffer=np.asarray(bytearray(image.make_blob(format='Gray')), dtype=np.uint8)
    img_buffer=np.reshape(img_buffer, (image.width, image.height), order='F')

    ex = Exam()
    ex.filename = filename

    # answers
    grid = layGrid(img_buffer, ansCoords)
    #print(grid)
    answers = largestColsInGrid(grid)
    #print(answers)
    ex.answers = answers

    # username
    grid = layGrid(img_buffer, usernameCoords)
    #print(grid)
    answers = largestRowsInGrid(grid)
    #print(answers)
    username = "" 
    for i in answers:
        username = username + indexToLetterNumber(i)
    ex.username = username.lower()

    # lastname
    grid = layGrid(img_buffer, lastCoords)
    #print(grid)
    answers = largestRowsInGrid(grid)
    #print(answers)
    lastname = ""
    for i in answers:
        lastname = lastname + indexToLetterNumber(i)
    ex.lastname = lastname.lower()

    # key
    grid = layGrid(img_buffer, keyCoords)
    answers = largestColsInGrid(grid)
    key = answers[0]+1   # first key is key 1
    ex.key = key
    
    return ex
    
def readExams(filenames):
    exams = []
    for i in filenames:
        exams.append(readExam(i))
    return exams

def sortExams(exams):
    """Find keys in the exam (a key will have no name and no username)"""
    keys = []
    others = []

    keyNums = []
    
    for e in exams:
        if len(e.lastname.strip()) == 0 and len(e.username.strip()) == 0:
            keys.append(e)
            keyNums.append(e.key)
        else:
            others.append(e)

    print("Found %d keys (%s) and %d submissions out of %d pages" % (len(keys), str(keyNums), len(others), len(exams)))
    return (keys, others)


def getKey(keys, requestedKey):
    for e in keys:
        if e.key == requestedKey:
            return e
    print("Failed to find requested key: " + str(requestedKey))
    return None

def gradeExams(keys, students):
    for e in students:
        sol = getKey(keys, e.key)
        if sol == None:
            print("Missing key %d for exam by %s %s" % (e.key, e.username, e.lastname))
            return
        e.totalPoints = 0
        e.correctCount = 0
        e.correctAnswers = sol.answers

        for i in range(len(sol.answers)):  # for each answer
            if sol.answers[i] != -1:       # is there an answer to this question?

                # verify answer has a corresponding point value.
                if i >= len(points):
                    print("Key %d has an answer for question %d---but you have no point value assigned to it in points array." % (e.key, i+1))
                    exit(1)

                # Check student's answer
                if sol.answers[i] == e.answers[i]:
                    e.correctCount = e.correctCount+1
                    e.totalPoints  = e.totalPoints + points[i]

def printExam(e, key=None):
    """Prints information about the exam to the console."""
    print("")
    print("%8s %11s - %3d points - %3d correct - key %d - %s" % (e.username, e.lastname, e.totalPoints, e.correctCount, e.key, e.filename))

    # Write 2 digit question number above questions
    for i in range(len(e.answers)):
        print("%-2d " % ((i+1)%100), end="")
    print("")

    for i in range(len(e.answers)):
        print("%s  " % indexToLetterNumber(e.answers[i]).lower(), end='')
        
    print("")
        
    if e.correctAnswers:
        for i in range(len(e.answers)):
            print("%s  " % indexToLetterNumber(e.correctAnswers[i]).lower(), end='')
        print("<--KEY")
        for i in range(len(e.answers)):
            if e.correctAnswers[i] >= 0 and e.correctAnswers[i] != e.answers[i]:
                print("X  ", end="")
            else:
                print("   ", end="")
        print("<--WRONG")
                
            
    

                    
inputFiles = glob.glob('bubblescan-????-thresh.tif')
inputFiles.sort()
exams = readExams(inputFiles)

#for e in exams:
#    printExam(e)


(keys, students) = sortExams(exams)

print("")
print("====== Keys ======")
# Sort keys before printing
keys.sort(key=lambda e: e.key, reverse=False)  # sort by key number
for e in keys:
    printExam(e)


gradeExams(keys, students)


print("")   
print("====== Submissions ======")
students.sort(key=lambda e: e.lastname, reverse=False)  # sort by last name
#students.sort(key=lambda e: e.key, reverse=False)  # sort by key
#students.sort(key=lambda e: e.username, reverse=False)  # sort by key
#students.sort(key=lambda e: e.totalPoints, reverse=False)  # sort by key
for e in students:
    printExam(e)



# ---- PRINT SUMMARY ----
print("")
print("====== Summary ======")

def percent(points, total):
    pcnt = 0
    denom = float(total)
    if denom > 0:
        pcnt = points/denom*100
    return pcnt


print("%-11s %-11s %3s %5s %3s %3s %s" % ("username", "lastname", "pts", "pcnt", "#c", "key", "filename"))
for e in students:
    print("%11s %11s %3d %5.1f %3d %1d %s" % (e.username, e.lastname, e.totalPoints, percent(e.totalPoints, sum(points)), e.correctCount, e.key, e.filename))

# ---- WRITE FILE ----
    
with open("grades.csv", 'w') as f:
    f.write("%s,%s,%s,%s,%s,%s,%s\n" % ("username", "lastname", "points", "percent", "num correct questions", "key", "filename"))
    for e in students:
        f.write("%s,%s,%d,%f,%d,%d,%s\n" % (e.username, e.lastname, e.totalPoints, percent(e.totalPoints, sum(points)), e.correctCount, e.key, e.filename))

print("Total points possible: %d" % sum(points))        
print("Wrote grades.csv")
