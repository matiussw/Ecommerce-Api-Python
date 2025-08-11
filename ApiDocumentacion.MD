# Colección completa cURL - API E-commerce

## Variables de entorno para Postman

```
BASE_URL = http://localhost:5050
TOKEN = [El token JWT que obtienes del login]
```

## 🔐 AUTENTICACIÓN

### 1. Registrar Usuario
```bash
curl -X POST {{BASE_URL}}/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "UserName": "nuevo_usuario",
    "Email": "nuevo@example.com",
    "PasswoRDkey": "password123",
    "iD_City": 1
  }'
```

### 2. Login
```bash
curl -X POST {{BASE_URL}}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "Email": "admin@ecommerce.com",
    "PasswoRDkey": "admin123"
  }'
```

### 3. Login Usuario Normal
```bash
curl -X POST {{BASE_URL}}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "Email": "juan@email.com",
    "PasswoRDkey": "password123"
  }'
```

### 4. Verificar Token
```bash
curl -X POST {{BASE_URL}}/api/auth/verify-token \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 5. Cambiar Password
```bash
curl -X PUT {{BASE_URL}}/api/auth/change-password \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "password123",
    "new_password": "newpassword456"
  }'
```

### 6. Obtener Roles
```bash
curl -X GET {{BASE_URL}}/api/auth/roles \
  -H "Content-Type: application/json"
```

## 📱 PRODUCTOS

### 7. Listar Productos (sin filtros)
```bash
curl -X GET {{BASE_URL}}/api/products/ \
  -H "Content-Type: application/json"
```

### 8. Listar Productos con Filtros
```bash
curl -X GET "{{BASE_URL}}/api/products/?page=1&per_page=5&search=iPhone&category_id=1&min_price=100&max_price=1000&in_stock=true" \
  -H "Content-Type: application/json"
```

### 9. Obtener Producto Específico
```bash
curl -X GET {{BASE_URL}}/api/products/1 \
  -H "Content-Type: application/json"
```

### 10. Crear Producto
```bash
curl -X POST {{BASE_URL}}/api/products/ \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "ProductName": "Nuevo Smartphone",
    "Price": 899.99,
    "Stock": 15,
    "categories": [1, 6]
  }'
```

### 11. Actualizar Producto
```bash
curl -X PUT {{BASE_URL}}/api/products/1 \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "ProductName": "iPhone 15 Pro Max",
    "Price": 1199.99,
    "Stock": 8,
    "categories": [1, 6]
  }'
```

### 12. Actualizar Solo Stock
```bash
curl -X PUT {{BASE_URL}}/api/products/1/stock \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "Stock": 25
  }'
```

### 13. Agregar Imagen a Producto
```bash
curl -X POST {{BASE_URL}}/api/products/1/images \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "pathimage": "/images/iphone15_new.jpg",
    "alt_text": "iPhone 15 Pro imagen actualizada",
    "is_main_image": true,
    "id_Category": 1
  }'
```

### 14. Eliminar Imagen de Producto
```bash
curl -X DELETE {{BASE_URL}}/api/products/1/images/1 \
  -H "Authorization: Bearer {{TOKEN}}"
```

### 15. Buscar Productos
```bash
curl -X GET "{{BASE_URL}}/api/products/search?q=Samsung" \
  -H "Content-Type: application/json"
```

### 16. Productos Destacados
```bash
curl -X GET {{BASE_URL}}/api/products/featured \
  -H "Content-Type: application/json"
```

### 17. Eliminar Producto
```bash
curl -X DELETE {{BASE_URL}}/api/products/11 \
  -H "Authorization: Bearer {{TOKEN}}"
```

## 🛒 CARRITO Y VENTAS

### 18. Ver Carrito
```bash
curl -X GET {{BASE_URL}}/api/sales/cart \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 19. Agregar al Carrito
```bash
curl -X POST {{BASE_URL}}/api/sales/cart/add \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "id_Product": 1,
    "quantity": 2
  }'
```

### 20. Agregar Otro Producto al Carrito
```bash
curl -X POST {{BASE_URL}}/api/sales/cart/add \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "id_Product": 2,
    "quantity": 1
  }'
```

### 21. Actualizar Cantidad en Carrito
```bash
curl -X PUT {{BASE_URL}}/api/sales/cart/update/1 \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 3
  }'
```

