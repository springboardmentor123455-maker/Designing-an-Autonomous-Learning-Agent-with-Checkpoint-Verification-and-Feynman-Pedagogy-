import streamlit as st
from ui_pdf_loader import PDFLoader

# streamlit run Learning_Agent_Ai\ui_upload_view.py

def upload_view():
    """
    Streamlit UI component for uploading a PDF file.
    Returns extracted text if a PDF is uploaded, else None.
    """

    st.subheader("📄 Upload Notes (Optional)")

    uploaded_file = st.file_uploader(
        label="Upload a PDF containing your notes",
        type=["pdf"],
        accept_multiple_files=False
    )

    if uploaded_file is None:
        return None

    try:
        loader = PDFLoader()
        text = loader.load(uploaded_file)

        if not text.strip():
            st.warning("⚠️ PDF uploaded, but no readable text was found.")
            return None

        st.success("✅ PDF uploaded and text extracted successfully.")
        return text

    except Exception as e:
        st.error("❌ Failed to read PDF.")
        st.exception(e)
        return None
