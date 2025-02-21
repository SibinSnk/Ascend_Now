from flask import render_template, redirect, flash, url_for, request, get_flashed_messages,jsonify
from dashboard.helpers import register_validations
from flask_login import login_user, login_required, logout_user, current_user
from email_validator import validate_email, EmailNotValidError
from dashboard import app,bcrypt,db
from dashboard.models import *
from datetime import datetime
import re


@app.route("/",methods=['GET', 'POST'])
def dashboard_login():
    get_flashed_messages()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            user.is_active = True
            db.session.commit()
            login_user(user,remember=True)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('dashboard_login'))
    
    teachers = User.query.filter_by(role='Teacher').all()
    students = Student.query.all()
    parents = Parent.query.all()
    return render_template('index.html', teachers=teachers, students=students, parents=parents)


@app.route('/logout')
@login_required
def logout_dashboard():
    current_user.is_active = False
    db.session.commit()
    logout_user()
    return redirect(url_for('dashboard_login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        phone = request.form.get("phone")
        role = request.form.get("role")
        confirm_password = request.form.get('confirm_password')
        school_id = request.form.get("school_id")

        try:
            validate_email(email, check_deliverability=False)

        except EmailNotValidError:
            flash('Invalid email format.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please log in.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[@$!%*?&]', password):
            flash('Password must be at least 8 characters long, include an uppercase letter, a number, and a special character.', 'danger')
            return redirect(url_for('register'))
        
        if not phone.isdigit():
            flash('Phone number should be digits.', 'danger')
            return redirect(url_for('register')) 

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        if role not in ['Admin', 'Teacher']:
            flash('Invalid role selection.', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            email=email, 
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            password_hash=hashed_password,
            school_id=school_id,
            has_dashboard_access=True
            )
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('dashboard_login'))

    schools = School.query.all()
    return render_template('register.html',schools=schools)



@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if not current_user.is_authenticated:
        flash('You must be logged in to add a teacher.', 'danger')
        return redirect(url_for('dashboard_login'))

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get("phone")
        role = request.form.get("role")
        school_id = request.form.get("school_id")

        try:
            validate_email(email, check_deliverability=False)

        except EmailNotValidError:
            flash('Invalid email format.', 'danger')
            return redirect(url_for('add_teacher'))
        
        if User.query.filter_by(email=email).first():
            flash('User with same email exists.', 'danger')
            return redirect(url_for('add_teacher'))\

        user = User(
            email=email, 
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            school_id=school_id
            )
        db.session.add(user)
        db.session.commit()
        flash(f'{role} added successfuly', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_teacher.html')


@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    classes = Class.query.all()
    sections = Section.query.all()
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob_str = request.form.get("dob")
        gender = request.form.get("gender")
        admission_number = request.form.get("admission_number")
        roll_number = request.form.get("roll_number")
        parent_contact = request.form.get("parent_contact")
        class_id = request.form.get("class_id")
        section_id = request.form.get("section_id")

        if not parent_contact.isdigit():
            flash('Phone number should be digits.', 'danger')
            return redirect(url_for('add_student')) 
        
        class_obj = Class.query.get(class_id)
        if not class_obj:
            flash('Invalid class selected.', 'danger')
            return redirect(url_for('add_student'))
        
        school_id = class_obj.school_id
        existing_admission = Student.query.filter_by(admission_number=admission_number).first()
        if existing_admission:
            flash('A student with the same admission number already exists.', 'danger')
            return redirect(url_for('add_student'))

        existing_roll = Student.query.filter_by(roll_number=roll_number, class_id=class_id, section_id=section_id).first()
        if existing_roll:
            flash('A student with the same roll number already exists in this class and section.', 'danger')
            return redirect(url_for('add_student'))
        
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        student = Student(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            gender=gender,
            admission_number=admission_number,
            roll_number=roll_number,
            parent_contact=parent_contact,
            school_id=school_id,
            class_id=class_id,
            section_id=section_id
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfuly', 'success')
        return redirect(url_for('dashboard')) 

    return render_template('add_student.html',classes=classes,sections=sections)


@app.route('/add_parent', methods=['GET', 'POST'])
@login_required
def add_parent():
    if request.method == 'POST':
        parent_name = request.form.get('parent_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        admission_num = request.form.get("admission_number")
        student = Student.query.filter_by(admission_number=admission_num,school_id=current_user.school_id).first()
        if not student:
            flash('Student with this admission number does not exist.', 'danger')
            return redirect(url_for('add_parent')) 
        
        if not phone.isdigit():
            flash('Phone number should be digits.', 'danger')
            return redirect(url_for('add_parent')) 
        parent =  Parent(
            parent_name=parent_name,
            email=email,
            phone=phone,
            student_id=student.id
        )
        db.session.add(parent)
        db.session.commit()
        flash('Parent details added successfuly', 'success')
        return redirect(url_for('dashboard')) 

    return render_template('add_parent.html')


@app.route('/dashboard/edit/teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    if not current_user.is_authenticated:
        flash('You must be logged in to edit a teacher.', 'danger')
        return redirect(url_for('dashboard_login'))
    
    teacher = User.query.get_or_404(teacher_id)

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        try:
            validate_email(email, check_deliverability=False)

        except EmailNotValidError:
            flash('Invalid email format.', 'danger')
            return redirect(url_for('edit_teacher', teacher_id=teacher_id))
        
        existing_user = User.query.filter(User.email == email, User.id != teacher_id).first()
        if existing_user:
            flash('User with this email already exists.', 'danger')
            return redirect(url_for('edit_teacher', teacher_id=teacher_id))
        
        teacher.email = email
        teacher.first_name = first_name
        teacher.last_name = last_name
        teacher.phone = phone
        
        db.session.commit()
        flash('Teacher details updated successfuly.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_teacher.html', teacher=teacher)



@app.route('/dashboard/delete/teacher/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = User.query.filter_by(id=teacher_id, role='Teacher').first()
    
    if not teacher:
        flash('Teacher not found.', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(teacher)
    db.session.commit()
    
    flash('Teacher deleted successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    classes = Class.query.all()
    sections = Section.query.all()

    if request.method == 'POST':
        student.first_name = request.form.get('first_name')
        student.last_name = request.form.get('last_name')
        student.dob = datetime.strptime(request.form.get("dob"), "%Y-%m-%d").date()
        student.gender = request.form.get("gender")
        student.admission_number = request.form.get("admission_number")
        student.roll_number = request.form.get("roll_number")
        student.parent_contact = request.form.get("parent_contact")
        student.class_id = request.form.get("class_id")
        student.section_id = request.form.get("section_id")

        if not student.parent_contact.isdigit():
            flash('Phone number should be digits.', 'danger')
            return redirect(url_for('edit_student', student_id=student_id)) 

        db.session.commit()
        flash('Student details updated successfully!', 'success')
        return redirect(url_for('dashboard'))  

    return render_template('edit_student.html', student=student, classes=classes, sections=sections)


@app.route('/dashboard/delete/student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.filter_by(id=student_id).first()
    
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(student)
    db.session.commit()
    
    flash('Student deleted successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/edit_parent/<int:parent_id>', methods=['GET', 'POST'])
@login_required
def edit_parent(parent_id):
    parent = Parent.query.get_or_404(parent_id)
    student = Student.query.filter_by(id=parent.student_id).first()

    if request.method == 'POST':
        parent_name = request.form.get('parent_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        admission_num = request.form.get("admission_number")

        if not phone.isdigit():
            flash('Phone number should be digits.', 'danger')
            return redirect(url_for('edit_parent', parent_id=parent_id)) 
        
        
        student = Student.query.filter_by(admission_number=admission_num,school_id=current_user.school_id).first()
        if not student:
            flash('Student with this admission number does not exist.', 'danger')
            return redirect(url_for('add_parent')) 

        parent.parent_name = parent_name
        parent.email = email
        parent.phone = phone
        parent.student_id=student.id

        db.session.commit()
        flash('Parent details updated successfully', 'success')
        return redirect(url_for('dashboard'))  

    return render_template('edit_parent.html', parent=parent,student=student)


@app.route('/dashboard/delete/parent/<int:parent_id>', methods=['GET', 'POST'])
@login_required
def delete_parent(parent_id):
    parent = Parent.query.filter_by(id=parent_id).first()
    
    if not parent:
        flash('Parent not found.', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(parent)
    db.session.commit()
    
    flash('Parent deleted successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/dashboard/teachers', methods=['GET', 'POST'])
@login_required
def view_teachers():
    teachers = User.query.filter_by(role='Teacher').all()
    return render_template("view_teachers.html",teachers=teachers)


@app.route('/dashboard/students', methods=['GET', 'POST'])
@login_required
def view_students():
    students = Student.query.all()
    return render_template("view_students.html",students=students)


@app.route('/dashboard/parents', methods=['GET', 'POST'])
@login_required
def view_parents():
    parents = Parent.query.all()
    return render_template("view_parents.html",parents=parents)


@app.route('/mark_attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    classes = Class.query.all()
    sections = Section.query.all()

    if request.method == 'POST':
        date = request.form.get('date')
        class_id = request.form.get('class_id')
        section_id = request.form.get('section_id')

        for student in Student.query.filter_by(class_id=class_id, section_id=section_id).all():
            status = request.form.get(f"status_{student.id}")
            attendance = Attendance(
                student_id=student.id,
                date=datetime.strptime(date, "%Y-%m-%d").date(),
                status=status
            )
            db.session.add(attendance)

        db.session.commit()
        flash("Attendance marked successfully!", "success")
        return redirect(url_for('mark_attendance'))

    return render_template('attendance.html', classes=classes, sections=sections)


@app.route('/dashboard/students/attendance/<int:student_id>', methods=['GET'])
def view_attendance(student_id):
    student = Student.query.get_or_404(student_id)
    students_attendance = Attendance.query.filter_by(student_id=student_id).all()
    return render_template("view_attendance.html", student=student, attendance=students_attendance)


@app.route('/get_students', methods=['GET'])
@login_required
def get_students():
    class_id = request.args.get('class_id')
    section_id = request.args.get('section_id')

    students = Student.query.filter_by(class_id=class_id, section_id=section_id).all()
    student_list = [{"id": student.id, "name": f"{student.first_name} {student.last_name}"} for student in students]

    return jsonify(student_list)



@app.route('/enter_marks', methods=['GET', 'POST'])
@login_required
def enter_marks():
    subjects = Subject.query.all()
    students = Student.query.all()
    if request.method == 'POST':
        pass
    return render_template('marks.html', subjects=subjects, students=students)
