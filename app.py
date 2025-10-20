from flask import Flask, request, jsonify, render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, ShippingService, ShippingRate, DeliveryLog
from services.openroute import OpenRouteService
from config import Config
import pytz
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# ============= FLASK-ADMIN =============

admin = Admin(
    app, 
    name='Shipping Admin', 
    template_mode='bootstrap4',
    url='/admin'
)

# Vistas Admin personalizadas
class ShippingServiceAdmin(ModelView):
    column_list = ('name', 'code', 'active', 'start_hour', 'end_hour')
    column_labels = {
        'name': 'Nombre del Servicio',
        'code': 'Código',
        'active': 'Activo',
        'start_hour': 'Hora Inicio (0-23)',
        'end_hour': 'Hora Fin (0-23)',
        'description': 'Descripción'
    }
    form_columns = ('name', 'code', 'description', 'active', 'start_hour', 'end_hour')
    column_filters = ('active',)
    can_export = True

class ShippingRateAdmin(ModelView):
    column_list = ('service_id', 'min_km', 'max_km', 'price', 'active')
    column_labels = {
        'service_id': 'ID Servicio',
        'min_km': 'KM Mínimo',
        'max_km': 'KM Máximo',
        'price': 'Precio (CLP)',
        'active': 'Activo'
    }
    form_columns = ('service_id', 'min_km', 'max_km', 'price', 'active')
    column_filters = ('service_id', 'active')
    column_sortable_list = ('min_km', 'max_km', 'price')
    can_export = True

class DeliveryLogAdmin(ModelView):
    can_create = False
    can_edit = False
    can_delete = True
    column_list = ('timestamp', 'from_address', 'to_address', 'distance_km', 'service_code', 'calculated_price')
    column_labels = {
        'timestamp': 'Fecha/Hora',
        'from_address': 'Origen',
        'to_address': 'Destino',
        'distance_km': 'Distancia (km)',
        'service_code': 'Servicio',
        'calculated_price': 'Precio (CLP)'
    }
    column_filters = ('service_code', 'timestamp')
    column_sortable_list = ('timestamp', 'distance_km', 'calculated_price')
    can_export = True
    column_default_sort = ('timestamp', True)

admin.add_view(ShippingServiceAdmin(ShippingService, db.session, name='Servicios'))
admin.add_view(ShippingRateAdmin(ShippingRate, db.session, name='Tarifas'))
admin.add_view(DeliveryLogAdmin(DeliveryLog, db.session, name='Historial'))

# ============= API ENDPOINTS =============

