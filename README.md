# Overview

This software scans bubble-sheets. It is aimed at people who are comfortable with Python and has been tested on Linux and MacOS.

# Usage

1. Print copies the provided bubble sheet PDF in the bubble-sheet subdirectory. Do not use a copying machine on the bubble sheet since scanning the original may result in all of the sheets to be inadvertently printed with the bubbles tilted on the page.

2. Create a bubble sheet key for each of the versions of the exam. The key you are using can be specified on the "key" field on the sheets. The key bubble sheet(s) should not have any name or username filled in. The software identifies the keys as blank names/usernames.

3. Create at least one test bubble sheet to ensure that the software is working correctly.

4. Scan the key(s) and the tests using a reasonable quality scanner into a single PDF. The bubble sheets must be scanned consistently. For example, if the pages are tilted, if the scanner crops pages differently, etc, the software may not work. When you flip through the pages in the PDF, all of the bubble sheets should line up fairly close.

5. Name your file bubblescan.pdf 

6. Run the bubblescan-extract.sh shell script. This will extract each page in the PDF into a TIFF file. For each page, it will create files such as bubblescan-0000.tif (scan of first page) and bubblescan-0000-thresh.tif (scan of first page but with the identified marks shown). It will also create avg.tif which is an image containing the average of all of the pages. The average image is created as quick way to get an idea of if all of your pages are aligned. It is also useful for if you have to make adjustments to the area that the software is looking for the bubbles.

7. The software will tell you how many questions were correct and assume that each question is worth one point. If you wish to assign exact point values to each question, edit the "points" array at the top of bubblescan.py.

8. Run "bubblescan.py" in the same directory as the extracted TIFF files. It will print information to the console and create a grades.csv file. If it doesn't work, see the "Troubleshooting" section below.

9. Cleanup: Run "rm bubblescan.tif avg.tif" to remove the temporary files TIFF files. Also consider removing bubblescan.pdf and grades.csv when you are finished.

10. Use the bubble sheets for a real exam!

# Troubleshooting

If the images are not being scanned properly, try the following:

* Copy an example PDF out of the examples folder, name it bubblescan.pdf, and see if that works.

* Ensure that the bubbles in the scanned PDFs are not tilted.

* Ensure the pages are aligned with each other. Look at the avg.tif file the extract step creates.

* Look at the thresholded TIFF files. If the black dots are not correct, bubblescan-extract.sh may need changes.

* Verify/update the pixel locations of the bubbles. To do this, follow the instructions at the top of bubblescan.py which describes changing the coordinates. In short, the software needs to know the pixel coordinate of the upper left and lower right corners around each of the 4 sets of bubbles (answers, username, last name, key).



# Installation

Python3 is required. bubblescan-extract.sh requires the ImageMagick command "convert" command and the bash shell. bubblescan.py requires Python 3 and the Python 3 ImageMagick Wand module.

## Ubuntu

    sudo apt install python3-wand imagemagick imagemagick-6

## MacOS

    brew install imagemagick@6
    pip install wand
    export MAGICK_HOME=/usr/local/Cellar/imagemagick@6/VERSION_NUMBER


