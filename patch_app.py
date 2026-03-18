from pathlib import Path

path = Path("app.py")
text = path.read_text(encoding="utf-8")

# 1) Fix old field names if present
text = text.replace("HourLog.submission_date", "HourLog.submitted_at")

# 2) Fix student dashboard to pass certificate_rows
old_student_dashboard = """    @app.route('/student/dashboard')
    @student_required
    def student_dashboard():
        student_id = session['user_id']
        registrations = Registration.query.filter_by(student_id=student_id).all()
        logs = HourLog.query.filter_by(student_id=student_id).all()
        notifications = Notification.query.filter_by(user_id=student_id).order_by(Notification.created_at.desc()).all()
        return render_template('student_dashboard.html', registrations=registrations, logs=logs, notifications=notifications)
"""

new_student_dashboard = """    @app.route('/student/dashboard')
    @student_required
    def student_dashboard():
        student_id = session['user_id']
        registrations = Registration.query.filter_by(student_id=student_id).all()
        logs = HourLog.query.filter_by(student_id=student_id).all()
        notifications = Notification.query.filter_by(user_id=student_id).order_by(Notification.created_at.desc()).all()

        certificate_rows = []
        for reg in registrations:
            event = reg.event
            approved_hours = get_approved_hours(student_id, event.id)
            level = calculate_certificate_level(approved_hours, event.total_event_hours)
            existing_certificate = Certificate.query.filter_by(student_id=student_id, event_id=event.id).first()

            certificate_rows.append({
                'event': event,
                'approved_hours': approved_hours,
                'total_event_hours': event.total_event_hours,
                'level': level,
                'certificate': existing_certificate
            })

        return render_template(
            'student_dashboard.html',
            registrations=registrations,
            logs=logs,
            notifications=notifications,
            certificate_rows=certificate_rows
        )
"""
if old_student_dashboard in text:
    text = text.replace(old_student_dashboard, new_student_dashboard)

# 3) Insert student certificate routes if missing
if "@app.route('/student/certificates')" not in text:
    insert_block = """
    @app.route('/student/certificates')
    @student_required
    def student_certificates():
        student_id = session['user_id']
        registrations = Registration.query.filter_by(student_id=student_id).all()
        certificate_rows = []

        for reg in registrations:
            event = reg.event
            approved_hours = get_approved_hours(student_id, event.id)
            level = calculate_certificate_level(approved_hours, event.total_event_hours)
            existing_certificate = Certificate.query.filter_by(student_id=student_id, event_id=event.id).first()

            certificate_rows.append({
                'event': event,
                'approved_hours': approved_hours,
                'total_event_hours': event.total_event_hours,
                'level': level,
                'certificate': existing_certificate
            })

        return render_template(
            'student_certificates.html',
            certificate_rows=certificate_rows,
            badge_colors=BADGE_COLORS
        )

    @app.route('/student/certificates/generate/<int:event_id>', methods=['POST'])
    @student_required
    def generate_student_certificate(event_id):
        student_id = session['user_id']
        certificate, error = get_or_create_certificate(student_id, event_id)

        if error:
            flash(error, 'warning')
            return redirect(url_for('student_certificates'))

        generate_certificate_pdf(certificate)

        note = Notification(
            user_id=student_id,
            title='Certificate Ready',
            message=f'Your {certificate.level} certificate for {certificate.event.title} is ready for download.'
        )
        db.session.add(note)
        db.session.commit()

        flash('Certificate generated successfully.', 'success')
        return redirect(url_for('student_certificates'))

    @app.route('/student/certificates/download/<int:event_id>')
    @student_required
    def download_student_certificate(event_id):
        student_id = session['user_id']
        certificate = Certificate.query.filter_by(student_id=student_id, event_id=event_id).first_or_404()

        if not certificate.file_path or not os.path.exists(certificate.file_path):
            generate_certificate_pdf(certificate)

        return send_file(certificate.file_path, as_attachment=True)

"""
    marker = "    @app.route('/supervisor/dashboard')"
    if marker in text:
        text = text.replace(marker, insert_block + marker)

