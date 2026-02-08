from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm




# ==================================================
# APP CONFIG
# ==================================================
app = Flask(__name__)
app.secret_key = "dev-secret-key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# ==================================================
# MODELS
# ==================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    level = db.Column(db.String(20))
    programme = db.Column(db.String(150))
    department = db.Column(db.String(150))
    session_type = db.Column(db.String(50))

    role = db.Column(db.String(20), default="student")


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file = db.Column(db.String(200))

    status = db.Column(db.String(20), default="pending")
    feedback = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    student = db.relationship("User", backref="projects")


class SubmissionDeadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deadline = db.Column(db.DateTime, nullable=False)

# ==================================================
# INIT DATABASE
# ==================================================

def create_default_admin():
    admin_email = "StArbOi@sintimdev.org"

    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            name="Benjamin Sintim",
            email=admin_email,
            password=generate_password_hash("baba1234"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Permanent admin created")

with app.app_context():
    db.create_all()
    create_default_admin()

    if not SubmissionDeadline.query.first():
        db.session.add(
            SubmissionDeadline(deadline=datetime(2026, 2, 12, 23, 59))
        )
        db.session.commit()

#def generate_gctu_cover_pdf(filename="gctu_report.pdf"):
 ######################)

    ######## c.save()
   # return file_path #





    

# ==================================================
# CLEAN PROFESSIONAL PDF REPORT ENGINE (RENDER SAFE)
# ==================================================

def draw_gctu_cover_page(c, subtitle):
    """
    Draws the GCTU logo + title on the SAME first page
    and returns where table content should start.
    """
    width, height = A4

    # ✅ Render-safe absolute logo path
    logo_path = os.path.join(app.root_path, "static", "images", "gctu_logo.png")

    # Draw logo if exists
    if os.path.exists(logo_path):
        c.drawImage(
            logo_path,
            width / 2 - 4 * cm,
            height - 5.5 * cm,
            width=8 * cm,
            preserveAspectRatio=True,
            mask="auto"
        )

    # University name
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(
        width / 2,
        height - 8.5 * cm,
        "GHANA COMMUNICATION TECHNOLOGY UNIVERSITY"
    )

    # System name
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(
        width / 2,
        height - 10 * cm,
        "PROJECT SUBMISSION SYSTEM"
    )

    # Report subtitle
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 11.5 * cm, subtitle)

    # Generated date
    c.setFont("Helvetica", 10)
    c.drawCentredString(
        width / 2,
        2.5 * cm,
        f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
    )

    # ✅ Return starting Y for table content
    return height - 13 * cm


# ==================================================
# REGISTERED STUDENTS PDF
# ==================================================

def generate_students_report_pdf(filename="students_report.pdf"):
    file_path = os.path.join(BASE_DIR, filename)
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    students = User.query.filter_by(role="student").all()
    total_students = len(students)

    # Draw first-page header
    y = draw_gctu_cover_page(c, "REGISTERED STUDENTS REPORT")

    row_height = 0.7 * cm

    # Table header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "NAME")
    c.drawString(8 * cm, y, "PROGRAMME")
    c.drawString(14 * cm, y, "LEVEL")

    y -= row_height
    c.setFont("Helvetica", 10)

    # Table rows
    for s in students:
        c.drawString(2 * cm, y, s.name)
        c.drawString(8 * cm, y, s.programme or "-")
        c.drawString(14 * cm, y, s.level or "-")

        y -= row_height

        # New page if space finished
        if y < 2.5 * cm:
            c.showPage()
            y = draw_gctu_cover_page(c, "REGISTERED STUDENTS REPORT")

    # Total count at bottom
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, 2 * cm, f"Total Registered Students: {total_students}")

    c.save()
    return file_path


# ==================================================
# SUBMITTED PROJECTS PDF
# ==================================================

def generate_projects_report_pdf(filename="projects_report.pdf"):
    file_path = os.path.join(BASE_DIR, filename)
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    projects = Project.query.all()
    total_projects = len(projects)

    # Draw first-page header
    y = draw_gctu_cover_page(c, "SUBMITTED PROJECTS REPORT")

    row_height = 0.7 * cm

    # Table header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "STUDENT")
    c.drawString(7 * cm, y, "PROJECT TITLE")
    c.drawString(14 * cm, y, "STATUS")

    y -= row_height
    c.setFont("Helvetica", 10)

    # Table rows
    for p in projects:
        c.drawString(2 * cm, y, p.student.name)
        c.drawString(7 * cm, y, p.title[:40])  # prevent overflow
        c.drawString(14 * cm, y, p.status)

        y -= row_height

        # New page handling
        if y < 2.5 * cm:
            c.showPage()
            y = draw_gctu_cover_page(c, "SUBMITTED PROJECTS REPORT")

    # Total count
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, 2 * cm, f"Total Submitted Projects: {total_projects}")

    c.save()
    return file_path




