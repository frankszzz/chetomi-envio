import requests
from flask import current_app


class OpenRouteService:
    """Cliente para OpenRouteService API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or current_app.config.get('ORS_API_KEY')
        self.base_url = current_app.config.get('ORS_BASE_URL', 'https://api.openrouteservice.org/v2')
    
    def geocode(self, address):
        """
        Geocodificar dirección a coordenadas
        
        Args:
            address (str): Dirección a geocodificar
            
        Returns:
            dict: {'lat': float, 'lon': float, 'formatted_address': str}
        """
        url = f"{self.base_url}/geocode/search"
        
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        
        params = {
            'text': address,
            'boundary.country': 'CL',  # Limitar a Chile
            'size': 1  # Solo el mejor resultado
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('features'):
                feature = data['features'][0]
                coords = feature['geometry']['coordinates']
                
                return {
                    'lon': coords[0],
                    'lat': coords[1],
                    'formatted_address': feature['properties'].get('label', address)
                }
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Geocoding error: {str(e)}")
            return None
    
    def calculate_distance(self, from_coords, to_coords, profile='driving-car'):
        """
        Calcular distancia y tiempo entre dos coordenadas
        
        Args:
            from_coords (dict): {'lat': float, 'lon': float}
            to_coords (dict): {'lat': float, 'lon': float}
            profile (str): 'driving-car', 'driving-hgv', 'cycling-regular', 'foot-walking'
            
        Returns:
            dict: {'distance_km': float, 'duration_minutes': float}
        """
        url = f"{self.base_url}/directions/{profile}"
        
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # OpenRouteService espera [lon, lat] no [lat, lon]
        body = {
            'coordinates': [
                [from_coords['lon'], from_coords['lat']],
                [to_coords['lon'], to_coords['lat']]
            ]
        }
        
        try:
            response = requests.post(url, json=body, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('routes'):
                route = data['routes'][0]
                summary = route['summary']
                
                # Distancia en metros, convertir a km
                distance_km = summary['distance'] / 1000
                
                # Duración en segundos, convertir a minutos
                duration_minutes = summary['duration'] / 60
                
                return {
                    'distance_km': round(distance_km, 2),
                    'duration_minutes': round(duration_minutes, 1)
                }
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Distance calculation error: {str(e)}")
            return None
    
    def calculate_from_addresses(self, from_address, to_address, profile='driving-car'):
        """
        Calcular distancia desde direcciones (geocodifica primero)
        
        Args:
            from_address (str): Dirección origen
            to_address (str): Dirección destino
            profile (str): Perfil de ruta
            
        Returns:
            dict: {
                'distance_km': float,
                'duration_minutes': float,
                'from_coords': dict,
                'to_coords': dict
            }
        """
        # Geocodificar origen
        from_coords = self.geocode(from_address)
        if not from_coords:
            return None
        
        # Geocodificar destino
        to_coords = self.geocode(to_address)
        if not to_coords:
            return None
        
        # Calcular distancia
        result = self.calculate_distance(from_coords, to_coords, profile)
        
        if result:
            result['from_coords'] = from_coords
            result['to_coords'] = to_coords
        
        return result
