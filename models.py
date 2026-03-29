from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json

db = SQLAlchemy()

class Employee(UserMixin, db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(100), nullable=False)  # job title
    department = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), default='G1')  # G1-G5
    phone = db.Column(db.String(20))
    reports_to_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reports_to = db.relationship('Employee', remote_side=[id], backref='direct_reports')
    daily_reports = db.relationship('DailyReport', backref='employee', lazy='dynamic')
    kpi_records = db.relationship('KPIRecord', backref='employee', lazy='dynamic')
    notifications = db.relationship('Notification', backref='employee', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def has_submitted_today(self):
        today = date.today()
        return self.daily_reports.filter(
            db.func.date(DailyReport.submitted_at) == today
        ).first() is not None

    @property
    def pending_kpis(self):
        return self.kpi_records.filter_by(status='pending').count()


class ReportTemplate(db.Model):
    __tablename__ = 'report_templates'
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    department = db.Column(db.String(100), nullable=False)
    role_filter = db.Column(db.String(200))  # comma-separated roles, or 'all'
    fields_json = db.Column(db.Text, nullable=False)  # JSON array of field definitions
    is_daily = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)

    @property
    def fields(self):
        return json.loads(self.fields_json)

    @fields.setter
    def fields(self, value):
        self.fields_json = json.dumps(value, ensure_ascii=False)


class DailyReport(db.Model):
    __tablename__ = 'daily_reports'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('report_templates.id'), nullable=False)
    report_date = db.Column(db.Date, nullable=False, default=date.today)
    data_json = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='submitted')  # submitted, reviewed, flagged
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    template = db.relationship('ReportTemplate')
    reviewer = db.relationship('Employee', foreign_keys=[reviewed_by_id])

    @property
    def data(self):
        return json.loads(self.data_json)

    @data.setter
    def data(self, value):
        self.data_json = json.dumps(value, ensure_ascii=False)


class KPITemplate(db.Model):
    __tablename__ = 'kpi_templates'
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), nullable=False)  # G1-G5
    department = db.Column(db.String(100))
    items_json = db.Column(db.Text, nullable=False)
    period = db.Column(db.String(20), default='weekly')  # daily, weekly, monthly
    is_active = db.Column(db.Boolean, default=True)

    @property
    def items(self):
        return json.loads(self.items_json)

    @items.setter
    def items(self, value):
        self.items_json = json.dumps(value, ensure_ascii=False)


class KPIRecord(db.Model):
    __tablename__ = 'kpi_records'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('kpi_templates.id'), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    scores_json = db.Column(db.Text)  # JSON: {item_id: score}
    total_score = db.Column(db.Float, default=0)
    performance_grade = db.Column(db.String(5))  # A, B, C, D, E
    status = db.Column(db.String(20), default='pending')  # pending, self_assessed, manager_reviewed, final
    notes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)

    template = db.relationship('KPITemplate')

    @property
    def scores(self):
        return json.loads(self.scores_json) if self.scores_json else {}

    @scores.setter
    def scores(self, value):
        self.scores_json = json.dumps(value, ensure_ascii=False)

    def calculate_grade(self):
        if self.total_score >= 90: return 'A'
        elif self.total_score >= 80: return 'B'
        elif self.total_score >= 70: return 'C'
        elif self.total_score >= 60: return 'D'
        else: return 'E'


class ProductionPlan(db.Model):
    __tablename__ = 'production_plans'
    id = db.Column(db.Integer, primary_key=True)
    plan_date = db.Column(db.Date, nullable=False)
    line = db.Column(db.String(50), nullable=False)  # bedroom_dining, upholstery, custom
    plan_data_json = db.Column(db.Text, nullable=False)
    actual_data_json = db.Column(db.Text)
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed
    created_by_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    created_by = db.relationship('Employee')

    @property
    def plan_data(self):
        return json.loads(self.plan_data_json)

    @plan_data.setter
    def plan_data(self, value):
        self.plan_data_json = json.dumps(value, ensure_ascii=False)

    @property
    def actual_data(self):
        return json.loads(self.actual_data_json) if self.actual_data_json else {}

    @actual_data.setter
    def actual_data(self, value):
        self.actual_data_json = json.dumps(value, ensure_ascii=False)

    @property
    def achievement_pct(self):
        plan = self.plan_data
        actual = self.actual_data
        if not actual or not plan:
            return 0
        plan_total = sum(item.get('qty', 0) for item in plan.get('items', []))
        actual_total = sum(item.get('qty', 0) for item in actual.get('items', []))
        return round((actual_total / plan_total * 100), 1) if plan_total > 0 else 0


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notif_type = db.Column(db.String(30), default='info')  # info, warning, urgent, reminder
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(200))
