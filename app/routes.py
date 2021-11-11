from flask import render_template, redirect, url_for, flash, request
import flask_login
from app import app, db
from app.models import *
from app.forms import *
from app.game_logic import *
from flask_login import login_user, logout_user, login_required



@app.route('/')
def home_page():
    return render_template('home_page.html')

  
@app.route('/register', methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            name=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data
        )

        db.session.add(user_to_create)
        db.session.commit()

        
        return redirect(f'create_gladiator/{user_to_create.name}')
    
    if form.errors != {}:
        for error in form.errors.values():
            flash(error[0], category='danger')

    return render_template('register_page.html', form=form)


@app.route('/create_gladiator/<string:username>', methods=["GET", "POST"])
def create_gladiator(username):
    user = User.query.filter_by(name=username).first()
    form = CreateGladiatorForm()
    if form.validate_on_submit():
        name = form.name.data
        
        new_gladiator = Player()
        new_gladiator.create_new(name=name, owner_id=user.id)
        db.session.add(new_gladiator)
        db.session.commit()
        login_user(user)
        flash(f"Account created successfully! You are now logged in as {user.name}", category="success")
        flash(f"{new_gladiator.name} created successfully! Welcome to the game!", category="success")
        flash(f"You have 5 stat points available. Go to training", category='success')
        return redirect(url_for('overview'))

    if form.errors != {}:
        for error in form.errors.values():
            flash(error[0], category='danger')

    return render_template('create_gladiator.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(name=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
    ):
            login_user(attempted_user)
            flash(f"Success! You are logged in as {attempted_user.name}", category="success")
            return redirect(url_for('overview'))
        else:
            flash("Username or password do not match! Try again.", category='danger')
    return render_template('login_page.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out.', category='info')
    return redirect(url_for('home_page'))


@app.route('/overview')
@login_required
def overview():
    
    user = flask_login.current_user
    player = user.gladiator[0]
    empty_inventory = ['']*18
    inventory = []
    weapons = player.weapons
    armors = player.armors
    shields = player.shields
    helmets = player.helmets
    boots = player.boots
    potions = player.potions
    items = weapons + armors + shields + helmets + boots + potions
    equipped_weapon = []
    equipped_armor = []
    equipped_shield = []
    equipped_helmet = []
    equipped_boots = []
    
    
    for item in items:
        if isinstance(item, Weapon):
            if item.is_equipped == True:
                equipped_weapon.append(item)
                items.remove(item)

    for item in items:
        if isinstance(item, Armor):
            if item.is_equipped == True:
                equipped_armor.append(item)
                items.remove(item)

    for item in items:
        if isinstance(item, Shield):
            if item.is_equipped == True:
                equipped_shield.append(item)
                items.remove(item)

    for item in items:
        if isinstance(item, Helmet):
            if item.is_equipped == True:
                equipped_helmet.append(item)
                items.remove(item)

    for item in items:
        if isinstance(item, Boots):
            if item.is_equipped == True:
                equipped_boots.append(item)
                items.remove(item)

    if equipped_weapon:
        equipped_weapon = equipped_weapon[0]
    if equipped_armor:
        equipped_armor = equipped_armor[0]
    if equipped_shield:
        equipped_shield = equipped_shield[0]
    if equipped_helmet:
        equipped_helmet = equipped_helmet[0]
    if equipped_boots:
        equipped_boots = equipped_boots[0]

    if not items:
        inventory = empty_inventory
    else:
        inventory.extend(items)

    for item in empty_inventory:
        if len(inventory) < 18:
            inventory.append(item)
    
    return render_template(
        'overview.html',
        player=player,
        inventory=inventory,
        items=items,
        weapons=weapons,
        armors=armors,
        shields=shields,
        helmets=helmets,
        boots=boots,
        potions=potions,
        equipped_weapon=equipped_weapon,
        equipped_armor=equipped_armor,
        equipped_shield=equipped_shield,
        equipped_helmet=equipped_helmet,
        equipped_boots=equipped_boots
        )



@app.route('/training')
@login_required
def train():
    user = flask_login.current_user
    player = user.gladiator[0]
    return render_template('training_page.html', player=player)

