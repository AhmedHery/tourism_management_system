from flask import Flask, request, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_management.db'
db = SQLAlchemy(app)

# Model Definitions
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class TravelType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(100), nullable=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    national_id = db.Column(db.String(100), unique=True, nullable=False)
    passport_number = db.Column(db.String(100), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    down_payment = db.Column(db.Float, nullable=False)
    remaining_amount = db.Column(db.Float, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('clients', lazy=True))


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        employee = Employee.query.filter_by(username=username).first()
        if employee and check_password_hash(employee.password, password):
            session['user_id'] = employee.id
            if employee.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    employees = Employee.query.all()
    clients = []
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_employee':
            name = request.form.get('emp_name')
            username = request.form.get('emp_username')
            password = generate_password_hash(request.form.get('emp_password'))
            role = request.form.get('emp_role')
            new_employee = Employee(name=name, username=username, password=password, role=role)
            db.session.add(new_employee)
            db.session.commit()
        elif action == 'update_employee':
            emp_id = request.form.get('emp_id')
            new_name = request.form.get('new_emp_name')
            new_username = request.form.get('new_emp_username')
            new_role = request.form.get('new_emp_role')
            employee = Employee.query.get(emp_id)
            if new_name:
                employee.name = new_name
            if new_username:
                employee.username = new_username
            if new_role:
                employee.role = new_role
            db.session.commit()
        elif action == 'delete_employee':
            emp_id = request.form.get('emp_id')
            employee = Employee.query.get(emp_id)
            db.session.delete(employee)
            db.session.commit()
        elif action == 'search_client':
            national_id = request.form.get('search_national_id')
            clients = Client.query.filter_by(national_id=national_id).all()  # تأكد من وجود نموذج Client

        return render_template('admin_dashboard.html', employees=employees, clients=clients)

    return render_template('admin_dashboard.html', employees=employees)

@app.route('/employee_dashboard', methods=['GET', 'POST'])
def employee_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    employee = Employee.query.get(session['user_id'])
    clients = []

    if request.method == 'POST':
        action = request.form.get('action')
        
        # إضافة العميل
        if action == 'add_client':
            name = request.form.get('client_name')
            national_id = request.form.get('client_national_id')
            passport_number = request.form.get('client_passport_number')
            profession = request.form.get('client_profession')
            phone_number = request.form.get('client_phone_number')
            application_date = request.form.get('client_application_date')
            total_amount = float(request.form.get('client_total_amount'))
            down_payment = float(request.form.get('client_down_payment'))
            remaining_amount = total_amount - down_payment
            application_date = datetime.strptime(application_date, '%Y-%m-%d').date()

            new_client = Client(
                name=name,
                national_id=national_id,
                passport_number=passport_number,
                profession=profession,
                phone_number=phone_number,
                application_date=application_date,
                total_amount=total_amount,
                down_payment=down_payment,
                remaining_amount=remaining_amount,
                employee_id=employee.id
            )
            db.session.add(new_client)
            db.session.commit()

        # البحث عن عميل باستخدام الرقم القومي
        elif action == 'search_client':
            national_id = request.form.get('search_national_id')
            clients = Client.query.filter_by(national_id=national_id).all()

    if employee.role == 'admin':
        clients = Client.query.all() if not clients else clients
    else:
        clients = Client.query.filter_by(employee_id=employee.id).all() if not clients else clients

    return render_template('employee_dashboard.html', clients=clients)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Make sure the tables are created in the database
        if not Employee.query.filter_by(username='admin').first():
            admin_user = Employee(name='Admin User', username='admin', password=generate_password_hash('admin123', method='sha256'), role='admin')
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
