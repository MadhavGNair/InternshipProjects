from pdf_parser import PDFParser
import time

OPENAI_API_KEY = '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'
pdf_path = './data/2022_Apple_ESG_Report.pdf'
output_directory = './data'

start = time.time()
parser = PDFParser(api_key=OPENAI_API_KEY)
output = parser.parse(pdf_path, output_directory)
print("--- %s seconds ---" % (time.time() - start))

