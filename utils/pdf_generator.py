from app import BASE_DIR, User, Project
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import os



def gctu_cover_page(output_path, student, project):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Logo
    logo_path = "static/images/gctu_logo.png"
    if os.path.exists(logo_path):
        c.drawImage(logo_path, width / 2 - 2 * cm, height - 4 * cm, 4 * cm, 4 * cm)

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 6 * cm, "GHANA COMMUNICATION TECHNOLOGY UNIVERSITY")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 7.2 * cm, "PROJECT SUBMISSION COVER PAGE")

    y = height - 9 * cm
    line_gap = 1.1 * cm

    details = [
        ("Student Name", student.name),
        ("Email", student.email),
        ("Programme", student.programme),
        ("Department", student.department),
        ("Level", student.level),
        ("Session", student.session_type),
        ("Project Title", project.title),
        ("Submission Date", datetime.now().strftime("%d %B %Y")),
    ]

    c.setFont("Helvetica", 11)

    for label, value in details:
        c.drawString(4 * cm, y, f"{label}:")
        c.drawString(9 * cm, y, str(value))
        y -= line_gap

    c.showPage()
    c.save()
    
    
def add_gctu_cover(c):
    width, height = A4

    logo_path = os.path.join(BASE_DIR, "static", "images", "gctu_logo.png")
    if os.path.exists(logo_path):
        c.drawImage(
            logo_path,
            width / 2 - 3 * cm,
            height - 6 * cm,
            width=6 * cm,
            preserveAspectRatio=True,
            mask="auto"
        )

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(
        width / 2,
        height - 8 * cm,
        "GHANA COMMUNICATION TECHNOLOGY UNIVERSITY"
    )

    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2,
        height - 9.5 * cm,
        "ADMIN REPORT"
    )

    c.setFont("Helvetica", 10)
    c.drawCentredString(
        width / 2,
        2 * cm,
        f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
    )

    c.showPage()


def generate_projects_pdf():
    file_path = os.path.join(BASE_DIR, "submitted_projects.pdf")
    c = canvas.Canvas(file_path, pagesize=A4)

    add_gctu_cover(c)

    projects = Project.query.all()
    width, height = A4
    y = height - 2*cm

    c.setFont("Helvetica", 10)

    for p in projects:
        c.drawString(
            2*cm,
            y,
            f"{p.student.name} | {p.title} | {p.status} | {p.created_at.date()}"
        )
        y -= 0.7*cm

        if y < 2*cm:
            c.showPage()
            y = height - 2*cm

    c.save()
    return file_path

def generate_students_pdf():
    file_path = os.path.join(BASE_DIR, "registered_students.pdf")
    c = canvas.Canvas(file_path, pagesize=A4)

    add_gctu_cover(c)

    students = User.query.filter_by(role="student").all()
    width, height = A4
    y = height - 2*cm

    c.setFont("Helvetica", 10)

    for s in students:
        c.drawString(
            2*cm,
            y,
            f"{s.name} | {s.programme} | {s.level} | {s.session_type}"
        )
        y -= 0.7*cm

        if y < 2*cm:
            c.showPage()
            y = height - 2*cm

    c.save()
    return file_path
