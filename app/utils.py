from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generate_resume(user_id: int):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"Resume for User ID: {user_id}")
    c.drawString(100, 730, "Name: Example Name")
    c.drawString(100, 710, "Email: example@example.com")
    c.drawString(100, 690, "Phone: 123-456-7890")
    c.save()
    buffer.seek(0)
    return buffer