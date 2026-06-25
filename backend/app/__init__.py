import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler


db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)

    app.config.from_object("app.config.Config")
    app.secret_key = os.environ.get("SECRET_KEY", "club-360-secret-key")

    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

    db.init_app(app)
    mail = Mail(app)

    with app.app_context():
        from app.models import db_structure

        db.create_all()

    from app.routes.central_routing import all_routes
    from app.routes.user_routes import user_bp
    from app.routes.tarjeta_routes import tarjeta_bp
    from app.routes.clase_routes import clase_bp
    from app.routes.reserva_routes import reserva_bp
    from app.routes.turno_routes import turno_bp
    from app.routes.actividad_routes import actividad_bp
    from app.routes.lista_espera_routes import lista_espera_bp
    from app.routes.asistencia_qr_routes import asistencia_bp
    from app.routes.asistencia_manual_routes import asistencia_manual_bp
    from app.routes.credito_routes import credito_bp
    from app.routes.suspension_routes import suspension_bp
    from app.routes.historial_routes import historial_bp
    # app.register_blueprint(user_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(tarjeta_bp)
    app.register_blueprint(clase_bp)
    app.register_blueprint(reserva_bp)
    app.register_blueprint(turno_bp)
    app.register_blueprint(actividad_bp)
    app.register_blueprint(lista_espera_bp)
    app.register_blueprint(asistencia_bp)
    app.register_blueprint(asistencia_manual_bp)
    app.register_blueprint(credito_bp)
    app.register_blueprint(historial_bp) 
    app.register_blueprint(suspension_bp)
    # from app.routes.user_routes import main as main_blueprint
    # app.register_blueprint(main_blueprint)
    # from app.routes import main
    # app.register_blueprint(main)
    
    def _job_suspender():
        with app.app_context():
            from app.services.suspension_service import suspender_abonados_pendientes
            suspender_abonados_pendientes()

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(_job_suspender, 'cron', day=11, hour=0, minute=0)
    scheduler.start()

    return app                           

    
    
    
    
    

    return app