# 4) Replace old admin_create_event
old_admin_create = """    @app.route('/admin/events/create', methods=['GET', 'POST'])
    @admin_required
    def admin_create_event():
        form = EventForm()

        if form.validate_on_submit():
            # Handle image upload
            image_filename = None
            file = request.files.get('image')
            if file and file.filename:
                allowed = {'png', 'jpg', 'jpeg', 'webp'}
                ext = file.filename.rsplit('.', 1)[-1].lower()
                if ext in allowed:
                    from werkzeug.utils import secure_filename
                    import os
                    filename = secure_filename(file.filename)
                    unique_name = f"{int(datetime.utcnow().timestamp())}_{filename}"
                    save_path = os.path.join(app.root_path, 'static', 'uploads', 'events', unique_name)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    file.save(save_path)
                    image_filename = unique_name

            # Combine date and time into one datetime
            event_date = datetime.combine(form.date.data, form.time.data)

            event = Event(
                title=form.title.data,
                description=form.description.data,
                date=event_date,
                location=form.location.data,
                max_participants=form.max_participants.data,
                category=form.category.data,
                status=form.status.data,
                image_filename=image_filename
            )

            db.session.add(event)
            db.session.commit()

            flash('Event created successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('admin_create_event.html', form=form)
"""

new_admin_create = """    @app.route('/admin/events/create', methods=['GET', 'POST'])
    @admin_required
    def admin_create_event():
        form = EventForm()

        if form.validate_on_submit():
            event_date = datetime.combine(form.date.data, form.time.data)
            supervisor = User.query.filter_by(role='supervisor').first()

            event = Event(
                title=form.title.data,
                description=form.description.data,
                date=event_date,
                location=form.location.data,
                max_participants=form.max_participants.data,
                category=form.category.data,
                status=form.status.data,
                total_event_hours=form.total_event_hours.data,
                supervisor_id=supervisor.id if supervisor else None
            )

            db.session.add(event)
            db.session.commit()

            flash('Event created successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('admin_create_event.html', form=form)
"""
if old_admin_create in text:
    text = text.replace(old_admin_create, new_admin_create)

# 5) Replace old/broken admin certificate route
start = text.find("    @app.route('/admin/certificates/issue/<int:student_id>'")
if start != -1:
    end = text.find("    @app.route('/admin/notify'", start)
    if end != -1:
        old_block = text[start:end]
        new_block = """    @app.route('/admin/certificates/issue/<int:student_id>', methods=['POST'])
    @app.route('/admin/certificates/issue/<int:student_id>/<int:event_id>', methods=['POST'])
    @admin_required
    def issue_certificate(student_id, event_id=None):
        if event_id is None:
            latest_approved = (
                HourLog.query
                .filter_by(student_id=student_id, status='approved')
                .order_by(HourLog.submitted_at.desc())
                .first()
            )
            if not latest_approved:
                flash('No approved event hours found for this student.', 'warning')
                return redirect(url_for('admin_dashboard'))
            event_id = latest_approved.event_id

        certificate, error = get_or_create_certificate(student_id, event_id, issued_by=session['user_id'])

        if error:
            flash(error, 'warning')
            return redirect(url_for('admin_dashboard'))

        generate_certificate_pdf(certificate)

        notification = Notification(
            user_id=student_id,
            title='Certificate Issued',
            message=f'Your {certificate.level} certificate for {certificate.event.title} has been issued.'
        )
        db.session.add(notification)

        db.session.commit()
        flash('Certificate issued successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

"""
        text = text.replace(old_block, new_block)

# 6) Fix old sample events so they include total_event_hours
text = text.replace(
"""                Event(
                    title='Community Garden Cleanup',
                    description='Help clean up the local community garden',
                    date=datetime(2026, 3, 15, 9, 0),
                    location='Durban Community Garden',
                    max_participants=20,
                    category='Community Service',
                    status='open',
                    supervisor_id=supervisor.id if supervisor else None
                ),""",
"""                Event(
                    title='Community Garden Cleanup',
                    description='Help clean up the local community garden',
                    date=datetime(2026, 3, 15, 9, 0),
                    location='Durban Community Garden',
                    max_participants=20,
                    category='Community Service',
                    status='open',
                    total_event_hours=8,
                    supervisor_id=supervisor.id if supervisor else None
                ),"""
)

text = text.replace(
"""                Event(
                    title='Beach Cleanup Drive',
                    description='Help keep our beaches clean and safe',
                    date=datetime(2026, 3, 20, 8, 0),
                    location='Durban North Beach',
                    max_participants=50,
                    category='Environmental',
                    status='open',
                    supervisor_id=supervisor.id if supervisor else None
                )""",
"""                Event(
                    title='Beach Cleanup Drive',
                    description='Help keep our beaches clean and safe',
                    date=datetime(2026, 3, 20, 8, 0),
                    location='Durban North Beach',
                    max_participants=50,
                    category='Environmental',
                    status='open',
                    total_event_hours=6,
                    supervisor_id=supervisor.id if supervisor else None
                )"""
)

path.write_text(text, encoding="utf-8")
print("app.py patched")