@app.route('/add/<string:stat>')
@login_required
def add_stats(stat):
    user = flask_login.current_user
    player = user.gladiator[0]
    player.train_stats(stat)
    return redirect(url_for('train'))


@app.route('/expedition')
@login_required
def choose_expedition():
    user = flask_login.current_user
    player = user.gladiator[0]
    return render_template('choose_expedition.html', player=player)

@app.route('/expedition/<int:id>')
@login_required
def choose_enemy(id):
    user = flask_login.current_user
    player = user.gladiator[0]
    if id == 1:
        enemies = Enemy.query.all()[:4]
    if id == 2:
        enemies = Enemy.query.all()[4:8]
    if id == 3:
        enemies = Enemy.query.all()[8:12]

    return render_template('enemy_page.html', player=player, enemies=enemies, id=id)



@app.route('/expedition/fight/<int:id>')
@login_required
def fight(id):
    
    user = flask_login.current_user
    player = user.gladiator[0]
    enemy_to_fight = Enemy.query.filter_by(id=id).first()

    if player.expedition_points == 0:
        flash("You don't have any expedition points!", category='danger')
        return redirect(url_for('choose_expedition'))
    elif player.hp == 0:
        flash("Heal Yourself!", category='danger')
        return redirect(url_for('choose_expedition'))
    else:
    
        history_of_fight = fight_enemy(player, enemy_to_fight)
        win_statement = history_of_fight.pop()
        reward = history_of_fight.pop()
        player.expedition_points -= 1
        if player.double_exp > 0:
            player.double_exp -= 1
        db.session.commit()

        if player.experience >= player.max_experience:
            player.level_up()
            player.get_exp_for_current_level()
            flash(f"Congratulations! You've achived level {player.level}. Your HP and Expedition points are now restored!", category='success')
            flash(f"You also gain 5 stat points and your HP increase by 25!", category="success")
            if player.level == 10:
                flash("Misty Mountains are now unlocked!", category="success")
            if player.level == 20:
                flash("Fire Temple is now unlocked!",category="success")
            
            
    return render_template(
        'fight_page.html',
        history_of_fight=history_of_fight,
        player=player, id=id,
        win_statement=win_statement,
        enemy_to_fight=enemy_to_fight,
        reward=reward,
        player_deal_critical=player_deal_critical(player)
        )

@app.route('/blacksmith')
@login_required
def blacksmith():

    blacksmith_weapons = Weapon.query.all()
    weapons_in_store = []
    for weapon in blacksmith_weapons:
        if weapon.owner == None:
            weapons_in_store.append(weapon)

    blacksmith_weapons = weapons_in_store
    blacksmith_weapons = sorted(blacksmith_weapons, key=lambda weapon: weapon.level)

    while len(blacksmith_weapons) < 18:
        blacksmith_weapons.append('')
    user = flask_login.current_user
    player = user.gladiator[0]

    weapons = player.weapons
    armors = player.armors
    shields = player.shields
    helmets = player.helmets
    boots = player.boots
    potions = player.potions

    inventory = weapons + armors + shields + helmets + boots
    inventory = [item for item in inventory if item.is_equipped == False]
    inventory = inventory + potions

    while len(inventory) < 18:
        inventory.append('')

    return render_template(
        'blacksmith_page.html',
        blacksmith_weapons=blacksmith_weapons,
        player=player,
        inventory=inventory,
        weapons=weapons,
        armors=armors,
        shields=shields,
        helmets=helmets,
        boots=boots,
        potions=potions
        )



@app.route('/armor')
@login_required
def armorer():

    armorer_items = []
    armorer_shields = Shield.query.all()
    armorer_armors = Armor.query.all()
    armorer_helmets = Helmet.query.all()
    armorer_boots = Boots.query.all()
    items = armorer_armors + armorer_shields + armorer_helmets + armorer_boots

    for item in items:
        if item.owner == None:
            armorer_items.append(item)

    items = armorer_items
    items = sorted(items, key=lambda item: item.level)

    while len(items) < 36:
        items.append('')

    user = flask_login.current_user
    player = user.gladiator[0]

    weapons = player.weapons
    armors = player.armors
    shields = player.shields
    helmets = player.helmets
    boots = player.boots
    potions = player.potions

    inventory = weapons + armors + shields + helmets + boots
    inventory = [item for item in inventory if item.is_equipped == False]
    inventory = inventory + potions

    while len(inventory) < 18:
        inventory.append('')
    
    return render_template(
        'armor_page.html',
        items=items,
        player=player,
        weapons=weapons,
        armors=armors,
        shields=shields,
        helmets=helmets,
        boots=boots,
        potions=potions,
        armorer_armors=armorer_armors,
        armorer_shields=armorer_shields,
        armorer_helmets=armorer_helmets,
        armorer_boots=armorer_boots,
        inventory=inventory
        )



