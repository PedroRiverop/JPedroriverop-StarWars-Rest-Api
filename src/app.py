"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Vehicle, PoliticalGroup, FavoriteCharacter, FavoritePlanet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/people', methods=['GET'])
def get_all_people():
    people = Character.query.all()
    return jsonify([person.serialize() for person in people]), 200



@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = Character.query.get(people_id)
    if not person:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(person.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        if not data or 'first_name' not in data or 'last_name' not in data or 'email' not in data or 'password' not in data or 'is_active' not in data:
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],  # En un escenario real, deberías hash esta contraseña
            is_active=data['is_active']
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify(new_user.serialize()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize_favorites()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    

    favorite_planet = FavoritePlanet(user_id=user.id, planet_id=planet.id)

    db.session.add(favorite_planet)
    db.session.commit()
    return jsonify(favorite_planet.serialize()), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])

def add_favorite_people(people_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    character = Character.query.get(people_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not character:
        return jsonify({"error": "Character not found"}), 404

    favorite_character = FavoriteCharacter(user_id=user.id, character_id=character.id)
    db.session.add(favorite_character)
    db.session.commit()
    return jsonify(favorite_character.serialize()), 201



@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    favorite_planet = FavoritePlanet.query.filter_by(user_id=user.id, planet_id=planet.id).first()
    if not favorite_planet:
        return jsonify({"error": "Favorite planet not found"}), 404

    db.session.delete(favorite_planet)
    db.session.commit()
    return jsonify({"message": "Favorite planet removed successfully"}), 200



@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people(people_id):
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    character = Character.query.get(people_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not character:
        return jsonify({"error": "Character not found"}), 404

    favorite_character = FavoriteCharacter.query.filter_by(user_id=user.id, character_id=character.id).first()
    if not favorite_character:
        return jsonify({"error": "Favorite character not found"}), 404

    db.session.delete(favorite_character)
    db.session.commit()
    return jsonify({"message": "Favorite character removed successfully"}), 200



@app.route('/planets', methods=['POST'])
def add_planet():
    data = request.get_json()
    new_planet = Planet(
        name=data['name'],
        description=data['description'],
        diameter=data['diameter'],
        orbital_period=data['orbital_period'],
        terrain_type=data['terrain_type'],
        atmosphere=data['atmosphere'],
        population=data['population'],
        climate=data['climate']
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    data = request.get_json()
    planet = Planet.query.get(planet_id)
    
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    
    planet.name = data['name']
    planet.description = data['description']
    planet.diameter = data['diameter']
    planet.orbital_period = data['orbital_period']
    planet.terrain_type = data['terrain_type']
    planet.atmosphere = data['atmosphere']
    planet.population = data['population']
    planet.climate = data['climate']
    db.session.commit()
    
    return jsonify(planet.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planet deleted successfully"}), 200



@app.route('/people', methods=['POST'])
def add_character():
    data = request.get_json()
    new_character = Character(
        name=data['name'],
        description=data['description'],
        species=data['species'],
        homeworld=data['homeworld'],
        special_ability=data['special_ability'],
        affiliation=data['affiliation'],
        favorite_weapon=data['favorite_weapon'],
        eye_color=data['eye_color'],
        hair_color=data['hair_color'],
        birth_year=data['birth_year'],
        gender=data['gender']
    )
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 201

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_character(people_id):
    data = request.get_json()
    character = Character.query.get(people_id)
    
    if not character:
        return jsonify({"error": "Character not found"}), 404
    
    character.name = data['name']
    character.description = data['description']
    character.species = data['species']
    character.homeworld = data['homeworld']
    character.special_ability = data['special_ability']
    character.affiliation = data['affiliation']
    character.favorite_weapon = data['favorite_weapon']
    character.eye_color = data['eye_color']
    character.hair_color = data['hair_color']
    character.birth_year = data['birth_year']
    character.gender = data['gender']
    db.session.commit()
    
    return jsonify(character.serialize()), 200



@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_character(people_id):
    character = Character.query.get(people_id)
    
    if not character:
        return jsonify({"error": "Character not found"}), 404
    
    db.session.delete(character)
    db.session.commit()
    return jsonify({"message": "Character deleted successfully"}), 200


@app.route('/political_groups', methods=['GET'])
def get_all_political_groups():
    groups = PoliticalGroup.query.all()
    return jsonify([group.serialize() for group in groups]), 200

@app.route('/political_groups', methods=['POST'])
def add_political_group():
    data = request.get_json()
    new_group = PoliticalGroup(
        name=data['name'],
        leader=data['leader'],
        affiliation=data['affiliation'],
        allies=data['allies'],
        enemies=data['enemies'],
        description=data['description']
    )
    db.session.add(new_group)
    db.session.commit()
    return jsonify(new_group.serialize()), 201

@app.route('/political_groups/<int:group_id>', methods=['PUT'])
def update_political_group(group_id):
    data = request.get_json()
    group = PoliticalGroup.query.get(group_id)
    
    if not group:
        return jsonify({"error": "Political group not found"}), 404
    
    group.name = data['name']
    group.leader = data['leader']
    group.affiliation = data['affiliation']
    group.allies = data['allies']
    group.enemies = data['enemies']
    group.description = data['description']
    db.session.commit()
    
    return jsonify(group.serialize()), 200

@app.route('/political_groups/<int:group_id>', methods=['DELETE'])
def delete_political_group(group_id):
    group = PoliticalGroup.query.get(group_id)
    
    if not group:
        return jsonify({"error": "Political group not found"}), 404
    
    db.session.delete(group)
    db.session.commit()
    return jsonify({"message": "Political group deleted successfully"}), 200

@app.route('/vehicles', methods=['GET'])
def get_all_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([vehicle.serialize() for vehicle in vehicles]), 200



@app.route('/vehicles', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    new_vehicle = Vehicle(
        name=data['name'],
        type=data['type'],
        manufacturer=data['manufacturer'],
        crew_capacity=data['crew_capacity'],
        weaponry=data['weaponry'],
        model=data['model'],
        planet_id=data['planet_id'],
        character_id=data['character_id']
    )
    db.session.add(new_vehicle)
    db.session.commit()
    return jsonify(new_vehicle.serialize()), 201

@app.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    data = request.get_json()
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    
    vehicle.name = data['name']
    vehicle.type = data['type']
    vehicle.manufacturer = data['manufacturer']
    vehicle.crew_capacity = data['crew_capacity']
    vehicle.weaponry = data['weaponry']
    vehicle.model = data['model']
    vehicle.planet_id = data['planet_id']
    vehicle.character_id = data['character_id']
    db.session.commit()
    
    return jsonify(vehicle.serialize()), 200

@app.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"message": "Vehicle deleted successfully"}), 200




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
