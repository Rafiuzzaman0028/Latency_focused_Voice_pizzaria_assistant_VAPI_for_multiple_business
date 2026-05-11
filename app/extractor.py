import os
import pandas as pd
from pypdf import PdfReader
from docx import Document
import win32com.client

def convert_doc_to_docx(doc_path: str) -> str:
    """Uses Microsoft Word to convert old .doc file into .docx."""
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False

    doc = word.Documents.Open(os.path.abspath(doc_path))
    new_path = doc_path + "x"

    doc.SaveAs(os.path.abspath(new_path), FileFormat=16)
    doc.Close()
    word.Quit()

    return new_path

def extract_text_from_docx(docx_path: str) -> str:
    """Extracts text from a valid .docx file."""
    document = Document(docx_path)
    return "\n".join([para.text for para in document.paragraphs])

def extract_text_from_excel(file_path: str) -> str:
    """Extracts text from an Excel or CSV file."""
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Convert the dataframe to a clean text representation
        text = df.to_string(index=False)
        return text
    except Exception as e:
        return f"Error extracting from spreadsheet: {str(e)}"

def extract_text(file_path: str) -> str:
    """
    Main extractor supporting PDF, DOCX, DOC, TXT, XLSX, CSV.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    if ext == ".docx":
        return extract_text_from_docx(file_path)

    if ext == ".doc":
        converted_path = convert_doc_to_docx(file_path)
        return extract_text_from_docx(converted_path)

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
            
    if ext in [".xlsx", ".xls", ".csv"]:
        return extract_text_from_excel(file_path)

    raise ValueError("Unsupported file type. Only PDF, DOC, DOCX, TXT, XLSX, CSV are allowed.")

def generate_uk_restaurant_prompt(business_rules: str, menu_text: str) -> str:
    """
    Generates a highly optimized System Prompt for a UK Restaurant/Takeaway.
    """
    prompt = f"""You are a professional, friendly, and highly efficient AI Voice Agent acting as a customer service representative and order-taker for a UK-based restaurant/takeaway.

### CORE PERSONA & RULES:
- You must always speak with a polite, natural UK English tone.
- When dealing with currency, strictly say "Pounds" and "Pence" (e.g., £4.50 is "four pounds fifty").
- For addresses, be prepared to accept standard UK Postcodes.
- If the customer asks for delivery, ensure you ask for their postcode and delivery address. If collection, confirm the pickup time.
- Be extremely concise. You are on the phone; do not give long-winded answers.
- Never hallucinate menu items. ONLY offer items explicitly listed in the Menu Knowledge below.

### BUSINESS SPECIFIC RULES & GREETING:
{business_rules}

### MENU KNOWLEDGE:
{menu_text}

### ORDER TAKING PROCEDURE:
1. Greet the customer and ask how you can help.
2. If they are ordering, ask for the items.
3. Check the Menu Knowledge to confirm availability and price.
4. Always up-sell politely (e.g., "Would you like any drinks or sides with that?").
5. Summarize the final order and state the total price.
6. Ask if it is for Delivery or Collection (Takeaway).
"""
    return prompt
