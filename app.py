import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Employee, ReportTemplate, DailyReport, KPITemplate, KPIRecord, ProductionPlan, Notification
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'furx-ops-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///furx_ops.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول أولاً'

@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))

# ============================================================
# NOTIFICATION SCHEDULER
# ============================================================
def check_missing_reports():
    """Runs at 2 PM daily — creates notifications for employees who haven't submitted."""
    with app.app_context():
        today = date.today()
        employees = Employee.query.filter_by(is_active=True).all()
        for emp in employees:
            templates = ReportTemplate.query.filter(
                ReportTemplate.is_active == True,
                ReportTemplate.is_daily == True,
                (ReportTemplate.department == emp.department) | (ReportTemplate.department == 'all')
            ).all()
            for tmpl in templates:
                submitted = DailyReport.query.filter_by(
                    employee_id=emp.id, template_id=tmpl.id, report_date=today
                ).first()
                if not submitted:
                    existing_notif = Notification.query.filter_by(
                        employee_id=emp.id, notif_type='reminder',
                    ).filter(db.func.date(Notification.created_at) == today).first()
                    if not existing_notif:
                        notif = Notification(
                            employee_id=emp.id,
                            title='تذكير: تقرير لم يُسلّم',
                            message=f'لم تقم بتسليم تقرير "{tmpl.name_ar}" اليوم بعد. يرجى التسليم قبل نهاية اليوم.',
                            notif_type='reminder',
                            link='/reports/submit'
                        )
                        db.session.add(notif)
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_missing_reports, trigger='cron', hour=14, minute=0)
scheduler.start()