# ==================================================
# AUTH
# ==================================================

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            session["name"] = user.name
            session["role"] = user.role

            return redirect(
                url_for("admin_dashboard")
                if user.role == "admin"
                else url_for("student_dashboard")
            )

        flash("Invalid email or password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==================================================
# REGISTER
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if User.query.filter_by(email=request.form["email"]).first():
            flash("Email already exists")
            return redirect(url_for("register"))

        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"]),
            level=request.form["level"],
            programme=request.form["programme"],
            department=request.form["department"],
            session_type=request.form["session_type"],
            role="student"
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")

# ==================================================
# CHANGE PASSWORD
# ==================================================

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        if not check_password_hash(user.password, request.form["old_password"]):
            flash("Old password incorrect")
            return redirect(url_for("change_password"))

        if request.form["new_password"] != request.form["confirm_password"]:
            flash("Passwords do not match")
            return redirect(url_for("change_password"))

        user.password = generate_password_hash(request.form["new_password"])
        db.session.commit()

        flash("Password updated successfully")

        return redirect(
            url_for("admin_dashboard")
            if user.role == "admin"
            else url_for("student_dashboard")
        )

    return render_template("change_password.html")



# ==================================================
# STUDENT
# ==================================================

@app.route("/student/dashboard")
def student_dashboard():
    if session.get("role") != "student":
        return redirect(url_for("login"))

    projects = Project.query.filter_by(student_id=session["user_id"]).all()
    return render_template("student/dashboard.html", projects=projects)

@app.route("/student/create_project", methods=["GET", "POST"])
def create_project():
    if session.get("role") != "student":
        return redirect(url_for("login"))

    deadline = SubmissionDeadline.query.first()

    if request.method == "POST":

        # ⛔ deadline check FIRST
        if datetime.now() > deadline.deadline:
            flash("Submission deadline has passed")
            return redirect(url_for("student_dashboard"))

        file = request.files.get("file")
        filename = None

        if file:
            filename = f"{session['user_id']}_{file.filename}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        project = Project(
            title=request.form["title"],
            description=request.form["description"],
            file=filename,
            student_id=session["user_id"]
        )

        db.session.add(project)
        db.session.commit()

        flash("Project submitted successfully")
        return redirect(url_for("student_dashboard"))

    return render_template("student/create_project.html")

@app.route("/student/profile")
def student_profile():
    if session.get("role") != "student":
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    return render_template("student/profile.html", user=user)

@app.route("/student/delete_project/<int:project_id>")
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    if project.student_id != session.get("user_id"):
        return redirect(url_for("student_dashboard"))

    if project.file:
        path = os.path.join(app.config["UPLOAD_FOLDER"], project.file)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(project)
    db.session.commit()

    flash("Project deleted")
    return redirect(url_for("student_dashboard"))

@app.route("/student/edit_project/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    if session.get("role") != "student":
        return redirect(url_for("login"))

    project = Project.query.get_or_404(project_id)

    if project.student_id != session["user_id"]:
        return redirect(url_for("student_dashboard"))

    if project.status != "rejected":
        flash("Only rejected projects can be edited")
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        project.title = request.form["title"]
        project.description = request.form["description"]

        file = request.files.get("file")
        if file:
            filename = f"{session['user_id']}_{file.filename}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            project.file = filename

        project.status = "pending"
        project.feedback = None
        db.session.commit()

        flash("Project resubmitted successfully")
        return redirect(url_for("student_dashboard"))

    return render_template("student/edit_project.html", project=project)


# ==================================================
# ADMIN
# ==================================================

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    total_students = User.query.filter_by(role="student").count()
    total_projects = Project.query.count()
    approved_projects = Project.query.filter_by(status="approved").count()
    pending_projects = Project.query.filter_by(status="pending").count()

    projects = Project.query.all()

    return render_template(
        "admin/dashboard.html",
        projects=projects,
        total_students=total_students,
        total_projects=total_projects,
        approved_projects=approved_projects,
        pending_projects=pending_projects,
        page="dashboard"
    )



@app.route("/admin/deadline", methods=["GET", "POST"])
def admin_deadline():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    deadline = SubmissionDeadline.query.first()

    if request.method == "POST":
        deadline.deadline = datetime.strptime(
            request.form["deadline"], "%Y-%m-%dT%H:%M"
        )
        db.session.commit()
        flash("Deadline updated")

    return render_template("admin/deadline.html", deadline=deadline)

@app.route("/admin/view_project/<int:project_id>", methods=["GET", "POST"])
def view_project(project_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        project.status = request.form.get("action")
        project.feedback = request.form.get("feedback")
        db.session.commit()

        flash("Decision saved successfully")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/view_project.html", project=project)

@app.route("/admin/students")
def admin_students():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    students = User.query.filter_by(role="student").all()
    return render_template(
        "admin/students.html",
        students=students,
        page="students"
    )

@app.route("/admin/download-projects-pdf")
def download_projects_pdf():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    pdf_path = generate_projects_report_pdf()
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="GCTU_Submitted_Projects_Report.pdf"
    )


@app.route("/admin/download-students-pdf")
def download_students_pdf():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    pdf_path = generate_students_report_pdf()
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="GCTU_Registered_Students_Report.pdf"
    )




@app.route("/admin/reset_password/<int:user_id>")
def admin_reset_password(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash("Admin password cannot be reset")
        return redirect(url_for("admin_dashboard"))

    temp_password = "student123"
    user.password = generate_password_hash(temp_password)
    db.session.commit()

    flash(f"Temporary password for {user.name}: {temp_password}")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/student/<int:user_id>")
def admin_view_student(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    student = User.query.get_or_404(user_id)
    projects = Project.query.filter_by(student_id=user_id).all()

    return render_template(
        "admin/view_student.html",
        student=student,
        projects=projects
    )

# ==========================
# PDF DOWNLOADS (ADMIN)
# ==========================

@app.route("/admin/download-projects-report")
def download_projects_report():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    pdf_path = generate_projects_report_pdf()

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="GCTU_Submitted_Projects_Report.pdf"
    )


@app.route("/admin/download-students-report")
def download_students_report():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    pdf_path = generate_students_report_pdf()

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="GCTU_Registered_Students_Report.pdf"
    )



# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)



