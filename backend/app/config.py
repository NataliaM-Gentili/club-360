class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False 
    SECRET_KEY = 'club-360-secret-key'
    
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "juanmanuelperezz468@gmail.com"
    MAIL_PASSWORD = "eexflwujtcdrxafw"
    FRONTEND_URL = "http://localhost:5173/"  
    MAIL_DEFAULT_SENDER = 'club360@gmail.com'

