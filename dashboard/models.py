from flask_login import UserMixin
from dashboard import db


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('User', backref='school', lazy=True)
    classes = db.relationship('Class', backref='school', lazy=True)


class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    class_name = db.Column(db.String(10), nullable=False)
    sections = db.relationship('Section', backref='class', lazy=True)
    subjects = db.relationship('Subject', backref='class', lazy=True)
    exams = db.relationship('Exam', backref='class', lazy=True)
    students = db.relationship('Student', backref='class', lazy=True)


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    section_name = db.Column(db.String(5), nullable=False)
    students = db.relationship('Student', backref='section', lazy=True)
    exams = db.relationship('Exam', backref='section', lazy=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum('Admin', 'Teacher', name="user_roles"), nullable=False)
    has_dashboard_access = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    subjects = db.relationship('Subject', backref='teacher', lazy=True)
    
    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name="gender_types"), nullable=False)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    roll_number = db.Column(db.String(50), nullable=False)
    parent_contact = db.Column(db.String(20), nullable=False)
    attendance = db.relationship('Attendance', backref='student', lazy=True)
    marks = db.relationship('Mark', backref='student', lazy=True)
    parents = db.relationship('Parent', backref='student', lazy=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def calculate_total_marks(self, exam_id=None):
        """Calculate total marks for a specific exam or overall"""
        query = Mark.query.filter_by(student_id=self.id)
        if exam_id:
            query = query.filter_by(exam_id=exam_id)
        
        marks = query.all()
        total_obtained = sum(mark.marks_obtained for mark in marks)
        total_possible = sum(mark.total_marks for mark in marks)
        
        if total_possible == 0:
            return 0, 0, 0
        
        percentage = (total_obtained / total_possible) * 100
        return total_obtained, total_possible, round(percentage, 2)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    marks = db.relationship('Mark', backref='subject', lazy=True)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Present', 'Absent', 'Late', name="attendance_status"), nullable=False)
    remarks = db.Column(db.Text, nullable=True)


class Exam(db.Model):
    """Updated from Exams to Exam for consistency"""
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    exam_type = db.Column(db.Enum('Midterm', 'Final', 'Quiz', 'Assignment', name="exam_types"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    marks = db.relationship('Mark', backref='exam', lazy=True)
    
    def __repr__(self):
        return f"{self.name} ({self.exam_type})"


class Mark(db.Model):
    """Updated from Marks to Mark for consistency"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    
    @property
    def percentage(self):
        if self.total_marks == 0:
            return 0
        return (self.marks_obtained / self.total_marks) * 100
    
    @staticmethod
    def calculate_grade(percentage):
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'


class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    parent_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)