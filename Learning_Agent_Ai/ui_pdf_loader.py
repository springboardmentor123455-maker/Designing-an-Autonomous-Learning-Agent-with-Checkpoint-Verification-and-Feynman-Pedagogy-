from PyPDF2 import PdfReader


class PDFLoader:
    def load(self, file):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
