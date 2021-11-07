
from flask import flash
from flask.helpers import url_for
from werkzeug.utils import redirect
from app import db
import random


def get_player_dmg(player):
    dmg = player.attack
    max_dmg = player.attack + 3
    return random.randint(dmg, max_dmg)

def get_enemy_dmg(enemy):
    dmg = enemy.attack
    max_dmg = enemy.attack + 3
    return random.randint(dmg, max_dmg)


def get_reward(enemy):
    easy = random.randint(1,2)
    medium = random.randint(2,3)
    hard = random.randint(3,4)
    very_hard = random.randint(4,6)
    easy_gold = random.randint(50,100)
    medium_gold = random.randint(200,300)
    hard_gold = random.randint(350,500)
    very_hard_gold = random.randint(550,1000)

    if enemy.level < 3:
        return (easy, easy_gold)
    elif 3 <= enemy.level < 6:
        return (medium, medium_gold)
    elif 6 <= enemy.level <= 10:
        return (hard, hard_gold)
    else:
        return (very_hard, very_hard_gold)




def fight_enemy(player, enemy):

    enemy_max_hp = enemy.hp
    result = []

    if player.hp <= 0:
        pass
    else:
        while player.hp > 0 and enemy.hp > 0:
            player_dmg = get_player_dmg(player)
            enemy.hp -= player_dmg
            result.append(f'{player.name} deals {player_dmg} damage...{enemy.name} left HP: {enemy.hp}')
            enemy_dmg = get_enemy_dmg(enemy)
            player.hp -= enemy_dmg
            result.append(f'{enemy.name} deals {enemy_dmg} damage...{player.name} left HP: {player.hp}')

            if enemy.hp <= 0:
                exp, gold = get_reward(enemy)
                player.gold += gold
                player.experience += exp
                result.append(f'You earned {exp} points of experience and {gold}')
                result.append('You won!')
            elif player.hp <= 0:
                player.hp = 0
                db.session.commit()
                result.append('No reward for this fight...')
                result.append(f"{enemy.name} has won...")
        
        enemy.hp = enemy_max_hp
        db.session.commit()
        return result
    