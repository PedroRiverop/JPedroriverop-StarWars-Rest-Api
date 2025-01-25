
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250))
    last_name = db.Column(db.String(250))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean(), default=True)

    favorite_characters = db.relationship('FavoriteCharacter', back_populates='user')
    favorite_planets = db.relationship('FavoritePlanet', back_populates='user')


    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "joined_date": self.joined_date,
            "is_active": self.is_active
            # do not serialize the password, its a security breach
        }
    
    def serialize_favorites(self):
        result = {
            "user": self.serialize(),
            "favorites": {
                "characters": [fc.character.serialize() for fc in self.favorite_characters],
                "planets": [fp.planet.serialize() for fp in self.favorite_planets]
            }
        }
        return result
    
class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500))  
    species = db.Column(db.String(250))  
    homeworld = db.Column(db.String(250))  
    special_ability = db.Column(db.String(250))  
    affiliation = db.Column(db.String(250))  
    favorite_weapon = db.Column(db.String(250)) 
    eye_color = db.Column(db.String(250))
    hair_color = db.Column(db.String(250))
    birth_year = db.Column(db.String(250))
    gender = db.Column(db.String(6))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    political_group_id = db.Column(db.Integer, db.ForeignKey('political_groups.id'))

    favorite_characters = db.relationship('FavoriteCharacter', back_populates='character')
    political_group = db.relationship('PoliticalGroup', back_populates='members')
    vehicles = db.relationship('Vehicle', back_populates='character')

    def __repr__(self):
        return '<Character %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "species": self.species,
            "homeworld": self.homeworld,
            "special_ability": self.special_ability,
            "affiliation": self.affiliation,
            "favorite_weapon": self.favorite_weapon,
            "eye_color": self.eye_color,
            "hair_color": self.hair_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    
class Planet(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500))  
    diameter = db.Column(db.Float) 
    orbital_period = db.Column(db.Integer)  
    terrain_type = db.Column(db.String(250))  
    atmosphere = db.Column(db.String(250))  
    population = db.Column(db.BigInteger)  
    climate = db.Column(db.String(250))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

   
    favorite_planets = db.relationship('FavoritePlanet', back_populates='planet')
    vehicles = db.relationship('Vehicle', back_populates='planet')


    def __repr__(self):
       return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "diameter": self.diameter,
            "orbital_period": self.orbital_period,
            "terrain_type": self.terrain_type,
            "atmosphere": self.atmosphere,
            "population": self.population,
            "climate": self.climate,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
class FavoriteCharacter(db.Model):
    __tablename__ = 'favorite_characters'
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    character = db.relationship('Character', back_populates='favorite_characters')
    user = db.relationship('User', back_populates='favorite_characters')

    def __repr__(self):
         return '<FavoriteCharacter %r>' % self.id

class FavoritePlanet(db.Model):
    __tablename__ = 'favorite_planets'
    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    planet = db.relationship('Planet', back_populates='favorite_planets')
    user = db.relationship('User', back_populates='favorite_planets')

    def __repr__(self):
       return '<FavoritePlanet %r>' % self.id





class PoliticalGroup(db.Model):
    __tablename__ = 'political_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    leader = db.Column(db.String(250))
    affiliation = db.Column(db.String(250))
    allies = db.Column(db.String(250))
    enemies = db.Column(db.String(250))
    description = db.Column(db.String(500))
    members = db.relationship('Character', back_populates='political_group')
    
    def __repr__(self):
        return '<FavoriteVehicle %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "leader": self.leader,
            "affiliation": self.affiliation,
            "allies": self.allies,
            "enemies": self.enemies,
            "description": self.description
        }


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    type = db.Column(db.String(100))
    manufacturer = db.Column(db.String(250))
    crew_capacity = db.Column(db.Integer)
    weaponry = db.Column(db.String(500))
    model = db.Column(db.String(250))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))


    planet = db.relationship('Planet', back_populates='vehicles')
    character = db.relationship('Character', back_populates='vehicles')

    def __repr__(self):
         return '<FavoriteVehicle %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "manufacturer": self.manufacturer,
            "crew_capacity": self.crew_capacity,
            "weaponry": self.weaponry,
            "model": self.model,
            "planet": self.planet.serialize() if self.planet else None,
            "character": self.character.serialize() if self.character else None
        }
