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



# @app.route('/enter_marks', methods=['GET', 'POST'])
# @login_required
# def enter_marks():
#     subjects = Subject.query.all()
#     students = Student.query.all()
#     if request.method == 'POST':
#         pass
#     return render_template('marks.html', subjects=subjects, students=students)
    

# @app.route('/enter_marks_bulk', methods=['GET', 'POST'])
# @login_required
# def enter_marks_bulk():
#     students = Student.query.all()
#     subjects = Subject.query.all()

#     if request.method == 'POST':
#         exam_type = request.form.get('exam_type')

#         # These will come in parallel lists, one entry per row in the table
#         student_ids = request.form.getlist('student_ids[]')
#         subject_ids = request.form.getlist('subject_ids[]')
#         marks_obtained = request.form.getlist('marks_obtained[]')
#         total_marks = request.form.getlist('total_marks[]')
        
#         for i in range(len(student_ids)):
#             new_mark = Mark(
#                 student_id=student_ids[i],
#                 subject_id=subject_ids[i],
#                 exam_type=exam_type,
#                 marks_obtained=marks_obtained[i],
#                 total_marks=total_marks[i],
#                 grade='N/A'
#             )
#             db.session.add(new_mark)

#         db.session.commit()
#         flash("Marks successfully entered!", "success")
#         return redirect(url_for('dashboard'))

#     return render_template('add_marks.html', students=students, subjects=subjects)
    

#########################################################


@app.route('/exams', methods=['GET'])
@login_required
def exams():
    """View all exams"""
    exams = Exam.query.all()
    return render_template('exams/index.html', exams=exams)


