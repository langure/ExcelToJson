import os

# ENV
EXCEL_FILE = "metadatos.xlsx"
JSON_FILE = "metadatos.json"

def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')
    else:    
        _ = os.system('cls')

if __name__ == "__main__":
    clear_screen()
    print("Hello world")