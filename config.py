import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-NOT-SECURE-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///shipping.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Admin
    FLASK_ADMIN_SWATCH = 'cerulean'
    
    # Timezone
    TIMEZONE = os.getenv('TIMEZONE', 'America/Santiago')
    
    # OpenRouteService
    ORS_API_KEY = os.getenv('ORS_API_KEY')
    ORS_BASE_URL = 'https://api.openrouteservice.org/v2'
    
    # Límites de servicio
    MAX_DELIVERY_DISTANCE_KM = float(os.getenv('MAX_DELIVERY_DISTANCE_KM', '7'))
