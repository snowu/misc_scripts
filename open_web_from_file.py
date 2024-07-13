import webbrowser
import time

def open_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = file.readlines()
    
    for url in urls:
        url = url.strip()
        if url:  
            webbrowser.open(url)
            time.sleep(0.5)  

file_path = "C:\\Users\\zanca\\Documents\\dropshipping.txt"
open_urls_from_file(file_path)