@app.route('/')
def index():
    """Página de inicio"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    tz = pytz.timezone(app.config['TIMEZONE'])
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    return jsonify({
        "status": "ok",
        "message": "Shipping API running with OpenRouteService",
        "current_time": current_time,
        "timezone": app.config['TIMEZONE'],
        "ors_configured": bool(app.config.get('ORS_API_KEY')),
        "max_distance_km": app.config['MAX_DELIVERY_DISTANCE_KM']
    }), 200

@app.route('/shipping/services', methods=['GET'])
def get_services():
    """
    Endpoint para Jumpseller: Lista servicios disponibles
    """
    services = ShippingService.query.filter_by(active=True).all()
    
    available_services = []
    for service in services:
        if service.is_available_now(app.config['TIMEZONE']):
            available_services.append({
                "service_name": service.name,
                "service_code": service.code
            })
    
    return jsonify({"services": available_services}), 200

@app.route('/shipping/rates', methods=['POST'])
def calculate_rates():
    """
    Endpoint para Jumpseller: Calcula tarifas de envío
    """
    data = request.json
    request_data = data.get('request', {})
    
    from_location = request_data.get('from', {})
    to_location = request_data.get('to', {})
    order_ref = request_data.get('request_reference', '')
    
    # Inicializar OpenRouteService
    ors = OpenRouteService()
    
    # Variables para almacenar coordenadas
    from_coords = None
    to_coords = None
    from_address = from_location.get('address', 'Origen')
    to_address = to_location.get('address', 'Destino')
    
    # Opción 1: Si vienen coordenadas, usarlas directamente
    if from_location.get('latitude') and to_location.get('latitude'):
        from_coords = {
            'lat': from_location['latitude'],
            'lon': from_location['longitude']
        }
        to_coords = {
            'lat': to_location['latitude'],
            'lon': to_location['longitude']
        }
        
        result = ors.calculate_distance(from_coords, to_coords)
        
        if not result:
            return jsonify({
                "reference_id": order_ref,
                "rates": [],
                "error": "No se pudo calcular la distancia"
            }), 200
        
        distance_km = result['distance_km']
        duration_minutes = result['duration_minutes']
    
    # Opción 2: Si vienen direcciones, geocodificar primero
    else:
        if not from_address or not to_address:
            return jsonify({
                "reference_id": order_ref,
                "rates": [],
                "error": "Faltan direcciones o coordenadas"
            }), 400
        
        result = ors.calculate_from_addresses(from_address, to_address)
        
        if not result:
            return jsonify({
                "reference_id": order_ref,
                "rates": [],
                "error": "No se pudieron geocodificar las direcciones"
            }), 200
        
        distance_km = result['distance_km']
        duration_minutes = result['duration_minutes']
        from_coords = result['from_coords']
        to_coords = result['to_coords']
    
    # Validar distancia máxima (7 km)
    max_distance = app.config['MAX_DELIVERY_DISTANCE_KM']
    if distance_km > max_distance:
        # Guardar log de consulta rechazada
        log = DeliveryLog(
            from_address=from_address,
            to_address=to_address,
            from_lat=from_coords['lat'] if from_coords else None,
            from_lon=from_coords['lon'] if from_coords else None,
            to_lat=to_coords['lat'] if to_coords else None,
            to_lon=to_coords['lon'] if to_coords else None,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            order_reference=order_ref
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            "reference_id": order_ref,
            "rates": [],
            "error": f"Fuera del área de cobertura (máximo {max_distance} km, solicitado {distance_km:.1f} km)"
        }), 200
    
    # Buscar servicios activos y disponibles
    services = ShippingService.query.filter_by(active=True).all()
    
    rates_response = []
    for service in services:
        # Verificar disponibilidad horaria
        if not service.is_available_now(app.config['TIMEZONE']):
            continue
        
        # Buscar tarifa aplicable para esta distancia
        applicable_rate = ShippingRate.query.filter(
            ShippingRate.service_id == service.id,
            ShippingRate.active == True,
            ShippingRate.min_km <= distance_km,
            ShippingRate.max_km > distance_km
        ).first()
        
        if applicable_rate:
            rates_response.append({
                "rate_id": f"{service.code}-{applicable_rate.id}",
                "rate_description": f"{service.name} - {distance_km:.1f} km (≈{duration_minutes:.0f} min)",
                "service_name": service.name,
                "service_code": service.code,
                "total_price": str(applicable_rate.price)
            })
            
            # Guardar log exitoso
            log = DeliveryLog(
                from_address=from_address,
                to_address=to_address,
                from_lat=from_coords['lat'] if from_coords else None,
                from_lon=from_coords['lon'] if from_coords else None,
                to_lat=to_coords['lat'] if to_coords else None,
                to_lon=to_coords['lon'] if to_coords else None,
                distance_km=distance_km,
                duration_minutes=duration_minutes,
                service_code=service.code,
                calculated_price=applicable_rate.price,
                order_reference=order_ref
            )
            db.session.add(log)
    
    db.session.commit()
    
    response = {
        "reference_id": order_ref,
        "rates": rates_response
    }
    
    return jsonify(response), 200

# ============= TEST ENDPOINTS =============

@app.route('/test/geocode', methods=['GET'])
def test_geocode():
    """Endpoint de prueba para geocodificar una dirección"""
    address = request.args.get('address', 'Av. Providencia 1208, Santiago, Chile')
    
    ors = OpenRouteService()
    result = ors.geocode(address)
    
    return jsonify({
        "input": address,
        "result": result
    }), 200

@app.route('/test/distance', methods=['GET'])
def test_distance():
    """Endpoint de prueba para calcular distancia entre dos direcciones"""
    from_addr = request.args.get('from', 'Av. Providencia 1208, Santiago, Chile')
    to_addr = request.args.get('to', 'Av. Andrés Bello 2687, Las Condes, Chile')
    
    ors = OpenRouteService()
    result = ors.calculate_from_addresses(from_addr, to_addr)
    
    return jsonify({
        "from": from_addr,
        "to": to_addr,
        "result": result
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=4010, debug=True)
