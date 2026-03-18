from app import app
from models import User, Event, Registration, HourLog, Certificate, Notification

with app.app_context():
    print("=== SYSTEM HEALTH CHECK ===")

    admins = User.query.filter_by(role='admin').all()
    supervisors = User.query.filter_by(role='supervisor').all()
    students = User.query.filter_by(role='student').all()

    print("\nUsers")
    print("Admins:", [(u.id, u.email) for u in admins])
    print("Supervisors:", [(u.id, u.email) for u in supervisors])
    print("Students:", [(u.id, u.email) for u in students])

    print("\nEvents")
    events = Event.query.all()
    print([(e.id, e.title, e.supervisor_id, e.total_event_hours, e.status) for e in events])

    print("\nRegistrations")
    regs = Registration.query.all()
    print([(r.id, r.student_id, r.event_id) for r in regs])

    print("\nHour Logs")
    logs = HourLog.query.all()
    print([(h.id, h.student_id, h.event_id, h.hours, h.status, h.reviewed_by) for h in logs])

    print("\nCertificates")
    certs = Certificate.query.all()
    print([(c.id, c.student_id, c.event_id, c.approved_hours, c.total_event_hours, c.level, c.file_path) for c in certs])

    print("\nRecent Notifications")
    notes = Notification.query.order_by(Notification.id.desc()).limit(10).all()
    print([(n.id, n.user_id, n.title) for n in notes])

    print("\nSupervisor Visibility")
    sup = User.query.filter_by(email='supervisor@dut.ac.za').first()
    if sup:
        sup_events = Event.query.filter_by(supervisor_id=sup.id).all()
        print("Supervisor events:", [(e.id, e.title) for e in sup_events])

        pending = HourLog.query.join(Event, HourLog.event_id == Event.id).filter(Event.supervisor_id == sup.id, HourLog.status == 'pending').all()
        reviewed = HourLog.query.join(Event, HourLog.event_id == Event.id).filter(Event.supervisor_id == sup.id, HourLog.status.in_(['approved', 'rejected'])).all()

        print("Pending logs:", [(h.id, h.student_id, h.event_id, h.hours) for h in pending])
        print("Reviewed logs:", [(h.id, h.student_id, h.event_id, h.hours, h.status) for h in reviewed])
    else:
        print("Default supervisor not found.")

    print("\n=== END CHECK ===")
