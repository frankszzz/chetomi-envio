# 🚚 Shipping API for Jumpseller - Chile

API de cálculo automático de tarifas de envío por distancia, integrable con Jumpseller usando OpenRouteService.

## 🌟 Características

- ✅ **Envío Hoy**: Disponible de 00:01 a 18:00 hrs
- ✅ **Envío Programado**: Disponible 24/7
- ✅ **Cálculo automático** de distancias con OpenRouteService
- ✅ **Panel de administración** web para gestionar tarifas
- ✅ **Límite de cobertura**: Máximo 7 km
- ✅ **Historial de consultas** para análisis

## 📋 Requisitos

- Docker y Docker Compose
- Cuenta en [OpenRouteService](https://openrouteservice.org/dev/#/signup) (gratis)
- Cuenta en Jumpseller

## 🚀 Instalación

### 1. Clonar repositorio

git clone https://github.com/tu-usuario/shipping-jumpseller.git
cd shipping-jumpseller

text

### 2. Configurar variables de entorno

cp .env.example .env

text

Edita `.env` y agrega tu API Key de OpenRouteService:

ORS_API_KEY=tu-api-key-aqui
SECRET_KEY=genera-una-clave-aleatoria-segura

text

### 3. Construir y ejecutar

docker-compose up --build

text

La API estará disponible en: `http://localhost:5010`

## 🔧 Configuración en Jumpseller

1. Ve a: **Admin → Checkout → Shipping → External Shipping Methods**
2. Click en **"Add External Shipping Method"**
3. Configura:
   - **Callback URL**: `https://tu-dominio.com/shipping/rates`
   - **Fetch Services URL**: `https://tu-dominio.com/shipping/services`
4. Click en **"Fetch Services"**
5. Activa los servicios que aparezcan
6. Guarda los cambios

## 💰 Tarifas

| Rango (km) | Precio (CLP) |
|------------|--------------|
| 0 - 3      | $3,500       |
| 3 - 4      | $4,500       |
| 4 - 5      | $5,000       |
| 5 - 6      | $5,500       |
| 6 - 7      | $6,500       |
| 7+         | No disponible|

## 🌐 Endpoints

- `GET /` - Página de inicio
- `GET /health` - Health check
- `GET /shipping/services` - Lista servicios disponibles
- `POST /shipping/rates` - Calcula tarifas de envío
- `GET /admin` - Panel de administración
- `GET /test/geocode?address=Dir` - Probar geocodificación
- `GET /test/distance?from=Dir1&to=Dir2` - Probar cálculo de distancia

## 📊 Panel de Administración

Accede en `http://localhost:5010/admin`

Puedes:
- ✏️ Modificar tarifas sin tocar código
- 📅 Cambiar horarios de disponibilidad
- 📈 Ver historial de consultas
- 📥 Exportar datos a CSV

## 🧪 Pruebas

### Probar geocodificación:

curl "http://localhost:5010/test/geocode?address=Av.%20Providencia%201208,%20Santiago"

text

### Probar cálculo de distancia:

curl "http://localhost:5010/test/distance?from=Av.%20Providencia%201208,%20Santiago&to=Av.%20Andrés%20Bello%202687,%20Las%20Condes"

text

## 📝 Licencia

MIT

## 🤝 Soporte

Para problemas o preguntas, abre un issue en GitHub.
PASOS PARA SUBIR A GITHUB
bash
# 1. Crear .env local (NO SE SUBIRÁ)
cp .env.example .env
# Edita .env con tus valores reales

# 2. Inicializar Git
git init
git add .
git commit -m "Initial commit: Shipping API for Jumpseller with OpenRouteService"

# 3. Crear repositorio en GitHub y conectar
git remote add origin https://github.com/tu-usuario/shipping-jumpseller.git
git branch -M main
git push -u origin main
PASOS PARA DESPLEGAR EN EASYPANEL
Sube el código a GitHub (siguiendo los pasos anteriores)

En EasyPanel:

Create New Project → Docker

Conecta tu repositorio GitHub

Puerto: 5010

Build Command: Automático (detecta Dockerfile)

Configura Environment Variables en EasyPanel:

text
ORS_API_KEY=tu-api-key-de-openrouteservice
SECRET_KEY=tu-clave-secreta-generada
TIMEZONE=America/Santiago
MAX_DELIVERY_DISTANCE_KM=7
Deploy y accede a tu dominio

✅ LISTO - Proyecto completo y actualizado sin confusiones

