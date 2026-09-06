from pydantic import BaseModel

from langchain_core.tools import StructuredTool

from tools.pdf_tool import create_pdf
from tools.text_tool import create_text_file
from tools.email_tool import send_email


# ======================================================
# EMAIL SCHEMA
# ======================================================

class EmailInput(BaseModel):

    receiver_email: str

    body: str


# ======================================================
# PDF TOOL
# ======================================================

pdf_tool = StructuredTool.from_function(
    func=create_pdf,
    name="PDFGenerator",
    description="Create PDF from content"
)


# ======================================================
# TEXT TOOL
# ======================================================

text_tool = StructuredTool.from_function(
    func=create_text_file,
    name="TextFileGenerator",
    description="Create text file from content"
)


# ======================================================
# EMAIL TOOL
# ======================================================

email_tool = StructuredTool.from_function(
    func=send_email,
    name="EmailSender",
    description="Send email",
    args_schema=EmailInput
)