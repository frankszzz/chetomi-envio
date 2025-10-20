from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()


class ShippingService(db.Model):
    """Tipos de servicio de envío (Envío Hoy, Envío Programado)"""
    __tablename__ = 'shipping_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    
    # Horario de disponibilidad (None = 24/7)
    start_hour = db.Column(db.Integer)  # Hora inicio (0-23)
    end_hour = db.Column(db.Integer)    # Hora fin (0-23)
    
    # Relación con tarifas
    rates = db.relationship('ShippingRate', backref='service', lazy=True, cascade='all, delete-orphan')
    
    def is_available_now(self, timezone='America/Santiago'):
        """Verifica si el servicio está disponible según la hora actual"""
        if not self.active:
            return False
        
        # Si no tiene restricción horaria, siempre disponible
        if self.start_hour is None or self.end_hour is None:
            return True
        
        # Obtener hora actual en zona horaria de Chile
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        current_hour = now.hour
        
        # Verificar si está dentro del rango horario
        return self.start_hour <= current_hour < self.end_hour
    
    def __repr__(self):
        return f'<ShippingService {self.name}>'


class ShippingRate(db.Model):
    """Tarifas por rango de kilómetros"""
    __tablename__ = 'shipping_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('shipping_services.id'), nullable=False)
    
    # Rango de distancia en kilómetros
    min_km = db.Column(db.Float, nullable=False)
    max_km = db.Column(db.Float, nullable=False)
    
    # Precio fijo para este rango (pesos chilenos)
    price = db.Column(db.Integer, nullable=False)
    
    active = db.Column(db.Boolean, default=True)
    
    def is_in_range(self, distance_km):
        """Verifica si la distancia está en este rango"""
        return self.min_km <= distance_km < self.max_km
    
    def __repr__(self):
        return f'<Rate {self.min_km}-{self.max_km}km: ${self.price}>'


class DeliveryLog(db.Model):
    """Log de consultas de envío para análisis"""
    __tablename__ = 'delivery_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ubicaciones
    from_address = db.Column(db.String(500))
    to_address = db.Column(db.String(500))
    from_lat = db.Column(db.Float)
    from_lon = db.Column(db.Float)
    to_lat = db.Column(db.Float)
    to_lon = db.Column(db.Float)
    
    # Resultado
    distance_km = db.Column(db.Float)
    duration_minutes = db.Column(db.Float)
    service_code = db.Column(db.String(50))
    calculated_price = db.Column(db.Integer)
    
    # Referencia de Jumpseller
    order_reference = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Log {self.timestamp}: {self.distance_km}km>'