@app.route('/exams/create', methods=['GET', 'POST'])
@login_required
def create_exam():
    """Create a new exam"""
    classes = Class.query.all()
    sections = Section.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        class_id = request.form.get('class_id')
        section_id = request.form.get('section_id')
        exam_type = request.form.get('exam_type')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        
        exam = Exam(
            name=name,
            class_id=class_id,
            section_id=section_id,
            exam_type=exam_type,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        db.session.add(exam)
        db.session.commit()
        
        flash('Exam created successfully!', 'success')
        return redirect(url_for('exams'))
    
    return render_template('exams/create.html', classes=classes,sections=sections)


@app.route('/exams/<int:exam_id>', methods=['GET'])
@login_required
def view_exam(exam_id):
    """View exam details and results"""
    exam = Exam.query.get_or_404(exam_id)
    subjects = Subject.query.filter_by(class_id=exam.class_id).all()
    students = Student.query.filter_by(class_id=exam.class_id).all()
    results = {}
    for student in students:
        student_marks = Mark.query.filter_by(exam_id=exam_id, student_id=student.id).all()
        total_obtained, total_possible, percentage = student.calculate_total_marks(exam_id)
        
        subject_marks = {}
        for subject in subjects:
            mark = next((m for m in student_marks if m.subject_id == subject.id), None)
            if mark:
                subject_marks[subject.id] = mark
            else:
                subject_marks[subject.id] = None
        
        results[student.id] = {
            'student': student,
            'subject_marks': subject_marks,
            'total_obtained': total_obtained,
            'total_possible': total_possible,
            'percentage': percentage,
            'grade': Mark.calculate_grade(percentage)
        }
    
    return render_template('exams/view.html', 
                          exam=exam, 
                          subjects=subjects, 
                          results=results)


@app.route('/marks/enter/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def enter_marks(exam_id):
    """Enter marks for a specific exam"""
    exam = Exam.query.get_or_404(exam_id)
    subjects = Subject.query.filter_by(class_id=exam.class_id).all()
    sections = Section.query.filter_by(class_id=exam.class_id).all()
    selected_section = request.args.get('section_id', type=int)
    selected_subject = request.args.get('subject_id', type=int)
    
    if selected_section:
        students = Student.query.filter_by(section_id=selected_section).all()
    else:
        students = Student.query.filter_by(class_id=exam.class_id).all()
    
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        
        for student in students:
            marks_obtained = request.form.get(f'marks_obtained_{student.id}')
            total_marks = request.form.get(f'total_marks_{student.id}')
            
            if marks_obtained and total_marks:
                marks_obtained = float(marks_obtained)
                total_marks = float(total_marks)
                percentage = (marks_obtained / total_marks) * 100 if total_marks > 0 else 0
                grade = Mark.calculate_grade(percentage)

                existing_mark = Mark.query.filter_by(
                    student_id=student.id,
                    subject_id=subject_id,
                    exam_id=exam_id
                ).first()
                
                if existing_mark:
                    existing_mark.marks_obtained = marks_obtained
                    existing_mark.total_marks = total_marks
                    existing_mark.grade = grade
                else:
                    new_mark = Mark(
                        student_id=student.id,
                        subject_id=subject_id,
                        exam_id=exam_id,
                        marks_obtained=marks_obtained,
                        total_marks=total_marks,
                        grade=grade
                    )
                    db.session.add(new_mark)
        
        db.session.commit()
        flash("Marks successfully entered!", "success")
        return redirect(url_for('view_exam', exam_id=exam_id))

    existing_marks = {}
    if selected_subject:
        for student in students:
            mark = Mark.query.filter_by(
                student_id=student.id,
                subject_id=selected_subject,
                exam_id=exam_id
            ).first()
            if mark:
                existing_marks[student.id] = mark
    
    return render_template('exams/enter.html', 
                          exam=exam, 
                          subjects=subjects, 
                          sections=sections,
                          selected_section=selected_section,
                          selected_subject=selected_subject,
                          students=students,
                          existing_marks=existing_marks)


@app.route('/marks/report/<int:student_id>', methods=['GET'])
@login_required
def student_marks_report(student_id):
    """Generate a report of all marks for a student"""
    student = Student.query.get_or_404(student_id)
    exams = Exam.query.filter_by(class_id=student.class_id).all()
    subjects = Subject.query.filter_by(class_id=student.class_id).all()

    marks_by_exam = {}
    for exam in exams:
        subject_marks = {}
        for subject in subjects:
            mark = Mark.query.filter_by(
                student_id=student_id,
                subject_id=subject.id,
                exam_id=exam.id
            ).first()
            subject_marks[subject.id] = mark
        
        total_obtained, total_possible, percentage = student.calculate_total_marks(exam.id)
        marks_by_exam[exam.id] = {
            'subject_marks': subject_marks,
            'total_obtained': total_obtained,
            'total_possible': total_possible,
            'percentage': percentage,
            'grade': Mark.calculate_grade(percentage)
        }
    
    overall_obtained, overall_possible, overall_percentage = student.calculate_total_marks()
    return render_template('exams/report.html',
                          student=student,
                          exams=exams,
                          subjects=subjects,
                          marks_by_exam=marks_by_exam,
                          overall_obtained=overall_obtained,
                          overall_possible=overall_possible,
                          overall_percentage=overall_percentage,
                          overall_grade=Mark.calculate_grade(overall_percentage))


@app.route('/marks/class_report/<int:class_id>', methods=['GET'])
@login_required
def class_marks_report(class_id):
    """Generate a report of all marks for a class"""
    class_obj = Class.query.get_or_404(class_id)
    exams = Exam.query.filter_by(class_id=class_id).all()
    sections = Section.query.filter_by(class_id=class_id).all()
    selected_exam = request.args.get('exam_id', type=int)
    selected_section = request.args.get('section_id', type=int)
    
    if selected_section:
        students = Student.query.filter_by(section_id=selected_section).all()
    else:
        students = Student.query.filter_by(class_id=class_id).all()
    
    results = []
    if selected_exam:
        exam = Exam.query.get(selected_exam)
        subjects = Subject.query.filter_by(class_id=class_id).all()
        
        for student in students:
            total_obtained, total_possible, percentage = student.calculate_total_marks(selected_exam)
            
            results.append({
                'student': student,
                'total_obtained': total_obtained,
                'total_possible': total_possible,
                'percentage': percentage,
                'grade': Mark.calculate_grade(percentage)
            })
        
        results.sort(key=lambda x: x['percentage'], reverse=True)
        if results:
            class_average = sum(r['percentage'] for r in results) / len(results)
        else:
            class_average = 0
    else:
        exam = None
        subjects = []
        class_average = 0
    
    return render_template('exams/class_report.html',
                          class_obj=class_obj,
                          exams=exams,
                          sections=sections,
                          selected_exam=selected_exam,
                          selected_section=selected_section,
                          subjects=subjects,
                          results=results,
                          class_average=class_average)