@app.route('/potions')
@login_required
def potions():
    potion_master_potions = Potion.query.all()
    potion_in_store = []
    for potion in potion_master_potions:
        if potion.owner == None and potion.heal != 0:
            potion_in_store.append(potion)

    potion_master_potions = potion_in_store
    potion_master_potions = sorted(potion_master_potions, key=lambda potion: potion.level)

    for potion in Potion.query.all():
        if potion.description:
            potion_master_potions.append(potion)

    while len(potion_master_potions) < 18:
        potion_master_potions.append('')
    user = flask_login.current_user
    player = user.gladiator[0]

    weapons = player.weapons
    armors = player.armors
    shields = player.shields
    helmets = player.helmets
    boots = player.boots
    potions = player.potions

    inventory = weapons + armors + shields + helmets + boots
    inventory = [item for item in inventory if item.is_equipped == False]
    inventory = inventory + potions

    while len(inventory) < 18:
        inventory.append('')

    return render_template(
        'potion_page.html',
        potion_master_potions=potion_master_potions,
        player=player,
        inventory=inventory,
        weapons=weapons,
        armors=armors,
        shields=shields,
        helmets=helmets,
        boots=boots,
        potions=potions
        )


@app.route('/blacksmith/buy/<int:item_id>', methods=["GET", "POST"])
@login_required
def buy_weapon(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    weapon_to_buy = Weapon.query.filter_by(id=item_id).first()
    if request.method == "POST":
        if player.inventory_slots == 18:
            flash("Your Inventory is full!", category='danger')
        if player.level >= weapon_to_buy.level and player.gold >= weapon_to_buy.cost and player.inventory_slots < 18:
            player.gold -= weapon_to_buy.cost
            if weapon_to_buy.charisma:
                new_weapon = Weapon(
                    name=weapon_to_buy.name,
                    picture=weapon_to_buy.picture,
                    level=weapon_to_buy.level,
                    min_dmg=weapon_to_buy.min_dmg,
                    max_dmg=weapon_to_buy.max_dmg,
                    cost=weapon_to_buy.cost,
                    charisma=weapon_to_buy.charisma,
                    owner=player
                    )
            else:
                new_weapon = Weapon(
                    name=weapon_to_buy.name,
                    picture=weapon_to_buy.picture,
                    level=weapon_to_buy.level,
                    min_dmg=weapon_to_buy.min_dmg,
                    max_dmg=weapon_to_buy.max_dmg,
                    cost=weapon_to_buy.cost,
                    owner=player
                    )
            player.inventory_slots += 1
            db.session.add(new_weapon)
            db.session.commit()
            flash(f"Successfully bought {weapon_to_buy.name} for {weapon_to_buy.cost} gold", category='success')
            return redirect(url_for('blacksmith'))
        else:
            return redirect(url_for('blacksmith'))
    else:
        return render_template('blacksmith_page.html', player=player, weapon_to_buy=weapon_to_buy)


@app.route('/armor/buy/<int:item_id>', methods=["GET", "POST"])
@login_required
def buy_armor(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    armor_to_buy = Armor.query.filter_by(id=item_id).first()
    if request.method == "POST":
        if player.inventory_slots == 18:
            flash("Your Inventory is full!", category='danger')
        if player.level >= armor_to_buy.level and player.gold >= armor_to_buy.cost and player.inventory_slots < 18:
            player.gold -= armor_to_buy.cost
            if armor_to_buy.vitality:
                new_armor = Armor(
                    name=armor_to_buy.name,
                    picture=armor_to_buy.picture,
                    level=armor_to_buy.level,
                    armor=armor_to_buy.armor,
                    cost=armor_to_buy.cost,
                    vitality=armor_to_buy.vitality,
                    owner=player
                    )
            else:
                new_armor = Armor(
                    name=armor_to_buy.name,
                    picture=armor_to_buy.picture,
                    level=armor_to_buy.level,
                    armor=armor_to_buy.armor,
                    cost=armor_to_buy.cost,
                    owner=player
                    )
            player.inventory_slots += 1
            db.session.add(new_armor)
            db.session.commit()
            flash(f"Successfully bought {armor_to_buy.name} for {armor_to_buy.cost} gold", category='success')
            return redirect(url_for('armorer'))
        else:
            return redirect(url_for('armorer'))
    else:
        return render_template('armor_page.html', player=player, armor_to_buy=armor_to_buy)


@app.route('/shield/buy/<int:item_id>', methods=["GET", "POST"])
@login_required
def buy_shield(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    shield_to_buy = Shield.query.filter_by(id=item_id).first()
    if request.method == "POST":
        if player.inventory_slots == 18:
            flash("Your Inventory is full!", category='danger')
        if player.level >= shield_to_buy.level and player.gold >= shield_to_buy.cost and player.inventory_slots < 18:
            player.gold -= shield_to_buy.cost
            if shield_to_buy.charisma:
                new_shield = Shield(
                    name=shield_to_buy.name,
                    picture=shield_to_buy.picture,
                    level=shield_to_buy.level,
                    armor=shield_to_buy.armor,
                    cost=shield_to_buy.cost,
                    charisma=shield_to_buy.charisma,
                    owner=player
                    )
            else:
                new_shield = Shield(
                    name=shield_to_buy.name,
                    picture=shield_to_buy.picture,
                    level=shield_to_buy.level,
                    armor=shield_to_buy.armor,
                    cost=shield_to_buy.cost,
                    owner=player
                    )
            player.inventory_slots += 1
            db.session.add(new_shield)
            db.session.commit()
            flash(f"Successfully bought {shield_to_buy.name} for {shield_to_buy.cost} gold", category='success')
            return redirect(url_for('armorer'))
        else:
            return redirect(url_for('armorer'))
    else:
        return render_template('armor_page.html', player=player, shield_to_buy=shield_to_buy)


@app.route('/helmet/buy/<int:item_id>', methods=["GET", "POST"])
@login_required
def buy_helmet(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    helmet_to_buy = Helmet.query.filter_by(id=item_id).first()
    if request.method == "POST":
        if player.inventory_slots == 18:
            flash("Your Inventory is full!", category='danger')
        if player.level >= helmet_to_buy.level and player.gold >= helmet_to_buy.cost and player.inventory_slots < 18:
            player.gold -= helmet_to_buy.cost
            if helmet_to_buy.vitality:
                new_helmet = Helmet(
                    name=helmet_to_buy.name,
                    picture=helmet_to_buy.picture,
                    level=helmet_to_buy.level,
                    armor=helmet_to_buy.armor,
                    cost=helmet_to_buy.cost,
                    vitality=helmet_to_buy.vitality,
                    owner=player
                    )
            else:
                new_helmet = Helmet(
                    name=helmet_to_buy.name,
                    picture=helmet_to_buy.picture,
                    level=helmet_to_buy.level,
                    armor=helmet_to_buy.armor,
                    cost=helmet_to_buy.cost,
                    owner=player
                    )
            player.inventory_slots += 1
            db.session.add(new_helmet)
            db.session.commit()
            flash(f"Successfully bought {helmet_to_buy.name} for {helmet_to_buy.cost} gold", category='success')
            return redirect(url_for('armorer'))
        else:
            return redirect(url_for('armorer'))
    else:
        return render_template('armor_page.html', player=player, helmet_to_buy=helmet_to_buy)

@app.route('/boots/buy/<int:item_id>', methods=["GET", "POST"])
@login_required
def buy_boots(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    boots_to_buy = Boots.query.filter_by(id=item_id).first()
    if request.method == "POST":
        if player.inventory_slots == 18:
            flash("Your Inventory is full!", category='danger')
        if player.level >= boots_to_buy.level and player.gold >= boots_to_buy.cost and player.inventory_slots < 18:
            player.gold -= boots_to_buy.cost
            if boots_to_buy.dexterity:
                new_boots = Boots(
                    name=boots_to_buy.name,
                    picture=boots_to_buy.picture,
                    level=boots_to_buy.level,
                    armor=boots_to_buy.armor,
                    cost=boots_to_buy.cost,
                    dexterity=boots_to_buy.dexterity,
                    owner=player
                    )
            else:
                new_boots = Boots(
                    name=boots_to_buy.name,
                    picture=boots_to_buy.picture,
                    level=boots_to_buy.level,
                    armor=boots_to_buy.armor,
                    cost=boots_to_buy.cost,
                    dexterity=boots_to_buy.dexterity,
                    owner=player
                    )
            player.inventory_slots += 1
            db.session.add(new_boots)
            db.session.commit()
            flash(f"Successfully bought {boots_to_buy.name} for {boots_to_buy.cost} gold", category='success')
            return redirect(url_for('armorer'))
        else:
            return redirect(url_for('armorer'))
    else:
        return render_template('armor_page.html', player=player, boots_to_buy=boots_to_buy)


@app.route('/potion/buy/<int:item_id>', methods=["GET", "POST"])
@login_required
def buy_potion(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    potion_to_buy = Potion.query.filter_by(id=item_id).first()
    if request.method == "POST":
        if player.inventory_slots == 18:
            flash("Your Inventory is full!", category='danger')
            return redirect(url_for('potions'))
        if player.level >= potion_to_buy.level and player.gold >= potion_to_buy.cost and player.inventory_slots < 18:
            player.gold -= potion_to_buy.cost
            if potion_to_buy.description:
                new_potion = Potion(
                name=potion_to_buy.name,
                picture=potion_to_buy.picture,
                level=potion_to_buy.level,
                heal=potion_to_buy.heal,
                cost=potion_to_buy.cost,
                description=potion_to_buy.description,
                owner=player
                )
            else:
                new_potion = Potion(
                    name=potion_to_buy.name,
                    picture=potion_to_buy.picture,
                    level=potion_to_buy.level,
                    heal=potion_to_buy.heal,
                    cost=potion_to_buy.cost,
                    owner=player
                    )
            player.inventory_slots += 1
            db.session.add(new_potion)
            db.session.commit()
            flash(f"Successfully bought {potion_to_buy.name} for {potion_to_buy.cost} gold", category='success')
            return redirect(url_for('potions'))
        else:
            return redirect(url_for('potions'))
    else:
        return render_template('potion_page.html', player=player, potion_to_buy=potion_to_buy)

@app.route('/use/potion/<int:item_id>')
@login_required
def use_potion(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    potion = Potion.query.get(item_id)

    if potion.name == "HP Potion":
        heal = player.max_hp // 2
        if player.hp + heal > player.max_hp:
            player.hp = player.max_hp
        else:
            player.hp += heal
    elif potion.name == "Expedition Potion":
        if player.expedition_points > 6:
            player.expedition_points = 12
        else:
            player.expedition_points += 6
    elif potion.name == "Exp Potion":
        player.double_exp = 12
    else:

        if player.hp + potion.heal > player.max_hp:
            player.hp = player.max_hp
        else:
            player.hp += potion.heal
        flash(f"Restored {potion.heal} HP", category='info')

    player.inventory_slots -= 1
    db.session.delete(potion)
    db.session.commit()
    

    return redirect(url_for('overview'))


@app.route('/sell/potion/<int:item_id>')
@login_required
def sell_potion(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    potion_to_sell = Potion.query.filter_by(id=item_id).first()
    player.gold += potion_to_sell.cost
    player.inventory_slots -= 1
    db.session.delete(potion_to_sell)
    db.session.commit()
    flash(f"Sold {potion_to_sell.name} for {potion_to_sell.cost} gold", category='success')
    return redirect(url_for('overview'))



@app.route('/sell/weapon/<int:item_id>')
@login_required
def sell_weapon(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    weapon_to_sell = Weapon.query.filter_by(id=item_id).first()
    player.gold += weapon_to_sell.cost
    player.inventory_slots -= 1
    db.session.delete(weapon_to_sell)
    db.session.commit()
    return redirect(url_for('overview'))



@app.route('/sell/armor/<int:item_id>')
@login_required
def sell_armor(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    armor_to_sell = Armor.query.filter_by(id=item_id).first()
    player.gold += armor_to_sell.cost
    player.inventory_slots -= 1
    db.session.delete(armor_to_sell)
    db.session.commit()
    return redirect(url_for('overview'))


@app.route('/sell/shield/<int:item_id>')
@login_required
def sell_shield(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    shield_to_sell = Shield.query.filter_by(id=item_id).first()
    player.gold += shield_to_sell.cost
    player.inventory_slots -= 1
    db.session.delete(shield_to_sell)
    db.session.commit()
    return redirect(url_for('overview'))


@app.route('/sell/helmet/<int:item_id>')
@login_required
def sell_helmet(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    helmet_to_sell = Helmet.query.filter_by(id=item_id).first()
    player.gold += helmet_to_sell.cost
    player.inventory_slots -= 1
    db.session.delete(helmet_to_sell)
    db.session.commit()
    return redirect(url_for('overview'))


@app.route('/sell/boots/<int:item_id>')
@login_required
def sell_boots(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    boots_to_sell = Boots.query.filter_by(id=item_id).first()
    player.gold += boots_to_sell.cost
    player.inventory_slots -= 1
    db.session.delete(boots_to_sell)
    db.session.commit()
    return redirect(url_for('overview'))


@app.route('/equip/weapon/<int:item_id>')
@login_required
def equip_weapon(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]

    weapons = player.weapons
    equipped_weapons = [weapon for weapon in weapons if weapon.is_equipped == True]
    
    if len(equipped_weapons) == 0:
        weapon_to_equip = Weapon.query.filter_by(id=item_id).first()
        weapon_to_equip.is_equipped = True
        player.min_dmg += weapon_to_equip.min_dmg
        player.max_dmg += weapon_to_equip.max_dmg
        if weapon_to_equip.charisma:
            player.charisma += weapon_to_equip.charisma
        player.inventory_slots -= 1
        db.session.commit()
        return redirect(url_for('overview'))

    else:
        equipped_weapon = equipped_weapons[0]
        equipped_weapon.is_equipped = False
        player.min_dmg -= equipped_weapon.min_dmg
        player.max_dmg -= equipped_weapon.max_dmg
        if equipped_weapon.charisma:
            player.charisma -= equipped_weapon.charisma

        weapon_to_equip = Weapon.query.filter_by(id=item_id).first()
        weapon_to_equip.is_equipped = True
        player.min_dmg += weapon_to_equip.min_dmg
        player.max_dmg += weapon_to_equip.max_dmg
        if weapon_to_equip.charisma:
            player.charisma += weapon_to_equip.charisma
        db.session.commit()
        return redirect(url_for('overview'))



@app.route('/equip/armor/<int:item_id>')
@login_required
def equip_armor(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]

    armors = player.armors
    equipped_armors = [armor for armor in armors if armor.is_equipped == True]
    
    if len(equipped_armors) == 0:
        armor_to_equip = Armor.query.filter_by(id=item_id).first()
        armor_to_equip.is_equipped = True
        player.armor += armor_to_equip.armor
        if armor_to_equip.vitality:
            player.vitality += armor_to_equip.vitality
            player.hp += armor_to_equip.vitality * 10
            player.max_hp += armor_to_equip.vitality * 10
        player.inventory_slots -= 1
        db.session.commit()
        return redirect(url_for('overview'))

    else:
        equipped_armor = equipped_armors[0]
        equipped_armor.is_equipped = False
        player.armor -= equipped_armor.armor
        if equipped_armor.vitality:
            player.vitality -= equipped_armor.vitality
            player.hp -= equipped_armor.vitality * 10
            player.max_hp -= equipped_armor.vitality * 10

        armor_to_equip = Armor.query.filter_by(id=item_id).first()
        armor_to_equip.is_equipped = True
        player.armor += armor_to_equip.armor
        if armor_to_equip.vitality:
            player.vitality += armor_to_equip.vitality
            player.hp += armor_to_equip.vitality * 10
            player.max_hp += armor_to_equip.vitality * 10
        db.session.commit()
        return redirect(url_for('overview'))


@app.route('/equip/shield/<int:item_id>')
@login_required
def equip_shield(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]

    shields = player.shields
    equipped_shields = [shield for shield in shields if shield.is_equipped == True]
    
    if len(equipped_shields) == 0:
        shield_to_equip = Shield.query.filter_by(id=item_id).first()
        shield_to_equip.is_equipped = True
        player.armor += shield_to_equip.armor
        if shield_to_equip.charisma:
            player.charisma += shield_to_equip.charisma
        player.inventory_slots -= 1
        db.session.commit()
        return redirect(url_for('overview'))

    else:
        equipped_shield = equipped_shields[0]
        equipped_shield.is_equipped = False
        player.armor -= equipped_shield.armor
        if equipped_shield.charisma:
            player.charisma -= equipped_shield.charisma

        shield_to_equip = Shield.query.filter_by(id=item_id).first()
        shield_to_equip.is_equipped = True
        player.armor += shield_to_equip.armor
        if shield_to_equip.charisma:
            player.charisma += shield_to_equip.charisma
        db.session.commit()
        return redirect(url_for('overview'))


@app.route('/equip/helmet/<int:item_id>')
@login_required
def equip_helmet(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]

    helmets = player.helmets
    equipped_helmets = [helmet for helmet in helmets if helmet.is_equipped == True]
    
    if len(equipped_helmets) == 0:
        helmet_to_equip = Helmet.query.filter_by(id=item_id).first()
        helmet_to_equip.is_equipped = True
        player.armor += helmet_to_equip.armor
        if helmet_to_equip.vitality:
            player.vitality += helmet_to_equip.vitality
            player.hp += helmet_to_equip.vitality * 10
            player.max_hp += helmet_to_equip.vitality * 10
        player.inventory_slots -= 1
        db.session.commit()
        return redirect(url_for('overview'))

    else:
        equipped_helmet = equipped_helmets[0]
        equipped_helmet.is_equipped = False
        player.armor -= equipped_helmet.armor
        if equipped_helmet.vitality:
            player.vitality -= equipped_helmet.vitality
            player.hp -= equipped_helmet.vitality * 10
            player.max_hp -= equipped_helmet.vitality * 10

        helmet_to_equip = Helmet.query.filter_by(id=item_id).first()
        helmet_to_equip.is_equipped = True
        player.armor += helmet_to_equip.armor
        if helmet_to_equip.vitality:
            player.vitality += helmet_to_equip.vitality
            player.hp += helmet_to_equip.vitality * 10
            player.max_hp += helmet_to_equip.vitality * 10
        db.session.commit()
        return redirect(url_for('overview'))


@app.route('/equip/boots/<int:item_id>')
@login_required
def equip_boots(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]

    boots = player.boots
    equipped_boots = [boot for boot in boots if boot.is_equipped == True]
    
    if len(equipped_boots) == 0:
        boots_to_equip = Boots.query.filter_by(id=item_id).first()
        boots_to_equip.is_equipped = True
        player.armor += boots_to_equip.armor
        if boots_to_equip.dexterity:
            player.dexterity += boots_to_equip.dexterity
        player.inventory_slots -= 1
        db.session.commit()
        return redirect(url_for('overview'))

    else:
        equipped_boot = equipped_boots[0]
        equipped_boot.is_equipped = False
        player.armor -= equipped_boot.armor
        if equipped_boot.dexterity:
            player.dexterity -= equipped_boot.dexterity

        boots_to_equip = Boots.query.filter_by(id=item_id).first()
        boots_to_equip.is_equipped = True
        player.armor += boots_to_equip.armor
        if boots_to_equip.dexterity:
            player.dexterity += boots_to_equip.dexterity
        db.session.commit()
        return redirect(url_for('overview'))
        

@app.route('/take_off/weapon/<int:item_id>')
@login_required
def take_off_weapon(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    if player.inventory_slots == 18:
        flash("Your Inventory is full!", category='danger')
        return redirect(url_for('overview'))
    weapon_to_take_off = Weapon.query.filter_by(id=item_id).first()
    weapon_to_take_off.is_equipped = False
    player.min_dmg -= weapon_to_take_off.min_dmg
    player.max_dmg -= weapon_to_take_off.max_dmg
    if weapon_to_take_off.charisma:
        player.charisma -= weapon_to_take_off.charisma
    player.inventory_slots += 1
    db.session.commit()
    return redirect(url_for('overview'))


@app.route('/take_off/armor/<int:item_id>')
@login_required
def take_off_armor(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    if player.inventory_slots == 18:
        flash("Your Inventory is full!", category='danger')
        return redirect(url_for('overview'))
    armor_to_take_off = Armor.query.filter_by(id=item_id).first()
    armor_to_take_off.is_equipped = False
    player.armor -= armor_to_take_off.armor
    if armor_to_take_off.vitality:
        player.vitality -= armor_to_take_off.vitality
        player.hp -= armor_to_take_off.vitality * 10
        player.max_hp -= armor_to_take_off.vitality * 10
    player.inventory_slots += 1
    db.session.commit()
    return redirect(url_for('overview'))


@app.route('/take_off/shield/<int:item_id>')
@login_required
def take_off_shield(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    if player.inventory_slots == 18:
        flash("Your Inventory is full!", category='danger')
        return redirect(url_for('overview'))
    shield_to_take_off = Shield.query.filter_by(id=item_id).first()
    shield_to_take_off.is_equipped = False
    player.armor -= shield_to_take_off.armor
    if shield_to_take_off.charisma:
        player.charisma -= shield_to_take_off.charisma
    player.inventory_slots += 1
    db.session.commit()
    return redirect(url_for('overview'))

@app.route('/take_off/helmet/<int:item_id>')
@login_required
def take_off_helmet(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    if player.inventory_slots == 18:
        flash("Your Inventory is full!", category='danger')
        return redirect(url_for('overview'))
    helmet_to_take_off = Helmet.query.filter_by(id=item_id).first()
    helmet_to_take_off.is_equipped = False
    player.armor -= helmet_to_take_off.armor
    if helmet_to_take_off.vitality:
        player.vitality -= helmet_to_take_off.vitality
        player.hp -= helmet_to_take_off.vitality * 10
        player.max_hp -= helmet_to_take_off.vitality * 10
    player.inventory_slots += 1
    db.session.commit()
    return redirect(url_for('overview'))

@app.route('/take_off/boots/<int:item_id>')
@login_required
def take_off_boots(item_id):
    user = flask_login.current_user
    player = user.gladiator[0]
    if player.inventory_slots == 18:
        flash("Your Inventory is full!", category='danger')
        return redirect(url_for('overview'))
    boots_to_take_off = Boots.query.filter_by(id=item_id).first()
    boots_to_take_off.is_equipped = False
    player.armor -= boots_to_take_off.armor
    if boots_to_take_off.dexterity:
        player.dexterity -= boots_to_take_off.dexterity
    player.inventory_slots += 1
    db.session.commit()
    return redirect(url_for('overview'))

@app.route('/ranking')
def ranking():
    all_gladiators = Player.query.all()
    all_gladiators = sorted(all_gladiators, key=lambda player: player.level)
    all_gladiators = all_gladiators[::-1]
    return render_template('ranking_page.html', all_gladiators=all_gladiators)


@app.route('/ranking/<string:name>')
def ranking_gladiator(name):
    gladiator_to_see = Player.query.filter_by(name=name).first()
    equipped_weapon = [weapon for weapon in gladiator_to_see.weapons if weapon.is_equipped == True]
    equipped_armor = [armor for armor in gladiator_to_see.armors if armor.is_equipped == True]
    equipped_shield = [shield for shield in gladiator_to_see.shields if shield.is_equipped == True]
    equipped_helmet =[helmet for helmet in gladiator_to_see.helmets if helmet.is_equipped == True]
    equipped_boots = [boots for boots in gladiator_to_see.boots if boots.is_equipped == True]
    
    if equipped_weapon:
        equipped_weapon = equipped_weapon[0]
    if equipped_armor:
        equipped_armor = equipped_armor[0]
    if equipped_shield:
        equipped_shield = equipped_shield[0]
    if equipped_helmet:
        equipped_helmet = equipped_helmet[0]
    if equipped_boots:
        equipped_boots = equipped_boots[0]

    return render_template(
        'ranking_gladiator_page.html',
        player=gladiator_to_see,
        equipped_weapon=equipped_weapon,
        equipped_armor=equipped_armor,
        equipped_shield=equipped_shield,
        equipped_helmet=equipped_helmet,
        equipped_boots=equipped_boots
        )