# ============================================================
# AUTH ROUTES
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = Employee.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('بيانات الدخول غير صحيحة', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ============================================================
# DASHBOARD
# ============================================================
@app.route('/')
@login_required
def dashboard():
    today = date.today()
    # Get templates for this employee's department
    templates = ReportTemplate.query.filter(
        ReportTemplate.is_active == True,
        (ReportTemplate.department == current_user.department) | (ReportTemplate.department == 'all')
    ).all()
    # Check which are submitted today
    submitted_ids = [r.template_id for r in DailyReport.query.filter_by(
        employee_id=current_user.id, report_date=today
    ).all()]
    # Pending KPIs
    pending_kpis = KPIRecord.query.filter_by(employee_id=current_user.id, status='pending').all()
    # Unread notifications
    notifs = Notification.query.filter_by(employee_id=current_user.id, is_read=False).order_by(
        Notification.created_at.desc()).limit(10).all()
    # Recent reports
    recent_reports = DailyReport.query.filter_by(employee_id=current_user.id).order_by(
        DailyReport.submitted_at.desc()).limit(5).all()
    # Production plans (if production role)
    today_plans = []
    if current_user.department in ['الإنتاج', 'production', 'all']:
        today_plans = ProductionPlan.query.filter_by(plan_date=today).all()

    return render_template('dashboard.html',
        templates=templates, submitted_ids=submitted_ids,
        pending_kpis=pending_kpis, notifications=notifs,
        recent_reports=recent_reports, today_plans=today_plans,
        today=today)

# ============================================================
# DAILY REPORTS
# ============================================================
@app.route('/reports/submit', methods=['GET', 'POST'])
@login_required
def submit_report():
    templates = ReportTemplate.query.filter(
        ReportTemplate.is_active == True,
        (ReportTemplate.department == current_user.department) | (ReportTemplate.department == 'all')
    ).all()
    if request.method == 'POST':
        template_id = request.form.get('template_id', type=int)
        tmpl = ReportTemplate.query.get_or_404(template_id)
        # Collect form data based on template fields
        report_data = {}
        for field in tmpl.fields:
            field_key = field['key']
            if field['type'] == 'checkbox':
                report_data[field_key] = request.form.get(field_key) == 'on'
            elif field['type'] == 'number':
                val = request.form.get(field_key, '0')
                report_data[field_key] = float(val) if val else 0
            else:
                report_data[field_key] = request.form.get(field_key, '')

        report = DailyReport(
            employee_id=current_user.id,
            template_id=template_id,
            report_date=date.today(),
            notes=request.form.get('notes', '')
        )
        report.data = report_data
        db.session.add(report)
        # Mark reminder notifications as read
        Notification.query.filter_by(
            employee_id=current_user.id, notif_type='reminder', is_read=False
        ).update({'is_read': True})
        db.session.commit()
        flash('تم تسليم التقرير بنجاح', 'success')
        return redirect(url_for('dashboard'))

    today = date.today()
    submitted_ids = [r.template_id for r in DailyReport.query.filter_by(
        employee_id=current_user.id, report_date=today).all()]
    return render_template('submit_report.html', templates=templates, submitted_ids=submitted_ids)

@app.route('/reports/history')
@login_required
def report_history():
    page = request.args.get('page', 1, type=int)
    reports = DailyReport.query.filter_by(employee_id=current_user.id).order_by(
        DailyReport.submitted_at.desc()).paginate(page=page, per_page=20)
    return render_template('report_history.html', reports=reports)

@app.route('/reports/view/<int:report_id>')
@login_required
def view_report(report_id):
    report = DailyReport.query.get_or_404(report_id)
    if report.employee_id != current_user.id and not current_user.is_admin:
        # Check if current user is the manager
        emp = Employee.query.get(report.employee_id)
        if emp.reports_to_id != current_user.id:
            flash('ليس لديك صلاحية مشاهدة هذا التقرير', 'error')
            return redirect(url_for('dashboard'))
    return render_template('view_report.html', report=report)

# ============================================================
# KPI TRACKING
# ============================================================
@app.route('/kpi')
@login_required
def kpi_list():
    records = KPIRecord.query.filter_by(employee_id=current_user.id).order_by(
        KPIRecord.period_start.desc()).all()
    return render_template('kpi_list.html', records=records)

@app.route('/kpi/submit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def kpi_submit(record_id):
    record = KPIRecord.query.get_or_404(record_id)
    if record.employee_id != current_user.id:
        flash('ليس لديك صلاحية', 'error')
        return redirect(url_for('kpi_list'))

    if request.method == 'POST':
        scores = {}
        total = 0
        items = record.template.items
        for item in items:
            key = item['key']
            val = request.form.get(key, '0')
            score = min(float(val) if val else 0, item.get('max_score', 100))
            scores[key] = score
            total += score * (item.get('weight', 1) / 100)
        record.scores = scores
        record.total_score = round(total, 1)
        record.performance_grade = record.calculate_grade()
        record.status = 'self_assessed'
        record.submitted_at = datetime.utcnow()
        record.notes = request.form.get('notes', '')
        db.session.commit()
        flash('تم تسجيل التقييم بنجاح', 'success')
        return redirect(url_for('kpi_list'))

    return render_template('kpi_submit.html', record=record)

# ============================================================
# PRODUCTION PLANNING
# ============================================================
@app.route('/production')
@login_required
def production_plans():
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    plans = ProductionPlan.query.filter(
        ProductionPlan.plan_date >= week_start
    ).order_by(ProductionPlan.plan_date).all()
    return render_template('production.html', plans=plans, today=today)

@app.route('/production/create', methods=['GET', 'POST'])
@login_required
def create_production_plan():
    if request.method == 'POST':
        plan_date = datetime.strptime(request.form.get('plan_date'), '%Y-%m-%d').date()
        line = request.form.get('line')
        items = []
        i = 0
        while f'product_{i}' in request.form:
            product = request.form.get(f'product_{i}')
            qty = request.form.get(f'qty_{i}', '0')
            priority = request.form.get(f'priority_{i}', 'normal')
            if product:
                items.append({'product': product, 'qty': int(qty) if qty else 0, 'priority': priority})
            i += 1

        plan = ProductionPlan(
            plan_date=plan_date, line=line,
            created_by_id=current_user.id,
            notes=request.form.get('notes', '')
        )
        plan.plan_data = {'items': items}
        db.session.add(plan)
        db.session.commit()
        flash('تم إنشاء خطة الإنتاج بنجاح', 'success')
        return redirect(url_for('production_plans'))

    lines = [
        {'id': 'bedroom_dining', 'name': 'خط نوم وسفرة'},
        {'id': 'upholstery', 'name': 'خط التنجيد'},
        {'id': 'custom', 'name': 'خط الكاستميز'},
    ]
    return render_template('create_plan.html', lines=lines)

@app.route('/production/update/<int:plan_id>', methods=['POST'])
@login_required
def update_production_actual(plan_id):
    plan = ProductionPlan.query.get_or_404(plan_id)
    items = []
    i = 0
    while f'actual_qty_{i}' in request.form:
        qty = request.form.get(f'actual_qty_{i}', '0')
        items.append({'qty': int(qty) if qty else 0})
        i += 1
    plan.actual_data = {'items': items}
    plan.status = 'completed' if request.form.get('mark_complete') else 'in_progress'
    db.session.commit()
    flash('تم تحديث الفعلي بنجاح', 'success')
    return redirect(url_for('production_plans'))

# ============================================================
# NOTIFICATIONS
# ============================================================
@app.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(employee_id=current_user.id).order_by(
        Notification.created_at.desc()).limit(50).all()
    return render_template('notifications.html', notifications=notifs)

@app.route('/notifications/read/<int:notif_id>', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.employee_id == current_user.id:
        notif.is_read = True
        db.session.commit()
    return jsonify({'ok': True})

@app.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(employee_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/notifications/count')
@login_required
def notification_count():
    count = Notification.query.filter_by(employee_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

# ============================================================
# ADMIN ROUTES
# ============================================================
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية الوصول', 'error')
        return redirect(url_for('dashboard'))
    today = date.today()
    employees = Employee.query.filter_by(is_active=True).all()
    # Submission status for today
    submission_status = []
    for emp in employees:
        templates = ReportTemplate.query.filter(
            ReportTemplate.is_active == True, ReportTemplate.is_daily == True,
            (ReportTemplate.department == emp.department) | (ReportTemplate.department == 'all')
        ).all()
        submitted = DailyReport.query.filter_by(employee_id=emp.id, report_date=today).count()
        total = len(templates)
        submission_status.append({
            'employee': emp,
            'submitted': submitted,
            'total': total,
            'complete': submitted >= total if total > 0 else True
        })
    # Today's production plans
    plans = ProductionPlan.query.filter_by(plan_date=today).all()
    # Recent KPI records
    kpi_records = KPIRecord.query.filter_by(status='self_assessed').order_by(
        KPIRecord.submitted_at.desc()).limit(10).all()
    return render_template('admin_dashboard.html',
        submission_status=submission_status, plans=plans,
        kpi_records=kpi_records, today=today, employees=employees)

@app.route('/admin/employees')
@login_required
def admin_employees():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية', 'error')
        return redirect(url_for('dashboard'))
    employees = Employee.query.order_by(Employee.department, Employee.name_ar).all()
    return render_template('admin_employees.html', employees=employees)

@app.route('/admin/employee/<int:emp_id>')
@login_required
def admin_employee_detail(emp_id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية', 'error')
        return redirect(url_for('dashboard'))
    emp = Employee.query.get_or_404(emp_id)
    reports = DailyReport.query.filter_by(employee_id=emp_id).order_by(
        DailyReport.submitted_at.desc()).limit(30).all()
    kpis = KPIRecord.query.filter_by(employee_id=emp_id).order_by(
        KPIRecord.period_start.desc()).limit(10).all()
    return render_template('admin_employee_detail.html', emp=emp, reports=reports, kpis=kpis)

@app.route('/admin/reports/all')
@login_required
def admin_all_reports():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية', 'error')
        return redirect(url_for('dashboard'))
    report_date = request.args.get('date', date.today().isoformat())
    target_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    reports = DailyReport.query.filter_by(report_date=target_date).order_by(
        DailyReport.submitted_at.desc()).all()
    return render_template('admin_all_reports.html', reports=reports, target_date=target_date)

@app.route('/admin/send-reminder', methods=['POST'])
@login_required
def send_reminder():
    if not current_user.is_admin:
        return jsonify({'error': 'unauthorized'}), 403
    emp_id = request.form.get('employee_id', type=int)
    notif = Notification(
        employee_id=emp_id,
        title='تذكير عاجل من الإدارة',
        message='يرجى تسليم التقرير اليومي فوراً. الإدارة في انتظار بياناتك.',
        notif_type='urgent',
        link='/reports/submit'
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({'ok': True, 'message': 'تم إرسال التذكير'})

@app.route('/admin/kpi/review/<int:record_id>', methods=['POST'])
@login_required
def admin_kpi_review(record_id):
    if not current_user.is_admin:
        return jsonify({'error': 'unauthorized'}), 403
    record = KPIRecord.query.get_or_404(record_id)
    action = request.form.get('action')
    if action == 'approve':
        record.status = 'final'
        record.reviewed_by_id = current_user.id
    elif action == 'adjust':
        new_score = request.form.get('adjusted_score', type=float)
        if new_score is not None:
            record.total_score = new_score
            record.performance_grade = record.calculate_grade()
        record.status = 'final'
        record.reviewed_by_id = current_user.id
    db.session.commit()
    flash('تم مراجعة التقييم', 'success')
    return redirect(url_for('admin_dashboard'))

# ============================================================
# PROFILE
# ============================================================
@app.route('/profile')
@login_required
def profile():
    reports_count = DailyReport.query.filter_by(employee_id=current_user.id).count()
    kpi_avg = db.session.query(db.func.avg(KPIRecord.total_score)).filter_by(
        employee_id=current_user.id, status='final').scalar() or 0
    return render_template('profile.html', reports_count=reports_count, kpi_avg=round(kpi_avg, 1))

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    old_pw = request.form.get('old_password')
    new_pw = request.form.get('new_password')
    if current_user.check_password(old_pw):
        current_user.set_password(new_pw)
        db.session.commit()
        flash('تم تغيير كلمة المرور بنجاح', 'success')
    else:
        flash('كلمة المرور الحالية غير صحيحة', 'error')
    return redirect(url_for('profile'))

# ============================================================
# MANAGER VIEWS (for supervisors)
# ============================================================
@app.route('/team')
@login_required
def team_reports():
    """View direct reports' submission status."""
    today = date.today()
    team = Employee.query.filter_by(reports_to_id=current_user.id, is_active=True).all()
    if not team:
        flash('لا يوجد لديك فريق مباشر', 'info')
        return redirect(url_for('dashboard'))
    team_status = []
    for member in team:
        today_reports = DailyReport.query.filter_by(employee_id=member.id, report_date=today).all()
        team_status.append({
            'employee': member,
            'submitted': len(today_reports),
            'reports': today_reports
        })
    return render_template('team_reports.html', team_status=team_status, today=today)

# ============================================================
# INIT DB & SEED
# ============================================================
@app.cli.command('init-db')
def init_db():
    """Initialize database and seed data."""
    db.create_all()
    from seed import seed_data
    seed_data(db)
    print('Database initialized and seeded.')

@app.cli.command('create-notifications')
def create_notifications_cmd():
    """Manually trigger notification check."""
    check_missing_reports()
    print('Notifications created for missing reports.')

# Auto-create tables on first run
with app.app_context():
    db.create_all()
    # Auto-seed if empty
    if Employee.query.count() == 0:
        try:
            from seed import seed_data
            seed_data(db)
            print('Auto-seeded database with FURX employees.')
        except Exception as e:
            print(f'Seed error: {e}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
