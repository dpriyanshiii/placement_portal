import os

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from extensions import db
from models import User, Student, Company


auth = Blueprint('auth', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_RESUME = {'pdf'}
ALLOWED_LOGO = {'png', 'jpg', 'jpeg'}




@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email   = request.form.get('email', '').strip()
        password  = request.form.get('password', '').strip()


        user = User.query.filter_by(email=email).first()


        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))


        session['user_id'] = user.user_id
        session['role']    = user.role


        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'student':
            return redirect(url_for('student.dashboard'))
        elif user.role == 'company':
            company = Company.query.filter_by(user_id=user.user_id).first()
            if not company or company.approval_status != 1:
                flash('Company not approved yet.', 'error')
                return redirect(url_for('home'))
            return redirect(url_for('company.dashboard'))
        
    
    #DEBUG!!!
    # users = User.query.all()
    # print("ALL USERS:")
    # for u in users:
    #     print(u.email, u.role)

    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))




#validating file inputttt
def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


@auth.route('/student_signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        #chunk one
        f_name     = request.form.get('f_name', '').strip()
        l_name     = request.form.get('l_name', '').strip()
        username   = request.form.get('username', '').strip()
        email      = request.form.get('email', '').strip()
        password   = request.form.get('password', '').strip()
        department = request.form.get('department', '').strip()
        cgpa       = request.form.get('cgpa', '').strip()
        phone      = request.form.get('phone', '').strip()
        resume     = request.files.get('resume')


        #chunk two
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('auth.student_signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.student_signup'))


        resume_path = None
        if resume and allowed_file(resume.filename, ALLOWED_RESUME):
            filename    = secure_filename(f"{username}_resume.pdf")
            resume_dir  = os.path.join(UPLOAD_FOLDER, 'resumes')
            os.makedirs(resume_dir, exist_ok=True)
            resume_path = os.path.join(resume_dir, filename)
            resume.save(resume_path)
        else:
            flash('Please upload a valid PDF resume.', 'error')
            return redirect(url_for('auth.student_signup'))


        #chunk threeee
        new_user = User(
            username      = username,
            email         = email,
            password_hash = generate_password_hash(password),
            role          = 'student'
        )
        db.session.add(new_user)
        db.session.flush()

        new_student = Student(
            user_id    = new_user.user_id,
            email      = email,
            f_name     = f_name,
            l_name     = l_name,
            department = department,
            cgpa       = float(cgpa) if cgpa else None,
            phone      = phone,
            resume     = resume_path
        )
        db.session.add(new_student)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/student_signup.html')



@auth.route('/company_signup', methods=['GET', 'POST'])
def company_signup():
    if request.method == 'POST':
        #oneee
        company_name = request.form.get('company_name', '').strip()
        hr_fname     = request.form.get('hr_fname', '').strip()
        hr_lname     = request.form.get('hr_lname', '').strip()
        hr_email     = request.form.get('hr_email', '').strip()
        website      = request.form.get('website', '').strip()
        description  = request.form.get('description', '').strip()
        username     = request.form.get('username', '').strip()
        email        = request.form.get('email', '').strip()
        password     = request.form.get('password', '').strip()
        logo         = request.files.get('logo')

        #two
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('auth.company_signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.company_signup'))

        logo_path = None
        if logo and allowed_file(logo.filename, ALLOWED_LOGO):
            filename  = secure_filename(f"{username}_logo.{logo.filename.rsplit('.', 1)[1].lower()}")
            logo_dir  = os.path.join(UPLOAD_FOLDER, 'logos')
            os.makedirs(logo_dir, exist_ok=True)
            logo_path = os.path.join(logo_dir, filename)
            logo.save(logo_path)

        #now threee
        new_user = User(
            username      = username,
            email         = email,
            password_hash = generate_password_hash(password),
            role          = 'company'
        )
        db.session.add(new_user)
        db.session.flush()

        new_company = Company(
            user_id         = new_user.user_id,
            email           = email,
            company_name    = company_name,
            hr_fname        = hr_fname,
            hr_lname        = hr_lname,
            hr_email        = hr_email,
            website         = website,
            description     = description,
            logo            = logo_path,
            approval_status = 0
        )
        db.session.add(new_company)
        db.session.commit()

        flash('Registration submitted! Wait for admin approval before logging in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/company_signup.html')