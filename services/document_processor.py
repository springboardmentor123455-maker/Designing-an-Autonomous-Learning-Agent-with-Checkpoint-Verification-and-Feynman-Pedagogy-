import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader

class DocumentProcessor:
    """Handles PDF document processing"""
    
    def parse_pdf(self, uploaded_file) -> str:
        """Parse PDF file and extract text"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()
            os.remove(tmp_path)
            
            # Combine all pages
            return "\n\n".join([p.page_content for p in pages])
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""