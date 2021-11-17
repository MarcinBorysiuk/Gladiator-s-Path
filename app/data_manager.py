from app import db
from app.models import *


class DataManagement:
    def __init__(self, db):
        self._db = db

    def create_user(self, name, email, password):
        user = User(name=name, email_address=email, password=password)
        db.session.add(user)
        db.session.commit()

    def filter_user_by_name(self, name):
        user = User.query.filter_by(name=name).first()
        return user

    def create_gladiator(self, name, id):
        gladiator = Player()
        gladiator.create_new(name=name, owner_id=id)
        db.session.add(gladiator)
        db.session.commit()

    def query_all_gladiators(self):
        gladiators = Player.query.all()
        return gladiators

    def filter_gladiator_by_name(self, name):
        gladiator = Player.query.filter_by(name=name).first()
        return gladiator

    def query_enemies(self, start, end):
        enemies = Enemy.query.all()
        return enemies[start:end]

    def filter_enemy_by_id(self, id):
        enemy = Enemy.query.filter_by(id=id).first()
        return enemy

    def query_all_weapons(self):
        weapons = Weapon.query.all()
        return weapons

    def query_all_armors(self):
        armors = Armor.query.all()
        return armors

    def query_all_shields(self):
        shields = Shield.query.all()
        return shields

    def query_all_helmets(self):
        helmets = Helmet.query.all()
        return helmets

    def query_all_boots(self):
        boots = Boots.query.all()
        return boots

    def query_all_potions(self):
        potions = Potion.query.all()
        return potions

    def filter_weapon_by_id(self, id):
        weapon = Weapon.query.filter_by(id=id).first()
        return weapon

    def filter_armor_by_id(self, id):
        armor = Armor.query.filter_by(id=id).first()
        return armor

    def filter_shield_by_id(self, id):
        shield = Shield.query.filter_by(id=id).first()
        return shield

    def filter_helmet_by_id(self, id):
        helmet = Helmet.query.filter_by(id=id).first()
        return helmet
    
    def filter_boots_by_id(self, id):
        boots = Boots.query.filter_by(id=id).first()
        return boots

    def filter_potion_by_id(self, id):
        potion = Potion.query.filter_by(id=id).first()
        return potion
