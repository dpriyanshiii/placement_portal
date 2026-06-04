from flask import Blueprint, render_template, session, redirect, url_for, flash, request

from models import User, Student, Company, PlacementDrive, Application

from extensions import db

from datetime import datetime


admin = Blueprint('admin', __name__)

# --- dashboard ---
@admin.route('/dashboard')
def dashboard():
    expired = PlacementDrive.query.filter(
        PlacementDrive.deadline < datetime.now(),
        PlacementDrive.status == False
        ).all()
    for d in expired:
        d.status = True
    db.session.commit()

    total_students    = Student.query.count()
    total_companies   = Company.query.filter_by(approval_status=True).count()
    pending_approvals = Company.query.filter_by(approval_status=False).count()
    total_drives      = PlacementDrive.query.count()
    students_placed   = Application.query.filter_by(status='shortlist').count()
    total_applications = Application.query.count()

    return render_template('admin/admin.html',
        total_students    = total_students,
        total_companies   = total_companies,
        pending_approvals = pending_approvals,
        total_drives      = total_drives,
        students_placed   = students_placed,
        total_applications= total_applications
    )


#companies chunk
@admin.route('/manage_companies')
def manage_companies():
    q           = request.args.get('q', '').strip()
    filter_type = request.args.get('filter', 'all')

    pending = Company.query.filter_by(approval_status=False).all()

    companies_query = Company.query

    if q:
        companies_query = companies_query.filter(Company.company_name.ilike(f'%{q}%'))

    if filter_type == 'approved':
        companies_query = companies_query.filter_by(approval_status=True, is_blacklisted=False)
    elif filter_type == 'blacklisted':
        companies_query = companies_query.filter_by(is_blacklisted=True)
    elif filter_type == 'pending':
        companies_query = companies_query.filter_by(approval_status=False, is_blacklisted=False)

    companies = companies_query.all()

    return render_template('admin/manage_company.html',
        companies = companies,
        pending   = pending,
    )

@admin.route('/approve_company/<int:company_id>')
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = True
    db.session.commit()
    flash(f'{company.company_name} approved.', 'success')
    return redirect(url_for('admin.manage_companies'))


@admin.route('/reject_company/<int:company_id>')
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    user = User.query.get(company.user_id)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash('Company rejected and removed.', 'error')
    return redirect(url_for('admin.manage_companies'))


@admin.route('/blacklist_company/<int:company_id>')
def blacklist_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    flash(f'{company.company_name} blacklist status updated.', 'success')
    return redirect(url_for('admin.company_detail', company_id=company_id))


@admin.route('/company/<int:company_id>')
def company_detail(company_id):
    company        = Company.query.get_or_404(company_id)
    drives         = PlacementDrive.query.filter_by(company_id=company_id).all()
    total_drives   = len(drives)
    ongoing_drives = sum(1 for d in drives if not d.status)
    students_hired = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company_id,
        Application.status == 'shortlist'
    ).count()

    if company.logo:
        company.logo = company.logo.replace('\\', '/')

    return render_template('admin/company_detail.html',
        company        = company,
        drives         = drives,
        total_drives   = total_drives,
        ongoing_drives = ongoing_drives,
        students_hired = students_hired,
    )


#and drives
@admin.route('/manage_drives')
def manage_drives():
    q            = request.args.get('q', '').strip()
    filter_type  = request.args.get('filter', 'all')
    drives_query = PlacementDrive.query.join(Company)

    if q:
        drives_query = drives_query.filter(
            db.or_(
                PlacementDrive.drive_name.ilike(f'%{q}%'),
                Company.company_name.ilike(f'%{q}%')
            )
        )

    if filter_type == 'ongoing':
        drives_query = drives_query.filter(PlacementDrive.status == False)
    elif filter_type == 'completed':
        drives_query = drives_query.filter(PlacementDrive.status == True)

    all_drives     = drives_query.all()
    ongoing_drives = [d for d in all_drives if not d.status]
    past_drives    = [d for d in all_drives if d.status]

    return render_template('admin/manage_drive.html',
        all_drives     = all_drives,
        ongoing_drives = ongoing_drives,
        past_drives    = past_drives,
    )


@admin.route('/complete_drive/<int:drive_id>')
def complete_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = True
    db.session.commit()
    flash(f'{drive.drive_name} marked as complete.', 'success')
    return redirect(url_for('admin.manage_drives'))


@admin.route('/drive/<int:drive_id>')
def drive_detail(drive_id):
    drive        = PlacementDrive.query.get_or_404(drive_id)
    company      = Company.query.get_or_404(drive.company_id)
    applications = Application.query.filter_by(drive_id=drive_id).all()

    return render_template('admin/drive_detail.html',
        drive        = drive,
        company      = company,
        applications = applications,
    )


#students chunk
@admin.route('/manage_students')
def manage_students():
    q = request.args.get('q', '').strip()

    if q:
        students = Student.query.filter(
            db.or_(
                Student.f_name.ilike(f'%{q}%'),
                Student.l_name.ilike(f'%{q}%'),
                Student.phone.ilike(f'%{q}%'),
                Student.student_id == q if q.isdigit() else False
            )
        ).all()
    else:
        students = Student.query.all()

    return render_template('admin/manage_student.html', students=students)


@admin.route('/blacklist_student/<int:student_id>')
def blacklist_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    flash(f'{student.f_name} blacklist status updated.', 'success')
    return redirect(url_for('admin.student_detail', student_id=student_id))


@admin.route('/student/<int:student_id>')
def student_detail(student_id):
    student      = Student.query.get_or_404(student_id)
    applications = Application.query.filter_by(student_id=student_id).all()

    if student.resume:
        student.resume = student.resume.replace('\\', '/')

    return render_template('admin/student_detail.html',
        student      = student,
        applications = applications,
    )



# #--------------still onto it----------

# def admin_required():
#     if session.get('role') != 'admin':
#         return redirect(url_for('auth.login'))
#     return None
