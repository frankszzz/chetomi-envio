from app import app, db
from models import ShippingService, ShippingRate

def seed_database():
    """Poblar base de datos con servicios y tarifas exactas"""
    with app.app_context():
        # Limpiar datos anteriores
        ShippingRate.query.delete()
        ShippingService.query.delete()
        db.session.commit()
        
        print("🧹 Base de datos limpiada")
        
        # ===== SERVICIO 1: ENVÍO HOY (00:00 - 18:00) =====
        envio_hoy = ShippingService(
            name='Envío Hoy',
            code='ENVIO_HOY',
            description='Envío el mismo día (disponible de 00:01 a 18:00)',
            active=True,
            start_hour=0,   # 00:00 (medianoche)
            end_hour=18     # 18:00 (6 PM)
        )
        db.session.add(envio_hoy)
        db.session.flush()
        
        # TARIFAS EXACTAS PARA ENVÍO HOY
        tarifas_hoy = [
            ShippingRate(service_id=envio_hoy.id, min_km=0.0, max_km=3.0, price=3500, active=True),
            ShippingRate(service_id=envio_hoy.id, min_km=3.0, max_km=4.0, price=4500, active=True),
            ShippingRate(service_id=envio_hoy.id, min_km=4.0, max_km=5.0, price=5000, active=True),
            ShippingRate(service_id=envio_hoy.id, min_km=5.0, max_km=6.0, price=5500, active=True),
            ShippingRate(service_id=envio_hoy.id, min_km=6.0, max_km=7.0, price=6500, active=True),
        ]
        db.session.add_all(tarifas_hoy)
        
        # ===== SERVICIO 2: ENVÍO PROGRAMADO (24/7) =====
        envio_programado = ShippingService(
            name='Envío Programado',
            code='ENVIO_PROGRAMADO',
            description='Envío programado (disponible 24 horas)',
            active=True,
            start_hour=None,  # Sin restricción horaria
            end_hour=None
        )
        db.session.add(envio_programado)
        db.session.flush()
        
        # TARIFAS EXACTAS PARA ENVÍO PROGRAMADO
        tarifas_programado = [
            ShippingRate(service_id=envio_programado.id, min_km=0.0, max_km=3.0, price=3500, active=True),
            ShippingRate(service_id=envio_programado.id, min_km=3.0, max_km=4.0, price=4500, active=True),
            ShippingRate(service_id=envio_programado.id, min_km=4.0, max_km=5.0, price=5000, active=True),
            ShippingRate(service_id=envio_programado.id, min_km=5.0, max_km=6.0, price=5500, active=True),
            ShippingRate(service_id=envio_programado.id, min_km=6.0, max_km=7.0, price=6500, active=True),
        ]
        db.session.add_all(tarifas_programado)
        
        db.session.commit()
        
        print("\n✅ Base de datos inicializada correctamente")
        print("\n" + "="*70)
        print("📦 SERVICIOS CREADOS:")
        print("="*70)
        print(f"   1. {envio_hoy.name}")
        print(f"      - Código: {envio_hoy.code}")
        print(f"      - Horario: {envio_hoy.start_hour}:00 a {envio_hoy.end_hour}:00 hrs")
        print(f"\n   2. {envio_programado.name}")
        print(f"      - Código: {envio_programado.code}")
        print(f"      - Horario: 24/7 (sin restricción)")
        
        print("\n" + "="*70)
        print("💰 TARIFAS (aplicables a ambos servicios):")
        print("="*70)
        print("   │ Rango (km) │ Precio (CLP) │")
        print("   │────────────│──────────────│")
        print("   │ 0.0 - 3.0  │   $3,500     │")
        print("   │ 3.0 - 4.0  │   $4,500     │")
        print("   │ 4.0 - 5.0  │   $5,000     │")
        print("   │ 5.0 - 6.0  │   $5,500     │")
        print("   │ 6.0 - 7.0  │   $6,500     │")
        print("   │ 7.0+       │ NO DISPONIBLE│")
        print("="*70)
        
        print("\n🌐 URLs importantes:")
        print("   - API Base: http://localhost:4010")
        print("   - Panel Admin: http://localhost:4010/admin")
        print("   - Health Check: http://localhost:4010/health")
        print("   - Test Geocode: http://localhost:4010/test/geocode?address=Tu+Direccion")
        print("   - Test Distance: http://localhost:4010/test/distance?from=Dir1&to=Dir2")
        print("\n")

if __name__ == '__main__':
    seed_database()
