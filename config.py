import os


class Config:

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'studentvolunteeringsystem@gmail.com' 
    MAIL_PASSWORD = 'ieilvmgpajhocate'
    MAIL_DEFAULT_SENDER = 'Volunteer System <studentvolunteeringsystem@gmail.com>'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-dut-project'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_NAME = 'Student Volunteering & Community Service Platform'
    DEBUG = True
