import os

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import User, Student, Company, PlacementDrive, Application

from extensions import db

from werkzeug.utils import secure_filename

from datetime import datetime

student = Blueprint('student', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_RESUME = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME


#dashboard
@student.route('/dashboard')
def dashboard():
    expired = PlacementDrive.query.filter(
        PlacementDrive.deadline < datetime.now(),
        PlacementDrive.status == False
    ).all()
    for d in expired:
        d.status = True
    db.session.commit()

    student_obj  = Student.query.filter_by(user_id=session.get('user_id')).first_or_404()
    applications = Application.query.filter_by(student_id=student_obj.student_id).all()

    applied_drive_ids = [a.drive_id for a in applications]
    companies = Company.query.filter_by(approval_status=True, is_blacklisted=False).join(
        PlacementDrive, Company.company_id == PlacementDrive.company_id
    ).filter(PlacementDrive.status == False).distinct().all()

    return render_template('student/student.html',
        student      = student_obj,
        applications = applications,
        companies    = companies,
    )


#company view
@student.route('/company/<int:company_id>')
def company_view(company_id):
    company = Company.query.get_or_404(company_id)
    drives  = PlacementDrive.query.filter_by(company_id=company_id, status=False).all()

    if company.logo:
        company.logo = company.logo.replace('\\', '/')

    return render_template('student/company_information.html',
        company = company,
        drives  = drives,
    )


#drive view
@student.route('/drive/<int:drive_id>')
def drive_view(drive_id):
    drive       = PlacementDrive.query.get_or_404(drive_id)
    company     = Company.query.get_or_404(drive.company_id)
    student_obj = Student.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if company.logo:
        company.logo = company.logo.replace('\\', '/')

    applied = Application.query.filter_by(
        student_id = student_obj.student_id,
        drive_id   = drive_id
    ).first() is not None

    return render_template('student/drive_information.html',
        drive   = drive,
        company = company,
        applied = applied,
    )


#apply
@student.route('/apply/<int:drive_id>', methods=['POST'])
def apply_drive(drive_id):
    student_obj = Student.query.filter_by(user_id=session.get('user_id')).first_or_404()
    drive       = PlacementDrive.query.get_or_404(drive_id)

    if drive.status:
        flash('This drive is closed.', 'error')
        return redirect(url_for('student.drive_view', drive_id=drive_id))

    already_applied = Application.query.filter_by(
        student_id = student_obj.student_id,
        drive_id   = drive_id
    ).first()

    if already_applied:
        flash('You have already applied to this drive.', 'error')
        return redirect(url_for('student.drive_view', drive_id=drive_id))

    new_application = Application(
        student_id = student_obj.student_id,
        drive_id   = drive_id,
        status     = 'waiting'
    )
    db.session.add(new_application)
    db.session.commit()
    flash('Application submitted successfully.', 'success')
    return redirect(url_for('student.dashboard'))


#history
@student.route('/history')
def history():
    student_obj  = Student.query.filter_by(user_id=session.get('user_id')).first_or_404()
    applications = Application.query.filter_by(student_id=student_obj.student_id).all()

    return render_template('student/history.html',
        student      = student_obj,
        applications = applications,
    )


#profile
@student.route('/profile')
def profile():
    student_obj = Student.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if student_obj.resume:
        student_obj.resume = student_obj.resume.replace('\\', '/')

    return render_template('student/student_profile.html',
        student = student_obj,
    )


#edit profile
@student.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    student_obj = Student.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if request.method == 'POST':
        student_obj.f_name     = request.form.get('f_name', '').strip()
        student_obj.l_name     = request.form.get('l_name', '').strip()
        student_obj.phone      = request.form.get('phone', '').strip()
        student_obj.cgpa       = float(request.form.get('cgpa')) if request.form.get('cgpa') else None
        student_obj.department = request.form.get('department', '').strip()

        resume = request.files.get('resume')
        if resume and allowed_file(resume.filename):
            filename   = secure_filename(f"{session.get('user_id')}_resume.pdf")
            resume_dir = os.path.join(UPLOAD_FOLDER, 'resumes')
            os.makedirs(resume_dir, exist_ok=True)
            resume_path = os.path.join(resume_dir, filename)
            resume.save(resume_path)
            student_obj.resume = resume_path

        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/student_profile_edit.html',
        student = student_obj,
    )