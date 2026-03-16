import os

class Config:
    """
    Base configuration class for the Flask application.
    All configuration settings are defined here.
    """
    
    # Secret key for session management and CSRF protection
    # In production, this should be a strong, random string
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-dut-project'
    
    # Database configuration
    # SQLite database will be stored in the instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'database.db')
    
    # Disable SQLAlchemy event handling for better performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application name
    APP_NAME = 'Student Volunteering & Community Service Platform'
    
    # Debug mode - set to False in production
    DEBUG = True