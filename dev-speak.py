#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Analyze year reports published by development organizations to measure the
# amount of buzzwords each of them contains.
#
# The PDF Reports are downloaded locally and transformed into text files. The
# reports and text files are kept on disk, giving the user the chance to
# analyze them.

# Results are stored in JSON

# ASSUMPTIONS
# - Only parsing PDF for now
# - Only one report per year per organization

# TODO
# - improve the count, currently only lowercasing the words and the text files


import os
import urllib
import csv
import sys
import json
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

# Files with the reports and buzzwords to be analyzed. Full path.
reports = "reports.csv"
buzzwords = "buzzwords.csv"

# Cache directories, with trailing slash
reports_dir = "cache/reports/"
txt_dir = "cache/txt/"
results_dir = "cache/results/"


def no_file_exit(f):
  "Check if a file exists. If not, the program exits."
  if not os.path.isfile(f):
    print "Can't find " + f + ". Aborting..."
    sys.exit(0)

def create_dir(d):
  "Attempt to create a directory."
  if not os.path.exists(d):
    os.makedirs(d)
  else:
    print "The '" + d + "' folder already exists."

def fetch_report(url,org,year):
  "Check if the report for an organization is already cached. If not, download it."
  filename = reports_dir + org + "-" + year + ".pdf"
  if os.path.isfile(filename):
    print "Skipped " + org + "'s " + year + " report. A cached version was found."
  else:
    try:
      urllib.urlretrieve (url,filename)
      print "Fetched the " + year + " report of " + org + "."
    except:
      print "Could not fetch the " + year + " report of " + org + "."
      pass

# http://stackoverflow.com/a/20905381
def convert_pdf_to_txt(filename):
  "Converts the PDF to txt and returns a string"
  rsrcmgr = PDFResourceManager()
  retstr = StringIO()
  codec = 'utf-8'
  laparams = LAParams()
  device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
  fp = file(filename, 'rb')
  interpreter = PDFPageInterpreter(rsrcmgr, device)
  password = ""
  maxpages = 0
  caching = True
  pagenos=set()
  for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
    interpreter.process_page(page)
  fp.close()
  device.close()
  str = retstr.getvalue()
  retstr.close()
  return str

def perform_count(f,bare_f,words):
  "Counts the frequency of each dict key in the file. Stores the results in json."
  with open (f, "r") as ifile:
    data=ifile.read().replace('\n', '').lower()
  for key in words:
    words[key] = data.count(key)
  with open(results_dir + bare_f + ".json", 'wb') as result_file:
    json.dump(words, result_file)


# Check if the list with reports and buzzwords exist.
for f in [reports,buzzwords]:
  no_file_exit(f)

# Create the cache folders for the downloaded reports and the transformed text
for d in [reports_dir,txt_dir,results_dir]:
  create_dir(d)

# Loop over the reports in the CSV and download them
with open(reports, 'rb') as ifile:
  reader = csv.reader(ifile)
  # Skip first row that contains the header
  next(reader)
  print "««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»"
  print "|  Starting to download the reports that will be analyzed  |"
  print "««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»"
  for row in reader:
    url = row[2]
    org = row[0]
    year = row[1]
    fetch_report(url,org,year)

print "««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»"
print "|  Starting the transformation of the PDF reports to txt   |"
print "««««««««««««««««««««««««««««««»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»"

# Loop over the contents of the cached reports folder and attempt to transform
# the files into text.
for f in os.listdir(reports_dir):
  
  # Get filename without extension
  bare_f = os.path.splitext(f)[0]

  source = reports_dir + f
  dest = txt_dir + bare_f + ".txt"

  # Only attempt to transform files
  if os.path.isfile(source):
    # If destination is already available, we can skip transformation
    if not os.path.isfile(dest):
      try:
        pdf_txt = convert_pdf_to_txt(source)
        text_file = open(dest, "w")
        text_file.write(pdf_txt)
        text_file.close()
        print f + " transformed."
      except:
        print "Can't transform " + f
        pass
    else:
      print "Skipped " + f + ". A cached version was found."

# Create the 'words' dict and store all the buzzwords as key with empty values
with open(buzzwords, 'rb') as ifile:
  reader = csv.reader(ifile)
  # Skip first row that contains the header
  next(reader)
  words = { }
  for row in reader:
    word = row[0].lower()
    words[word] = ''

# Loop over all the text files in the cache folder and perform a count.
for f in os.listdir(txt_dir):

  # Get filename without extension
  bare_f = os.path.splitext(f)[0]
  source = txt_dir + f
  
  # Only attempt to count files
  if os.path.isfile(source):
    perform_count(source,bare_f,words)