### 22. Eliminar Item del Carrito
```bash
curl -X DELETE {{BASE_URL}}/api/sales/cart/remove/2 \
  -H "Authorization: Bearer {{TOKEN}}"
```

### 23. Procesar Compra (Checkout)
```bash
curl -X POST {{BASE_URL}}/api/sales/checkout \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "DescripcionSale": "Compra realizada desde API"
  }'
```

### 24. Vaciar Carrito
```bash
curl -X DELETE {{BASE_URL}}/api/sales/cart/clear \
  -H "Authorization: Bearer {{TOKEN}}"
```

### 25. Listar Ventas del Usuario
```bash
curl -X GET "{{BASE_URL}}/api/sales/?page=1&per_page=10" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 26. Obtener Venta Específica
```bash
curl -X GET {{BASE_URL}}/api/sales/1 \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 27. Estadísticas de Ventas (Admin)
```bash
curl -X GET {{BASE_URL}}/api/sales/stats \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

## 👥 USUARIOS

### 28. Ver Perfil Propio
```bash
curl -X GET {{BASE_URL}}/api/users/profile \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 29. Actualizar Perfil
```bash
curl -X PUT {{BASE_URL}}/api/users/profile \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "UserName": "Nombre Actualizado",
    "iD_City": 2
  }'
```

### 30. Listar Usuarios (Admin)
```bash
curl -X GET "{{BASE_URL}}/api/users/?page=1&per_page=10&search=juan" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 31. Obtener Usuario Específico
```bash
curl -X GET {{BASE_URL}}/api/users/2 \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 32. Actualizar Roles de Usuario (Admin)
```bash
curl -X PUT {{BASE_URL}}/api/users/2/roles \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "role_ids": [3, 4]
  }'
```

### 33. Obtener Ventas de Usuario Específico
```bash
curl -X GET "{{BASE_URL}}/api/users/2/sales?page=1&per_page=5" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 34. Buscar Usuarios (Admin)
```bash
curl -X GET "{{BASE_URL}}/api/users/search?q=juan" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 35. Estadísticas de Usuarios (Admin)
```bash
curl -X GET {{BASE_URL}}/api/users/stats \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### 36. Eliminar Usuario (Admin)
```bash
curl -X DELETE {{BASE_URL}}/api/users/5 \
  -H "Authorization: Bearer {{TOKEN}}"
```

## 📂 CATEGORÍAS

### 37. Listar Categorías
```bash
curl -X GET {{BASE_URL}}/api/categories/ \
  -H "Content-Type: application/json"
```

### 38. Listar Categorías con Productos
```bash
curl -X GET "{{BASE_URL}}/api/categories/?include_products=true" \
  -H "Content-Type: application/json"
```

### 39. Obtener Categoría Específica
```bash
curl -X GET "{{BASE_URL}}/api/categories/1?page=1&per_page=5" \
  -H "Content-Type: application/json"
```

### 40. Crear Categoría
```bash
curl -X POST {{BASE_URL}}/api/categories/ \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "CategoryName": "Accesorios"
  }'
```

### 41. Actualizar Categoría
```bash
curl -X PUT {{BASE_URL}}/api/categories/8 \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "CategoryName": "Accesorios Tecnológicos"
  }'
```

### 42. Productos de Categoría con Filtros
```bash
curl -X GET "{{BASE_URL}}/api/categories/1/products?page=1&per_page=5&min_price=100&in_stock=true" \
  -H "Content-Type: application/json"
```

### 43. Estadísticas de Categorías
```bash
curl -X GET {{BASE_URL}}/api/categories/stats \
  -H "Content-Type: application/json"
```

### 44. Eliminar Categoría
```bash
curl -X DELETE {{BASE_URL}}/api/categories/8 \
  -H "Authorization: Bearer {{TOKEN}}"
```

## 🌍 UBICACIONES

### 45. Listar Países
```bash
curl -X GET {{BASE_URL}}/api/locations/countries \
  -H "Content-Type: application/json"
```

### 46. Crear País
```bash
curl -X POST {{BASE_URL}}/api/locations/countries \
  -H "Content-Type: application/json" \
  -d '{
    "CountryName": "Brasil"
  }'
```

### 47. Obtener País con Estados
```bash
curl -X GET "{{BASE_URL}}/api/locations/countries/1?include_states=true" \
  -H "Content-Type: application/json"
