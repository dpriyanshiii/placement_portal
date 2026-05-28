from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models import User, Student, Company, PlacementDrive, Application
from extensions import db

company = Blueprint('company', __name__)


# --- dashboard ---
@company.route('/dashboard')
def dashboard():
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()
    drives      = PlacementDrive.query.filter_by(company_id=company_obj.company_id).all()

    return render_template('company/company.html',
        company = company_obj,
        drives  = drives,
    )


#profile
@company.route('/profile')
def profile():
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if company_obj.logo:
        company_obj.logo = company_obj.logo.replace('\\', '/')

    return render_template('company/company_profile.html',
        company = company_obj,
    )


@company.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if request.method == 'POST':
        company_obj.hr_fname     = request.form.get('hr_fname', '').strip()
        company_obj.hr_lname     = request.form.get('hr_lname', '').strip()
        company_obj.hr_email     = request.form.get('hr_email', '').strip()
        company_obj.website      = request.form.get('website', '').strip()
        company_obj.description  = request.form.get('description', '').strip()
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('company.profile'))

    return render_template('company/company_profile_edit.html',
        company = company_obj,
    )


#drives
@company.route('/create_drive', methods=['GET', 'POST'])
def create_drive():
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if request.method == 'POST':
        drive_name           = request.form.get('drive_name', '').strip()
        job_title            = request.form.get('job_title', '').strip()
        job_description      = request.form.get('job_description', '').strip()
        eligibility_criteria = request.form.get('eligibility_criteria', '').strip()
        salary               = request.form.get('salary', '').strip()
        location             = request.form.get('location', '').strip()
        deadline             = request.form.get('deadline', '').strip()

        from datetime import datetime
        new_drive = PlacementDrive(
            company_id           = company_obj.company_id,
            drive_name           = drive_name,
            job_title            = job_title,
            job_description      = job_description,
            eligibility_criteria = eligibility_criteria,
            salary               = float(salary),
            location             = location,
            deadline             = datetime.strptime(deadline, '%Y-%m-%dT%H:%M'),
            status               = False
        )
        db.session.add(new_drive)
        db.session.commit()
        flash('Drive created successfully.', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/create_drive.html',
        company = company_obj,
    )


@company.route('/edit_drive/<int:drive_id>', methods=['GET', 'POST'])
def edit_drive(drive_id):
    drive       = PlacementDrive.query.get_or_404(drive_id)
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if drive.company_id != company_obj.company_id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        from datetime import datetime
        drive.drive_name           = request.form.get('drive_name', '').strip()
        drive.job_title            = request.form.get('job_title', '').strip()
        drive.job_description      = request.form.get('job_description', '').strip()
        drive.eligibility_criteria = request.form.get('eligibility_criteria', '').strip()
        drive.salary               = float(request.form.get('salary', 0))
        drive.location             = request.form.get('location', '').strip()
        drive.deadline             = datetime.strptime(request.form.get('deadline'), '%Y-%m-%dT%H:%M')
        db.session.commit()
        flash('Drive updated.', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/edit_drive.html',
        drive = drive,
    )


@company.route('/delete_drive/<int:drive_id>')
def delete_drive(drive_id):
    drive       = PlacementDrive.query.get_or_404(drive_id)
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if drive.company_id != company_obj.company_id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('company.dashboard'))

    db.session.delete(drive)
    db.session.commit()
    flash('Drive deleted.', 'success')
    return redirect(url_for('company.dashboard'))


@company.route('/close_drive/<int:drive_id>')
def close_drive(drive_id):
    drive       = PlacementDrive.query.get_or_404(drive_id)
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if drive.company_id != company_obj.company_id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('company.dashboard'))

    drive.status = True
    db.session.commit()
    flash('Drive closed.', 'success')
    return redirect(url_for('company.dashboard'))


#applications
@company.route('/drive/<int:drive_id>/applications')
def drive_applications(drive_id):
    drive       = PlacementDrive.query.get_or_404(drive_id)
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if drive.company_id != company_obj.company_id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('company.dashboard'))

    q = request.args.get('q', '').strip()
    applications = Application.query.filter_by(drive_id=drive_id).join(Student)

    if q:
        applications = applications.filter(
            db.or_(
                Student.f_name.ilike(f'%{q}%'),
                Student.l_name.ilike(f'%{q}%')
            )
        )

    applications = applications.all()

    return render_template('company/drive_applications.html',
        drive        = drive,
        applications = applications,
    )


@company.route('/application/<int:application_id>')
def application_detail(application_id):
    application = Application.query.get_or_404(application_id)
    drive       = PlacementDrive.query.get_or_404(application.drive_id)
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if drive.company_id != company_obj.company_id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('company.dashboard'))

    if application.student.resume:
        application.student.resume = application.student.resume.replace('\\', '/')

    return render_template('company/application_detail.html',
        application = application,
        drive       = drive,
    )


@company.route('/update_application/<int:application_id>', methods=['POST'])
def update_application(application_id):
    application = Application.query.get_or_404(application_id)
    drive       = PlacementDrive.query.get_or_404(application.drive_id)
    company_obj = Company.query.filter_by(user_id=session.get('user_id')).first_or_404()

    if drive.company_id != company_obj.company_id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('company.dashboard'))

    application.status  = request.form.get('status', 'waiting')
    application.remarks = request.form.get('remarks', '').strip()
    db.session.commit()
    flash('Application status updated.', 'success')
    return redirect(url_for('company.application_detail', application_id=application_id))
