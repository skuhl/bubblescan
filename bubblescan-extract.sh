#!/usr/bin/env bash


# Takes a filename as a parameter and echo's the parameter without a filename extension.
function remove_file_exten() {
	EXTEN=`echo "${1}" | awk -F . '{print $NF}'`
	echo "${1/%.${EXTEN}/}"
}




if [[ ! -e bubblescan.pdf ]]; then
	echo "Expecting file 'bubblescan.pdf' containing keys and students sheets"
	exit
fi

echo "Exploding pdf"
convert bubblescan.pdf -colorspace Gray -depth 8 bubblescan-%04d.tif

echo "Averaging (useful for finding grid bounds)"
convert -background transparent bubblescan-????.tif -average avg.tif

for i in bubblescan-????.tif; do
	echo "Thresholding $i"

	base=`remove_file_exten "$i"`
	
	# 1. Normalize image so dark areas become black.
	#
	# 2. Apply a median filter to cut down noise. (Try adjusting
	# size). This step removes most of the blank bubbles.
	#
	# 3. Convolve a circle with the image. (Try adjusting size---it is
	# the radius of the circle in pixels.)  This step removes any
	# remaining noise.
	#
	# 4. Normalize the result.
	#
	# Note: Tiny, single pixel black spots or very light smudges over
	# a tiny area will be ignored. But, basically most smudges you see
	# in the output thresholded image will be considered as marks. See
	# countPixels() function in bubblescan.py for what it is configured
	# to ignore.
	convert "$i" -normalize -statistic Median 4x4 -morphology Correlate Disk:3.3 -normalize "$base-thresh.tif"

done
