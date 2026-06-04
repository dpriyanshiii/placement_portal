from extensions import db
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key = True)

    username = db.Column(db.String(20), unique = True, nullable  = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password_hash = db.Column(db.String(200), nullable = False)
    role = db.Column(db.String(7), nullable = False) #company/student/admin



class Student(db.Model):
    __tablename__ = 'students'

    student_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True)
    email = db.Column(db.String(100), db.ForeignKey('users.email'), unique=True, nullable=False)

    f_name = db.Column(db.String(20), nullable=False)
    l_name = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    phone = db.Column(db.String(10))
    resume = db.Column(db.String(200))
    is_blacklisted = db.Column(db.Boolean, default=False)



class Company(db.Model):
    __tablename__ = 'companies'

    company_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True)
    email = db.Column(db.String(100), db.ForeignKey('users.email'), unique=True, nullable=False)

    company_name = db.Column(db.String(100), nullable=False)
    hr_fname = db.Column(db.String(20), nullable=False)
    hr_lname = db.Column(db.String(20), nullable=False)
    hr_email = db.Column(db.String(100), nullable=False)
    website = db.Column(db.Text)
    description = db.Column(db.Text)
    logo = db.Column(db.String(200))
    approval_status = db.Column(db.Boolean, default=False)  # shortlist, waiting/reject
    is_blacklisted = db.Column(db.Boolean, default=False)




class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    drive_id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'))

    drive_name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text, nullable=False)
    salary = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.Boolean, default=False) #pending, complete


    company = db.relationship('Company', backref='drives')



class Application(db.Model):
    __tablename__ = 'applications'

    aplication_id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.drive_id'))

    applied_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(11), default='waiting')  # shortlist, waiting, reject
    remarks = db.Column(db.Text)


    student = db.relationship('Student', backref='applications')
    drive   = db.relationship('PlacementDrive', backref='applications')