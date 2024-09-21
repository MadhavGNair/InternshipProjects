# PDF Parser
**Author: Madhav Girish Nair (madhavgirish02@gmail.com)**

The purpose of this class is to parse a given PDF and convert it into a format that can be processed by later pipelines.
The module also includes code for a first-level table detection as this reduces the load on the actual table extraction
module and reduces costs of OCR. Even though the module is titled PDFParser, it essentially comprises two equally 
important components:

(1) PDFParser: this component parses each page of the PDF using PyPDF2 and extracts metadata as well. It also does an initial
table detection using the building in table finder, however, there are a lot of false positives in the output of this detector. 
Later, an LLM is prompted to remove these false positives such that we are left with a list of pages with only the relevant tables.
These pages that contain the tables are then converted to images and stored in the /data folder.

(2) TableDetector: this component takes the images extracted from the PDFParser module and performs OCR on them to extract the 
tables in either HTML or Markdown format as desired. Currently, the GPT-4o-mini Vision model is prompted to perform OCR, however,
other methods will be added gradually.

The folder and file structure is explained below:

## /pdf_parser
This folder contains the bulk of the code and the following sub-folders,

### /data
The initial PDF to be processed, as well as any output from either modules are stored in this folder.

### pdf_parser.py
This file contains the main PDFParser module.

### table_extraction.py
This file contains the main TableExtractor module.

### main.py
This file is where both modules are initialized and manipulated.