#!/usr/bin/env python3
#from libtiff import TIFF
from wand.image import Image
from wand.color import Color
import numpy as np
import glob

# How many points are each question worth?  Initialize this list to
# zeros to force user to notice that they should fill it in. The
# length of this list only needs to match the length of the number of
# answers provided in the key.
points = [ 0 ] * 50


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
    if count < 255*1.5:  # if sum shows less than 1.5 fully lit pixels, ignore.
        return 0
    return count;

def layGrid(image, upperLeftX, upperLeftY, lrX, lrY, cols, rows):
    """Given an image, the upper left corner, and lower left corner of an area on the image, the numbers of rows and columns in the area, return a 2D array showing how many white pixels are in the area."""

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
    grid = layGrid(img_buffer, 97, 59, 170, 716, 6, 50)
    #print(grid)
    answers = largestColsInGrid(grid)
    #print(answers)
    ex.answers = answers

    # email
    grid = layGrid(img_buffer, 194, 149, 329, 619, 11, 26+10)
    #print(grid)
    answers = largestRowsInGrid(grid)
    #print(answers)
    username = "" 
    for i in answers:
        username = username + indexToLetterNumber(i)
    ex.username = username.lower()

    # lastname
    grid = layGrid(img_buffer, 348, 150, 482, 489, 11, 26)
    #print(grid)
    answers = largestRowsInGrid(grid)
    #print(answers)
    lastname = ""
    for i in answers:
        lastname = lastname + indexToLetterNumber(i)
    ex.lastname = lastname.lower()

    # key
    grid = layGrid(img_buffer, 226, 89, 293, 101, 5, 1)
    answers = largestColsInGrid(grid)
    key = answers[0]+1
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
        for i in range(len(sol.answers)):
            if sol.answers[i] != -1:
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
    
    for a in e.answers:
        print("%s  " % indexToLetterNumber(a).lower(), end='')
    print("")
        
    if e.correctAnswers:
        for a in e.correctAnswers:
            print("%s  " % indexToLetterNumber(a).lower(), end='')
        print("<--KEY")

                    
inputFiles = glob.glob('bubblescan-????-thresh.tif')
inputFiles.sort()
exams = readExams(inputFiles)

#for e in exams:
#    printExam(e)


(keys, students) = sortExams(exams)
gradeExams(keys, students)


# ---- PRINT LONG FORM VERSION ----

print("")
print("====== Keys ======")
# Sort keys before printing
students.sort(key=lambda e: e.key, reverse=False)  # sort by key number
for e in keys:
    printExam(e)


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
        pcnt = total/denom*100
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
