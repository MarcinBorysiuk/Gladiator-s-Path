from app import db, login_manager, bcrypt
from flask import flash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    email_address = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(60), nullable=False)
    gladiator = db.relationship('Player', backref='owner')

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    gold = db.Column(db.Integer)
    picture = db.Column(db.String, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.Integer)
    max_experience = db.Column(db.Integer)
    max_hp = db.Column(db.Integer)
    hp = db.Column(db.Integer)
    armor = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    dexterity = db.Column(db.Integer)
    charisma = db.Column(db.Integer)
    vitality = db.Column(db.Integer)
    attack_cost = db.Column(db.Integer, default=100)
    dexterity_cost = db.Column(db.Integer, default=100)
    charisma_cost = db.Column(db.Integer, default=100)
    vitality_cost = db.Column(db.Integer, default=100)
    stat_point = db.Column(db.Integer)
    expedition_points = db.Column(db.Integer)
    dungeon_points = db.Column(db.Integer)
    inventory_slots = db.Column(db.Integer, default=0)
    weapons = db.relationship('Weapon', backref='owner')
    armors = db.relationship('Armor', backref='owner')
    shields = db.relationship('Shield', backref='owner')
    boots = db.relationship('Boots', backref='owner')
    helmets = db.relationship('Helmet', backref='owner')
    potions = db.relationship('Potion', backref='owner')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def create_new(self, name, owner_id):
        self.name = name
        self.picture = "https://s20-en.gladiatus.gameforge.com/game/9194/img/faces/gladiator_1_m.jpg"
        self.level = 1
        self.gold = 500
        self.experience = 0
        self.max_experience = 10
        self.max_hp = 300
        self.hp = 300
        self.armor = 0
        self.attack = 1
        self.dexterity = 1
        self.charisma = 1
        self.vitality = 1
        self.attack_cost = 100
        self.dexterity_cost = 100
        self.charisma_cost = 100
        self.vitality_cost = 100
        self.stat_point = 5
        self.expedition_points = 12
        self.dungeon_points = 12
        self.inventory_slots = 0
        self.owner_id = owner_id

        db.session.commit()

    

    def get_exp_for_current_level(self):
        exp_per_level = {
            1:10,
            2:15,
            3:20,
            4:25,
            5:30,
            6:40,
            7:50,
            8:60,
            9:70,
            10:80,
            11:95,
            12:110,
            13:125,
            14:140,
            15:160,
            16:180,
            17:200

        }

        for k,v in exp_per_level.items():
            if self.level == k:
                self.max_experience = v
                db.session.commit()


    def level_up(self):
        if self.experience > self.max_experience:
            self.level += 1
            self.experience -= self.max_experience
        elif self.max_experience == self.max_experience:
            self.level += 1
            self.experience = 0
            
        self.hp = self.max_hp
        self.expedition_points = 12
        self.dungeon_points = 12
        self.stat_point += 5
        db.session.commit()


    def train_stats(self, stat):
        if stat == 'attack':
            if self.stat_point > 0:
                self.attack += 1
                self.stat_point -= 1
                db.session.commit()
                flash("Added 1 Strength", category='success')
            else:
                if self.gold >= self.attack_cost:
                    self.gold -= self.attack_cost
                    self.attack += 1
                    self.attack_cost += 100
                    db.session.commit()
                    flash("Added 1 Strength", category='success')
                else:
                    flash("Not enough Gold!", category='danger')
        elif stat == 'dexterity':
            if self.stat_point > 0:
                self.dexterity += 1
                self.stat_point -= 1
                db.session.commit()
                flash("Added 1 Dexterity", category='success')
            else:
                if self.gold >= self.dexterity_cost:
                    self.gold -= self.dexterity_cost
                    self.dexterity += 1
                    self.dexterity_cost += 100
                    db.session.commit()
                    flash("Added 1 Dexterity", category='success')
                else:
                    flash("Not enough Gold!", category='danger')
        elif stat == 'charisma':
            if self.stat_point > 0:
                self.charisma += 1
                self.stat_point -= 1
                db.session.commit()
                flash("Added 1 Charisma", category='success')
            else:
                if self.gold >= self.charisma:
                    self.gold -= self.charisma_cost
                    self.charisma += 1
                    self.charisma_cost += 100
                    db.session.commit()
                    flash("Added 1 Charisma", category='success')
                else:
                    flash("Not enough Gold!", category='danger')
        elif stat == 'vitality':
            if self.stat_point > 0:
                self.vitality += 1
                self.max_hp += 10
                self.stat_point -= 1
                db.session.commit()
                flash("Added 1 Vitality", category='success')
            else:
                if self.gold >= self.vitality_cost:
                    self.gold -= self.vitality_cost
                    self.vitality += 1
                    self.max_hp += 10
                    self.vitality_cost += 100
                    db.session.commit()
                    flash("Added 1 Vitality", category='success')
                else:
                    flash("Not enough Gold!", category='danger')


class Weapon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    damage = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer)
    is_equipped = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('player.id'))

    

class Armor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    armor = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    is_equipped = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('player.id'))


class Shield(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    armor = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    is_equipped = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('player.id'))



class Boots(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    armor = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    is_equipped = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('player.id'))


class Helmet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    armor = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    is_equipped = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('player.id'))



class Potion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    heal = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    used = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('player.id'))



class Enemy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    picture = db.Column(db.String, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    dexterity = db.Column(db.Integer)