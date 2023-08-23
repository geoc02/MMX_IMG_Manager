"""
Description
-----------
This script/module parses the pdf given as a parameter and extracts slide number and associated GeL participant_id to 'output.csv'
Output will be redirected to database table, once we set the system up.
Input will be modified to S3 or Sharepoint location, once that's specified. 
 
Usage
-----
-h, --help : Select for help page.
-d, --pdf  : PDF to parse.
 
...
"""

import pandas as pd
import csv
import argparse
import src.pdf_manifest_processor as pmp


msg = "Hello MMX_IMG_Manager"
print(msg)

# Image load
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--pdf", required=True, help="path to input pdf")
args = vars(ap.parse_args())

results = pmp.parse_pdf(args['pdf'])

SlideNumbers = pmp.extract_slide_numbers(results[1])
ThumbnailStrings = pmp.extract_slide_info_image(results[0])
ThumbnailIDs = pmp.extract_IDs(ThumbnailStrings, 'RW3')

print(ThumbnailIDs)
ThumbnailIDs.to_csv("./result/output.csv", index = False)
