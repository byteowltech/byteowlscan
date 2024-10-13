
import datetime
import os
import re
import unicodedata


#Get file name from path
def get_file_name(filePath):
    file_name = os.path.basename(filePath)
    return file_name

#Clean file name
def clean_filename(filename):
    # Normalize the filename to NFC (Normalization Form C)
    normalized_name = unicodedata.normalize('NFC', filename)
    
    # Replace spaces with an underscore
    normalized_name = normalized_name.replace(' ', '_')
    
    # Remove any characters that are not alphanumeric, underscore, or hyphen
    clean_name = re.sub(r'[^\w\-]', '', normalized_name)
    
    return clean_name


# Testing the script by parsing a PDF/Word/Image resume
if __name__ == '__main__':
    now = datetime.datetime.now()
    timeStamp = now.strftime("%Y-%m-%d %H:%M:%S")
    fileName = get_file_name('/Users/hoangnhh/Sources/NLP/ScanResume/tests/Fresher_tranthienhieu.pdf')
    json_file_path = fileName
    print(json_file_path)
        