```

### 48. Listar Estados
```bash
curl -X GET {{BASE_URL}}/api/locations/states \
  -H "Content-Type: application/json"
```

### 49. Estados por País
```bash
curl -X GET "{{BASE_URL}}/api/locations/states?country_id=1" \
  -H "Content-Type: application/json"
```

### 50. Crear Estado
```bash
curl -X POST {{BASE_URL}}/api/locations/states \
  -H "Content-Type: application/json" \
  -d '{
    "StatesName": "Nariño",
    "iD_Country": 1
  }'
```

### 51. Obtener Estado con Ciudades
```bash
curl -X GET "{{BASE_URL}}/api/locations/states/1?include_cities=true" \
  -H "Content-Type: application/json"
```

### 52. Estados de País Específico
```bash
curl -X GET {{BASE_URL}}/api/locations/countries/1/states \
  -H "Content-Type: application/json"
```

### 53. Listar Ciudades
```bash
curl -X GET {{BASE_URL}}/api/locations/cities \
  -H "Content-Type: application/json"
```

### 54. Ciudades por Estado
```bash
curl -X GET "{{BASE_URL}}/api/locations/cities?state_id=1" \
  -H "Content-Type: application/json"
```

### 55. Crear Ciudad
```bash
curl -X POST {{BASE_URL}}/api/locations/cities \
  -H "Content-Type: application/json" \
  -d '{
    "CityName": "Rionegro",
    "iD_States": 1
  }'
```

### 56. Ciudades de Estado Específico
```bash
curl -X GET {{BASE_URL}}/api/locations/states/1/cities \
  -H "Content-Type: application/json"
```

### 57. Ciudades por País
```bash
curl -X GET {{BASE_URL}}/api/locations/countries/1/cities \
  -H "Content-Type: application/json"
```

### 58. Jerarquía Completa
```bash
curl -X GET {{BASE_URL}}/api/locations/hierarchy \
  -H "Content-Type: application/json"
```

### 59. Buscar Ubicaciones
```bash
curl -X GET "{{BASE_URL}}/api/locations/search?q=Medell&type=city" \
  -H "Content-Type: application/json"
```

## 🏠 RUTA PRINCIPAL

### 60. Información de la API
```bash
curl -X GET {{BASE_URL}}/ \
  -H "Content-Type: application/json"
```

## 📋 FLUJO DE PRUEBA RECOMENDADO

### Paso 1: Autenticación
1. Ejecutar **#2 Login Admin** para obtener token de administrador
2. Guardar el token en variable `{{TOKEN}}`

### Paso 2: Explorar Datos
3. **#60** - Ver info de la API
4. **#37** - Ver categorías disponibles
5. **#7** - Ver productos disponibles
6. **#45** - Ver países disponibles

### Paso 3: Crear Usuario y Probar Carrito
7. **#1** - Registrar nuevo usuario
8. **#2** - Login con nuevo usuario y actualizar `{{TOKEN}}`
9. **#19, #20** - Agregar productos al carrito
10. **#18** - Ver carrito
11. **#23** - Procesar compra

### Paso 4: Funciones Admin
12. **#2** - Login como admin y actualizar `{{TOKEN}}`
13. **#30** - Ver usuarios
14. **#27** - Ver estadísticas de ventas
15. **#10** - Crear nuevo producto

## 💡 NOTAS IMPORTANTES

1. **Token JWT**: Después del login, copia el token de la respuesta y úsalo en `{{TOKEN}}`
2. **Base URL**: Asegúrate de que la API esté corriendo en puerto 5050
3. **Datos de prueba**: La BD viene con usuarios pre-creados:
   - **Admin**: `admin@ecommerce.com` / `admin123`
   - **Usuario**: `juan@email.com` / `password123`
4. **IDs**: Los IDs pueden variar, ajusta según tus datos
5. **Permisos**: Algunas operaciones requieren rol de administrador

## 🔍 CÓDIGOS DE RESPUESTA ESPERADOS

- **200**: Operación exitosa
- **201**: Recurso creado
- **400**: Error en datos enviados
- **401**: Token inválido o faltante
- **403**: Sin permisos suficientes
- **404**: Recurso no encontrado
- **409**: Conflicto (email duplicado, etc.)
- **500**: Error del servidor