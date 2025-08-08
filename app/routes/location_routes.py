from flask import Blueprint, request, jsonify
from app import db
from app.models import Country, States, City

location_bp = Blueprint('locations', __name__)

# ===============================
# RUTAS DE PAÍSES
# ===============================

@location_bp.route('/countries', methods=['GET'])
def get_countries():
    """Obtener todos los países"""
    try:
        countries = Country.query.all()
        return jsonify({
            'countries': [country.to_dict() for country in countries],
            'count': len(countries)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@location_bp.route('/countries', methods=['POST'])
def create_country():
    """Crear un nuevo país"""
    try:
        data = request.get_json()
        
        if not data.get('CountryName'):
            return jsonify({'error': 'CountryName es requerido'}), 400
        
        # Verificar si ya existe
        existing_country = Country.query.filter_by(
            CountryName=data['CountryName']
        ).first()
        
        if existing_country:
            return jsonify({'error': 'El país ya existe'}), 409
        
        new_country = Country(CountryName=data['CountryName'])
        db.session.add(new_country)
        db.session.commit()
        
        return jsonify({
            'message': 'País creado exitosamente',
            'country': new_country.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@location_bp.route('/countries/<int:country_id>', methods=['GET'])
def get_country(country_id):
    """Obtener un país específico con sus estados"""
    try:
        country = Country.query.get_or_404(country_id)
        
        include_states = request.args.get('include_states', False, type=bool)
        
        result = country.to_dict()
        
        if include_states:
            result['states'] = [state.to_dict() for state in country.states]
        
        return jsonify({'country': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===============================
# RUTAS DE ESTADOS/DEPARTAMENTOS
# ===============================

@location_bp.route('/states', methods=['GET'])
def get_states():
    """Obtener todos los estados"""
    try:
        country_id = request.args.get('country_id', type=int)
        
        query = States.query
        if country_id:
            query = query.filter_by(iD_Country=country_id)
        
        states = query.all()
        
        return jsonify({
            'states': [state.to_dict() for state in states],
            'count': len(states)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@location_bp.route('/states', methods=['POST'])
def create_state():
    """Crear un nuevo estado/departamento"""
    try:
        data = request.get_json()
        
        required_fields = ['StatesName', 'iD_Country']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Verificar que el país existe
        country = Country.query.get(data['iD_Country'])
        if not country:
            return jsonify({'error': 'País no encontrado'}), 404
        
        # Verificar si ya existe en ese país
        existing_state = States.query.filter_by(
            StatesName=data['StatesName'],
            iD_Country=data['iD_Country']
        ).first()
        
        if existing_state:
            return jsonify({'error': 'El estado ya existe en este país'}), 409
        
        new_state = States(
            StatesName=data['StatesName'],
            iD_Country=data['iD_Country']
        )
        
        db.session.add(new_state)
        db.session.commit()
        
        return jsonify({
            'message': 'Estado creado exitosamente',
            'state': new_state.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@location_bp.route('/states/<int:state_id>', methods=['GET'])
def get_state(state_id):
    """Obtener un estado específico con sus ciudades"""
    try:
        state = States.query.get_or_404(state_id)
        
        include_cities = request.args.get('include_cities', False, type=bool)
        
        result = state.to_dict()
        
        if include_cities:
            result['cities'] = [city.to_dict() for city in state.cities]
        
        return jsonify({'state': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@location_bp.route('/countries/<int:country_id>/states', methods=['GET'])
def get_states_by_country(country_id):
    """Obtener todos los estados de un país específico"""
    try:
        country = Country.query.get_or_404(country_id)
        states = States.query.filter_by(iD_Country=country_id).all()
        
        return jsonify({
            'country': country.to_dict(),
            'states': [state.to_dict() for state in states],
            'count': len(states)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===============================
# RUTAS DE CIUDADES
# ===============================

@location_bp.route('/cities', methods=['GET'])
def get_cities():
    """Obtener todas las ciudades"""
    try:
        state_id = request.args.get('state_id', type=int)
        country_id = request.args.get('country_id', type=int)
        
        query = City.query
        
        if state_id:
            query = query.filter_by(iD_States=state_id)
        elif country_id:
            # Filtrar por país a través de la relación con states
            query = query.join(States).filter(States.iD_Country == country_id)
        
        cities = query.all()
        
        return jsonify({
            'cities': [city.to_dict() for city in cities],
            'count': len(cities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@location_bp.route('/cities', methods=['POST'])
def create_city():
    """Crear una nueva ciudad"""
    try:
        data = request.get_json()
        
        required_fields = ['CityName', 'iD_States']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Verificar que el estado existe
        state = States.query.get(data['iD_States'])
        if not state:
            return jsonify({'error': 'Estado no encontrado'}), 404
        
        # Verificar si ya existe en ese estado
        existing_city = City.query.filter_by(
            CityName=data['CityName'],
            iD_States=data['iD_States']
        ).first()
        
        if existing_city:
            return jsonify({'error': 'La ciudad ya existe en este estado'}), 409
        
        new_city = City(
            CityName=data['CityName'],
            iD_States=data['iD_States']
        )
        
        db.session.add(new_city)
        db.session.commit()
        
        return jsonify({
            'message': 'Ciudad creada exitosamente',
            'city': new_city.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@location_bp.route('/cities/<int:city_id>', methods=['GET'])
def get_city(city_id):
    """Obtener una ciudad específica"""
    try:
        city = City.query.get_or_404(city_id)
        return jsonify({'city': city.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@location_bp.route('/states/<int:state_id>/cities', methods=['GET'])
def get_cities_by_state(state_id):
    """Obtener todas las ciudades de un estado específico"""
    try:
        state = States.query.get_or_404(state_id)
        cities = City.query.filter_by(iD_States=state_id).all()
        
        return jsonify({
            'state': state.to_dict(),
            'cities': [city.to_dict() for city in cities],
            'count': len(cities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@location_bp.route('/countries/<int:country_id>/cities', methods=['GET'])
def get_cities_by_country(country_id):
    """Obtener todas las ciudades de un país específico"""
    try:
        country = Country.query.get_or_404(country_id)
        
        # Obtener ciudades a través de la relación con states
        cities = City.query.join(States).filter(
            States.iD_Country == country_id
        ).all()
        
        return jsonify({
            'country': country.to_dict(),
            'cities': [city.to_dict() for city in cities],
            'count': len(cities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===============================
# RUTAS DE JERARQUÍA COMPLETA
# ===============================

@location_bp.route('/hierarchy', methods=['GET'])
def get_location_hierarchy():
    """Obtener jerarquía completa de ubicaciones"""
    try:
        countries = Country.query.all()
        
        result = []
        for country in countries:
            country_data = country.to_dict()
            country_data['states'] = []
            
            for state in country.states:
                state_data = state.to_dict()
                state_data['cities'] = [city.to_dict() for city in state.cities]
                country_data['states'].append(state_data)
            
            result.append(country_data)
        
        return jsonify({
            'hierarchy': result,
            'countries_count': len(countries)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@location_bp.route('/search', methods=['GET'])
def search_locations():
    """Buscar ubicaciones por nombre"""
    try:
        query_text = request.args.get('q', '')
        location_type = request.args.get('type', 'all')  # all, country, state, city
        
        if not query_text:
            return jsonify({'results': []}), 200
        
        results = []
        
        if location_type in ['all', 'country']:
            countries = Country.query.filter(
                Country.CountryName.contains(query_text)
            ).limit(10).all()
            
            for country in countries:
                results.append({
                    'type': 'country',
                    'data': country.to_dict()
                })
        
        if location_type in ['all', 'state']:
            states = States.query.filter(
                States.StatesName.contains(query_text)
            ).limit(10).all()
            
            for state in states:
                results.append({
                    'type': 'state',
                    'data': state.to_dict()
                })
        
        if location_type in ['all', 'city']:
            cities = City.query.filter(
                City.CityName.contains(query_text)
            ).limit(10).all()
            
            for city in cities:
                results.append({
                    'type': 'city',
                    'data': city.to_dict()
                })
        
        return jsonify({
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500