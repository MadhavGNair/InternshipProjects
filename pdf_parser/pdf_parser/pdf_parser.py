import os
import time
import json
import pymupdf
from openai import OpenAI
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path

class PDFParser:
    def __init__(self, api_key):
        self.pdf_path = None
        self.pdf_name = None
        self.api_key = api_key
        self.output_dir = None
        self.parsed_data = []
        self.client = None

    def __initialize_LLM(self):
        """
        Function to initialize an LLM client. This prevent multiple initializations for processing the same PDF.
        """
        self.client = OpenAI(api_key=self.api_key)

    def __isolate_text(self):
        """
        Function to extract the parsed text from parsing output of PyMuPDF.
        """
        return [item['text'] for item in self.parsed_data]
    
    def __parse_pages(self):
        """
        Function to parse a given PDF.
        """
        docs = pymupdf.open(self.pdf_path)
        tab_list = []
        for idx, page in enumerate(docs):
            page_dict = {'text': '', 'metadata': {}}
            page_dict['text'] = page.get_text()
            page_dict['metadata']['pdf_path'] = self.pdf_path
            page_dict['metadata']['page_number'] = idx
            page_dict['metadata']['has_table'] = 0
            # detect all pages with tables using PyMuPDF
            tables = page.find_tables(vertical_strategy='text', horizontal_strategy='lines_strict')
            if len(tables.tables) > 0:
                tab_list.append(idx)
            self.parsed_data.append(page_dict)
        return tab_list

    def __detect_tables(self, table_list):
        """
        Function to detect which pages of the parsed PDF contains tables and add identified to parsed_pages.
        """
        # send the tab list through an LLM for further filtering
        if self.client == None:
            self.__initialize_LLM()

        final_list = []

        for page in table_list:
            text = self.parsed_data[page]['text']
            
            prompt = f"""
                Analyze the following text extracted from a PDF page and determine if it contains a table.
                A table is typically characterized by:
                1. A lot of numbers close to each other
                2. Use of delimiters like '|', '-', or spaces to separate columns
                3. Headers that describe the content of each column

                Respond with 'YES' if a table is present, or 'NO' if there is no table.
                Do not provide any explanation, just 'YES' or 'NO'.

                Text:
                {text}

                Does this text contain a table?
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert specialized in analyzing document structure and identifying tables in text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1
            )

            if response.choices[0].message.content.strip().upper() == 'YES':
                final_list.append(page)

        for t_page in final_list:
            self.parsed_data[t_page]['metadata']['has_table'] = 1
        return final_list

    def __filter_table_pages(self, table_list):
        """
        Function to remove all pages with no tables for later OCR processing.
        """
        output_path = f"./data/trimmed_{self.pdf_name}"
        pdf_reader = PdfReader(self.pdf_path)
        pdf_writer = PdfWriter()

        for page in table_list:
            pdf_writer.add_page(pdf_reader.pages[page])

        with open(output_path,'wb') as out:
                pdf_writer.write(out)
        return output_path

    def __convert_pages_to_img(self, trimmed_pdf_path):
        """
        Function to convert each page of a PDF into JPEG images and saves them in a directory named after the PDF file.
        """
        # create a directory based on the PDF filename
        output_dir = f"./data/{self.pdf_name}_images"
        os.makedirs(output_dir, exist_ok=True)

        # convert each page of the PDF into images
        images = convert_from_path(trimmed_pdf_path)
        saved_image_paths = []
        for i, img in enumerate(images):
            image_path = os.path.join(output_dir, f'page_{i}.jpg')
            img.save(image_path, 'JPEG')
            saved_image_paths.append(image_path)

        print(f'Images saved to {output_dir}.')
        
        return saved_image_paths

    def __save_parse_to_json(self):
        with open(self.output_dir + f'/{self.pdf_name}.json', 'w') as file:
            json.dump(self.parsed_data, file, indent=4)
        print(f'Parsed data saved to {self.output_dir}.')

    def parse(self, pdf_path, output_directory):
        """
        Main function to generate JSON of parsed PDF and save pages with tables as images.
        """
        self.pdf_path = pdf_path
        self.pdf_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        self.output_dir = output_directory

        tables_list = self.__parse_pages()
        filtered_tab_list = self.__detect_tables(tables_list)
        trimmed_pdf_path = self.__filter_table_pages(filtered_tab_list)
        image_paths = self.__convert_pages_to_img(trimmed_pdf_path)

        # save the results and delete temp files
        self.__save_parse_to_json()
        remove_path = f'./data/trimmed_{self.pdf_name}'
        if os.path.exists(remove_path):
            os.remove(remove_path)
        else:
            print(f"The file {remove_path} does not exist.")

        return image_paths
        