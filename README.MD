# E-commerce API

API REST completa para sistema de e-commerce desarrollada con Flask y SQLAlchemy.

## Estructura del Proyecto

```
ecommerce-api/
├── .env                    # Variables de entorno
├── app.py                  # Punto de entrada
├── requirements.txt        # Dependencias
├── database/
│   ├── create-ecommerce.sql
│   └── ecommerce.db
└── app/
    ├── __init__.py         # Configuración Flask
    ├── models.py           # Modelos SQLAlchemy
    └── routes/
        ├── auth_routes.py      # Autenticación
        ├── product_routes.py   # Productos
        ├── user_routes.py      # Usuarios
        ├── sales_routes.py     # Ventas y carrito
        ├── category_routes.py  # Categorías
        └── location_routes.py  # Ubicaciones
```

## Instalación

1. **Clonar y navegar al proyecto**
```bash
cd ecommerce-api
```

2. **Crear entorno virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
El archivo `.env` ya está configurado:
```
FLASK_DEBUG=True
SECRET_KEY=HolaMundo
DATABASE_URL=sqlite:///database/ecommerce.db
```

5. **Ejecutar la aplicación**
```bash
python app.py
```

La API estará disponible en: `http://localhost:5050`

## Endpoints Principales

### Autenticación (`/api/auth`)
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/verify-token` - Verificar token
- `PUT /api/auth/change-password` - Cambiar contraseña
- `GET /api/auth/roles` - Obtener roles

### Productos (`/api/products`)
- `GET /api/products/` - Listar productos (con filtros)
- `GET /api/products/{id}` - Obtener producto específico
- `POST /api/products/` - Crear producto
- `PUT /api/products/{id}` - Actualizar producto
- `DELETE /api/products/{id}` - Eliminar producto
- `GET /api/products/search` - Buscar productos
- `GET /api/products/featured` - Productos destacados

### Ventas y Carrito (`/api/sales`)
**Carrito:**
- `GET /api/sales/cart` - Ver carrito
- `POST /api/sales/cart/add` - Agregar al carrito
- `PUT /api/sales/cart/update/{id}` - Actualizar cantidad
- `DELETE /api/sales/cart/remove/{id}` - Eliminar del carrito
- `DELETE /api/sales/cart/clear` - Vaciar carrito

**Ventas:**
- `POST /api/sales/checkout` - Procesar compra
- `GET /api/sales/` - Listar ventas
- `GET /api/sales/{id}` - Detalle de venta
- `GET /api/sales/stats` - Estadísticas (admin)

### Usuarios (`/api/users`)
- `GET /api/users/profile` - Perfil del usuario
- `PUT /api/users/profile` - Actualizar perfil
- `GET /api/users/` - Listar usuarios (admin)
- `GET /api/users/{id}` - Usuario específico
- `PUT /api/users/{id}/roles` - Actualizar roles (admin)
- `DELETE /api/users/{id}` - Eliminar usuario (admin)

### Categorías (`/api/categories`)
- `GET /api/categories/` - Listar categorías
- `GET /api/categories/{id}` - Categoría específica
- `POST /api/categories/` - Crear categoría
- `PUT /api/categories/{id}` - Actualizar categoría
- `DELETE /api/categories/{id}` - Eliminar categoría

### Ubicaciones (`/api/locations`)
- `GET /api/locations/countries` - Listar países
- `GET /api/locations/states` - Listar estados
- `GET /api/locations/cities` - Listar ciudades
- `GET /api/locations/hierarchy` - Jerarquía completa
- `GET /api/locations/search` - Buscar ubicaciones

## Autenticación

La API usa JWT (JSON Web Tokens) para autenticación. 

**Para endpoints protegidos, incluir en headers:**
```
Authorization: Bearer {token}
```

## Ejemplos de Uso

### 1. Registrar Usuario
```bash
curl -X POST http://localhost:5050/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "UserName": "test_user",
    "Email": "test@example.com",
    "PasswoRDkey": "password123",
    "iD_City": 1
  }'
```

### 2. Iniciar Sesión
```bash
curl -X POST http://localhost:5050/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "Email": "test@example.com",
    "PasswoRDkey": "password123"
  }'
```

### 3. Listar Productos
```bash
curl -X GET "http://localhost:5050/api/products/?page=1&per_page=10&search=iPhone"
```

### 4. Agregar al Carrito
```bash
curl -X POST http://localhost:5050/api/sales/cart/add \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "id_Product": 1,
    "quantity": 2
  }'
```

### 5. Procesar Compra
```bash
curl -X POST http://localhost:5050/api/sales/checkout \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "DescripcionSale": "Compra online"
  }'
```

## Roles de Usuario

- **Administrador**: Acceso completo a toda la API
- **Usuario/Cliente**: Acceso a productos, carrito y sus propias ventas
- **Vendedor**: Funcionalidades específicas de ventas
- **Cliente**: Funcionalidades básicas de compra

## Filtros y Paginación

La mayoría de endpoints de listado soportan:
- `page`: Número de página (default: 1)
- `per_page`: Items por página (default: 10)
- `search`: Búsqueda por texto
- Filtros específicos por endpoint

## Códigos de Respuesta

- `200`: Éxito
- `201`: Creado exitosamente
- `400`: Error en datos enviados
- `401`: No autorizado (token inválido)
- `403`: Prohibido (sin permisos)
- `404`: No encontrado
- `409`: Conflicto (duplicado)
- `500`: Error del servidor

## Base de Datos

La API usa SQLite por defecto. El archivo de base de datos se crea automáticamente en `database/ecommerce.db` con datos de ejemplo incluidos.

### Datos de Ejemplo Incluidos:
- **Admin**: admin@ecommerce.com / admin123
- **Productos**: iPhone, Samsung, MacBook, etc.
- **Categorías**: Electrónicos, Ropa, Hogar, etc.
- **Ubicaciones**: Colombia con departamentos y ciudades

## Funcionalidades Principales

✅ **Sistema de autenticación JWT**
✅ **CRUD completo para productos**
✅ **Carrito de compras funcional**
✅ **Sistema de ventas**
✅ **Gestión de usuarios y roles**
✅ **Categorías de productos**
✅ **Ubicaciones geográficas**
✅ **Búsqueda y filtros**
✅ **Paginación**
✅ **Validaciones**
✅ **Manejo de errores**

## Notas Técnicas

- **ORM**: SQLAlchemy con relaciones bien definidas
- **Validaciones**: Verificación de stock, emails únicos, etc.
- **Seguridad**: Passwords hasheados, validación de tokens
- **CORS**: Habilitado para desarrollo frontend
- **Blueprints**: Código organizado en módulos
- **Gestión de stock**: Actualización automática en ventas