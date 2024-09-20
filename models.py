from app import db

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
