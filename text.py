from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter as cts

def process_files(files):
    text = ""

    for file in files:
        pdf = PdfReader(file) # Transforma em PyPDF2._reader.PdfReader
        for page in pdf.pages: # Transforma em PyPDF2._page.PageObject e itera sobre
            text += page.extract_text() # Transforma em string
    return text

def create_text_chunks(text):
    text_splitter = cts(
        separator='\n',    # como separa chunks, no caso nova linha 
        chunk_size=1500,   # tamanho de cada chunk
        chunk_overlap=300,  # faz com que cada chunk comece com 300 caracteres do chunk anterior 
        length_function=len)
    
    chunks = text_splitter.split_text(text) # separa o texto em chunks
    return chunks