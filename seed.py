"""Seed FURX OPS database with real employees, templates, and KPI structures."""
from models import Employee, ReportTemplate, KPITemplate, KPIRecord
from datetime import date, timedelta
import json

def seed_data(db):
    # ============================================================
    # EMPLOYEES
    # ============================================================
    employees_data = [
        # Admin / Management
        {"name_ar": "هادي الدجيدي", "name_en": "Hady Eldeghidi", "email": "hady@furx.com", "role": "المدير العام", "department": "الإدارة العامة", "grade": "G5", "is_admin": True, "reports_to": None},
        {"name_ar": "وليد سعيد البنا", "name_en": "Waleed Elbanna", "email": "waleed@furx.com", "role": "مدير المصنع", "department": "إدارة المصنع", "grade": "G5", "is_admin": True, "reports_to": "hady@furx.com"},

        # Deputy Plant Managers
        {"name_ar": "عبد الرحمن عشعش", "name_en": "Abdelrahman Ashash", "email": "abdelrahman.a@furx.com", "role": "نائب مدير المصنع / إنتاج + صيانة", "department": "الإنتاج", "grade": "G4", "is_admin": False, "reports_to": "waleed@furx.com"},
        {"name_ar": "ياسمين البنا", "name_en": "Yasmin Elbanna", "email": "yasmin.b@furx.com", "role": "نائب مدير المصنع / مكتب فني + جودة", "department": "المكتب الفني", "grade": "G4", "is_admin": False, "reports_to": "waleed@furx.com"},

        # Finance & Audit
        {"name_ar": "هاجر حسين", "name_en": "Hagar Hussein", "email": "hagar@furx.com", "role": "مدير حسابات", "department": "المالية", "grade": "G4", "is_admin": False, "reports_to": "waleed@furx.com"},
        {"name_ar": "ياسمين عبد العزيز", "name_en": "Yasmin Abdelaziz", "email": "yasmin.a@furx.com", "role": "مدير مراجعة داخلية", "department": "المراجعة الداخلية", "grade": "G4", "is_admin": False, "reports_to": "waleed@furx.com"},

        # Supply Chain
        {"name_ar": "محمد موسي", "name_en": "Mohamed Mousa", "email": "mousa@furx.com", "role": "مدير سلاسل الإمداد واللوجستيات", "department": "سلاسل الإمداد", "grade": "G4", "is_admin": False, "reports_to": "waleed@furx.com"},
        {"name_ar": "محمد عامر", "name_en": "Mohamed Amer", "email": "amer@furx.com", "role": "مدير مخازن منتج تام", "department": "سلاسل الإمداد", "grade": "G3", "is_admin": False, "reports_to": "mousa@furx.com"},
        {"name_ar": "عبد الرحمن منصور", "name_en": "Abdelrahman Mansour", "email": "mansour@furx.com", "role": "مدير مخازن خامات", "department": "سلاسل الإمداد", "grade": "G3", "is_admin": False, "reports_to": "mousa@furx.com"},

        # Production Management
        {"name_ar": "ماهر متولي", "name_en": "Maher Metwally", "email": "maher@furx.com", "role": "مدير إنتاج تنفيذي", "department": "الإنتاج", "grade": "G4", "is_admin": False, "reports_to": "abdelrahman.a@furx.com"},
        {"name_ar": "عمرو الجوهري", "name_en": "Amr Elgohary", "email": "amr@furx.com", "role": "نائب مدير إنتاج تنفيذي", "department": "الإنتاج", "grade": "G3", "is_admin": False, "reports_to": "maher@furx.com"},

        # Production Supervisors
        {"name_ar": "علي أبو صالح", "name_en": "Ali Abu Saleh", "email": "ali@furx.com", "role": "مشرف نوم/سفرة تنفيذي", "department": "الإنتاج", "grade": "G3", "is_admin": False, "reports_to": "amr@furx.com"},
        {"name_ar": "طارق حامد", "name_en": "Tarek Hamed", "email": "tarek@furx.com", "role": "مشرف نوم/سفرة إداري", "department": "الإنتاج", "grade": "G3", "is_admin": False, "reports_to": "amr@furx.com"},
        {"name_ar": "معتز أبو العز", "name_en": "Moataz Abu Elezz", "email": "moataz@furx.com", "role": "مشرف تنجيد تنفيذي", "department": "الإنتاج", "grade": "G3", "is_admin": False, "reports_to": "amr@furx.com"},
        {"name_ar": "محمود داود", "name_en": "Mahmoud Dawoud", "email": "mahmoud@furx.com", "role": "مشرف تنجيد إداري", "department": "الإنتاج", "grade": "G3", "is_admin": False, "reports_to": "amr@furx.com"},
        {"name_ar": "فادي شلاطة", "name_en": "Fady Shalata", "email": "fady@furx.com", "role": "مشرف ورش مشتركة تنفيذي", "department": "الإنتاج", "grade": "G3", "is_admin": False, "reports_to": "amr@furx.com"},
        {"name_ar": "مصطفى شلبي", "name_en": "Mostafa Shalaby", "email": "mostafa@furx.com", "role": "مشرف ورش مشتركة إداري", "department": "الإنتاج", "grade": "G3", "is_admin": False, "reports_to": "amr@furx.com"},
        {"name_ar": "إبراهيم الحسيني", "name_en": "Ibrahim Elhusseiny", "email": "ibrahim@furx.com", "role": "مشرف خط كاستمايز", "department": "الإنتاج", "grade": "G3", "is_admin": False, "reports_to": "amr@furx.com"},

        # Technical Office & Quality
        {"name_ar": "محمد خضير", "name_en": "Mohamed Khodier", "email": "khodier@furx.com", "role": "محاسب تكاليف / BOM & Routing", "department": "المكتب الفني", "grade": "G3", "is_admin": False, "reports_to": "yasmin.b@furx.com"},
        {"name_ar": "هيثم العربي", "name_en": "Haitham Elaraby", "email": "haitham@furx.com", "role": "مدير جودة وتحسين مستمر", "department": "الجودة", "grade": "G4", "is_admin": False, "reports_to": "yasmin.b@furx.com"},
        {"name_ar": "رضوى بركات", "name_en": "Radwa Barakat", "email": "radwa@furx.com", "role": "بحث وتطوير المنتجات", "department": "المكتب الفني", "grade": "G3", "is_admin": False, "reports_to": "yasmin.b@furx.com"},

        # Maintenance
        {"name_ar": "محمد تومة", "name_en": "Mohamed Toma", "email": "toma@furx.com", "role": "مدير صيانة وتجهيزات", "department": "الصيانة", "grade": "G4", "is_admin": False, "reports_to": "abdelrahman.a@furx.com"},

        # Data Entry
        {"name_ar": "منة موسي", "name_en": "Menna Mousa", "email": "menna@furx.com", "role": "داتا إنتري مخازن خامات", "department": "سلاسل الإمداد", "grade": "G2", "is_admin": False, "reports_to": "mousa@furx.com"},
    ]

    # First pass: create all employees
    emp_map = {}
    for data in employees_data:
        emp = Employee(
            name_ar=data["name_ar"],
            name_en=data.get("name_en"),
            email=data["email"],
            role=data["role"],
            department=data["department"],
            grade=data.get("grade", "G1"),
            is_admin=data.get("is_admin", False),
        )
        emp.set_password("furx2026")  # Default password for all
        db.session.add(emp)
        emp_map[data["email"]] = emp

    db.session.flush()  # Get IDs

    # Second pass: set reports_to
    for data in employees_data:
        if data.get("reports_to"):
            emp = emp_map[data["email"]]
            manager = emp_map.get(data["reports_to"])
            if manager:
                emp.reports_to_id = manager.id

    db.session.commit()

    # ============================================================
    # REPORT TEMPLATES
    # ============================================================
    templates = [
        # Production supervisors daily report
        {
            "name_ar": "تقرير الإنتاج اليومي",
            "name_en": "Daily Production Report",
            "department": "الإنتاج",
            "fields": [
                {"key": "units_planned", "label_ar": "الكمية المخططة", "type": "number"},
                {"key": "units_produced", "label_ar": "الكمية المنتجة فعلياً", "type": "number"},
                {"key": "units_rework", "label_ar": "كمية إعادة التشغيل", "type": "number"},
                {"key": "downtime_minutes", "label_ar": "وقت التوقف (دقائق)", "type": "number"},
                {"key": "downtime_reason", "label_ar": "سبب التوقف", "type": "select", "options": ["لا يوجد", "عطل ماكينة", "نقص خامات", "نقص عمالة", "انقطاع كهرباء", "مشكلة جودة", "أخرى"]},
                {"key": "workers_present", "label_ar": "عدد العمال الحاضرين", "type": "number"},
                {"key": "workers_absent", "label_ar": "عدد العمال الغائبين", "type": "number"},
                {"key": "quality_issues", "label_ar": "مشاكل جودة ظهرت اليوم", "type": "textarea"},
                {"key": "material_issues", "label_ar": "مشاكل خامات", "type": "textarea"},
                {"key": "handover_complete", "label_ar": "تم تسليم واستلام الشغل بين المراحل (SOP-PROD-05)", "type": "checkbox"},
                {"key": "safety_incidents", "label_ar": "حوادث سلامة", "type": "select", "options": ["لا يوجد", "إصابة بسيطة", "إصابة متوسطة", "حادث كبير"]},
                {"key": "notes", "label_ar": "ملاحظات إضافية", "type": "textarea"},
            ]
        },
        # Quality daily report
        {
            "name_ar": "تقرير الجودة اليومي",
            "name_en": "Daily Quality Report",
            "department": "الجودة",
            "fields": [
                {"key": "pieces_inspected", "label_ar": "عدد القطع المفحوصة", "type": "number"},
                {"key": "pieces_passed", "label_ar": "عدد القطع المقبولة", "type": "number"},
                {"key": "pieces_rejected", "label_ar": "عدد القطع المرفوضة", "type": "number"},
                {"key": "nc_count", "label_ar": "عدد حالات عدم المطابقة (NC)", "type": "number"},
                {"key": "nc_types", "label_ar": "أنواع عدم المطابقة", "type": "textarea"},
                {"key": "corrective_actions", "label_ar": "إجراءات تصحيحية تم اتخاذها", "type": "textarea"},
                {"key": "incoming_inspection", "label_ar": "تم فحص خامات واردة اليوم", "type": "checkbox"},
                {"key": "sop_compliance", "label_ar": "نسبة الالتزام بالـ SOP (%)", "type": "number"},
                {"key": "notes", "label_ar": "ملاحظات", "type": "textarea"},
            ]
        },
        # Supply chain daily report
        {
            "name_ar": "تقرير سلاسل الإمداد اليومي",
            "name_en": "Daily Supply Chain Report",
            "department": "سلاسل الإمداد",
            "fields": [
                {"key": "materials_received", "label_ar": "خامات تم استلامها اليوم", "type": "textarea"},
                {"key": "materials_issued", "label_ar": "خامات تم صرفها للإنتاج", "type": "textarea"},
                {"key": "stockout_alerts", "label_ar": "خامات قاربت على النفاد", "type": "textarea"},
                {"key": "pending_pos", "label_ar": "أوامر شراء معلقة", "type": "number"},
                {"key": "deliveries_today", "label_ar": "تسليمات تمت اليوم", "type": "number"},
                {"key": "delivery_issues", "label_ar": "مشاكل في التسليم", "type": "textarea"},
                {"key": "fg_received", "label_ar": "قطع منتج تام تم استلامها", "type": "number"},
                {"key": "fg_shipped", "label_ar": "قطع منتج تام تم شحنها", "type": "number"},
                {"key": "inventory_accuracy_check", "label_ar": "تم إجراء فحص دقة مخزون", "type": "checkbox"},
                {"key": "notes", "label_ar": "ملاحظات", "type": "textarea"},
            ]
        },
        # Finance daily report
        {
            "name_ar": "التقرير المالي اليومي",
            "name_en": "Daily Finance Report",
            "department": "المالية",
            "fields": [
                {"key": "cash_balance", "label_ar": "رصيد النقدية (EGP)", "type": "number"},
                {"key": "bank_balance", "label_ar": "رصيد البنك (EGP)", "type": "number"},
                {"key": "collections_today", "label_ar": "تحصيلات اليوم (EGP)", "type": "number"},
                {"key": "payments_today", "label_ar": "مدفوعات اليوم (EGP)", "type": "number"},
                {"key": "invoices_issued", "label_ar": "فواتير صادرة اليوم", "type": "number"},
                {"key": "invoices_value", "label_ar": "قيمة الفواتير الصادرة (EGP)", "type": "number"},
                {"key": "payroll_due", "label_ar": "مستحقات مرتبات/أجور قادمة", "type": "text"},
                {"key": "supplier_payments_due", "label_ar": "مستحقات موردين عاجلة", "type": "textarea"},
                {"key": "notes", "label_ar": "ملاحظات", "type": "textarea"},
            ]
        },
        # Maintenance daily report
        {
            "name_ar": "تقرير الصيانة اليومي",
            "name_en": "Daily Maintenance Report",
            "department": "الصيانة",
            "fields": [
                {"key": "breakdowns_today", "label_ar": "أعطال حدثت اليوم", "type": "number"},
                {"key": "breakdowns_fixed", "label_ar": "أعطال تم إصلاحها", "type": "number"},
                {"key": "breakdown_details", "label_ar": "تفاصيل الأعطال", "type": "textarea"},
                {"key": "preventive_done", "label_ar": "صيانة وقائية تمت اليوم", "type": "checkbox"},
                {"key": "preventive_details", "label_ar": "تفاصيل الصيانة الوقائية", "type": "textarea"},
                {"key": "spare_parts_needed", "label_ar": "قطع غيار مطلوبة", "type": "textarea"},
                {"key": "machines_status", "label_ar": "حالة الماكينات العامة", "type": "select", "options": ["كل الماكينات تعمل", "ماكينة واحدة متوقفة", "أكثر من ماكينة متوقفة", "مشكلة كبيرة"]},
                {"key": "notes", "label_ar": "ملاحظات", "type": "textarea"},
            ]
        },
        # General daily report (for everyone)
        {
            "name_ar": "تقرير الحضور والمهام اليومي",
            "name_en": "Daily Attendance & Tasks",
            "department": "all",
            "fields": [
                {"key": "arrival_time", "label_ar": "وقت الحضور", "type": "text"},
                {"key": "tasks_planned", "label_ar": "المهام المخططة لليوم", "type": "textarea"},
                {"key": "tasks_completed", "label_ar": "المهام المنجزة", "type": "textarea"},
                {"key": "tasks_pending", "label_ar": "مهام لم تكتمل (مع السبب)", "type": "textarea"},
                {"key": "escalations", "label_ar": "مشاكل تحتاج تصعيد", "type": "textarea"},
                {"key": "tomorrow_plan", "label_ar": "خطة الغد", "type": "textarea"},
            ]
        },
    ]

    for tmpl_data in templates:
        tmpl = ReportTemplate(
            name_ar=tmpl_data["name_ar"],
            name_en=tmpl_data.get("name_en"),
            department=tmpl_data["department"],
            is_daily=True,
            is_active=True,
        )
        tmpl.fields = tmpl_data["fields"]
        db.session.add(tmpl)

    # ============================================================
    # KPI TEMPLATES
    # ============================================================
    kpi_templates = [
        {
            "name_ar": "تقييم أداء عامل / فني (G1-G2)",
            "grade": "G1",
            "department": None,
            "period": "weekly",
            "items": [
                {"key": "output_qty", "label_ar": "كمية الإنتاج مقابل الهدف", "weight": 30, "max_score": 100, "description": "نسبة تحقيق الكمية المستهدفة يومياً"},
                {"key": "quality", "label_ar": "جودة العمل", "weight": 20, "max_score": 100, "description": "نسبة القطع المقبولة من أول مرة"},
                {"key": "waste", "label_ar": "الهدر والإتلاف", "weight": 10, "max_score": 100, "description": "كمية المواد المهدرة (أقل = أفضل)"},
                {"key": "attendance", "label_ar": "الحضور والانضباط", "weight": 20, "max_score": 100, "description": "الحضور في الموعد، عدم التأخر أو الغياب"},
                {"key": "behavior", "label_ar": "السلوك والتعاون", "weight": 10, "max_score": 100, "description": "التعاون مع الزملاء، اتباع التعليمات"},
                {"key": "safety", "label_ar": "السلامة", "weight": 10, "max_score": 100, "description": "الالتزام بقواعد السلامة، ارتداء معدات الحماية"},
            ]
        },
        {
            "name_ar": "تقييم أداء مشرف خط (G3)",
            "grade": "G3",
            "department": None,
            "period": "weekly",
            "items": [
                {"key": "line_results", "label_ar": "نتائج الخط (خطة مقابل فعلي)", "weight": 30, "max_score": 100, "description": "نسبة تحقيق خطة الإنتاج اليومية/الأسبوعية"},
                {"key": "quality_rate", "label_ar": "معدل الجودة", "weight": 20, "max_score": 100, "description": "First-pass yield للخط"},
                {"key": "reports_submission", "label_ar": "تسليم التقارير", "weight": 15, "max_score": 100, "description": "تسليم التقارير اليومية في الوقت المحدد"},
                {"key": "team_development", "label_ar": "تطوير الفريق", "weight": 10, "max_score": 100, "description": "توجيه وتدريب العمال"},
                {"key": "attendance", "label_ar": "الحضور والانضباط", "weight": 15, "max_score": 100, "description": "الحضور في الموعد والانضباط"},
                {"key": "culture", "label_ar": "ثقافة العمل", "weight": 10, "max_score": 100, "description": "الالتزام بقيم الشركة والتعاون"},
            ]
        },
        {
            "name_ar": "تقييم أداء مدير (G4-G5)",
            "grade": "G4",
            "department": None,
            "period": "monthly",
            "items": [
                {"key": "dept_goals", "label_ar": "تحقيق أهداف القسم", "weight": 30, "max_score": 100, "description": "نسبة تحقيق الأهداف الشهرية للقسم"},
                {"key": "cost_control", "label_ar": "ضبط التكاليف", "weight": 20, "max_score": 100, "description": "الالتزام بالميزانية وتقليل الهدر"},
                {"key": "projects", "label_ar": "مشاريع التطوير", "weight": 15, "max_score": 100, "description": "تقدم مشاريع التحسين والتطوير"},
                {"key": "team_building", "label_ar": "بناء الفريق", "weight": 15, "max_score": 100, "description": "تطوير المرؤوسين وبناء القدرات"},
                {"key": "reporting", "label_ar": "جودة التقارير", "weight": 10, "max_score": 100, "description": "دقة وشمولية التقارير المقدمة"},
                {"key": "culture", "label_ar": "ثقافة العمل", "weight": 10, "max_score": 100, "description": "القيادة بالقدوة والالتزام بالقيم"},
            ]
        },
    ]

    for kpi_data in kpi_templates:
        kpi = KPITemplate(
            name_ar=kpi_data["name_ar"],
            grade=kpi_data["grade"],
            department=kpi_data.get("department"),
            period=kpi_data["period"],
            is_active=True,
        )
        kpi.items = kpi_data["items"]
        db.session.add(kpi)

    db.session.commit()

    # Create initial KPI records for current period
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = today.replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    all_employees = Employee.query.all()
    kpi_tmpls = KPITemplate.query.filter_by(is_active=True).all()

    for emp in all_employees:
        for tmpl in kpi_tmpls:
            # Match by grade
            if emp.grade in ['G1', 'G2'] and tmpl.grade == 'G1':
                period_start, period_end = week_start, week_end
            elif emp.grade == 'G3' and tmpl.grade == 'G3':
                period_start, period_end = week_start, week_end
            elif emp.grade in ['G4', 'G5'] and tmpl.grade == 'G4':
                period_start, period_end = month_start, month_end
            else:
                continue

            record = KPIRecord(
                employee_id=emp.id,
                template_id=tmpl.id,
                period_start=period_start,
                period_end=period_end,
                status='pending'
            )
            db.session.add(record)

    db.session.commit()
    print(f"Seeded: {Employee.query.count()} employees, {ReportTemplate.query.count()} templates, {KPITemplate.query.count()} KPI templates, {KPIRecord.query.count()} KPI records")
