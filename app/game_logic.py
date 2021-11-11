
from flask import flash
from flask.helpers import url_for
from werkzeug.utils import redirect
from app import db
import random


def get_player_dmg(player):
    min_dmg = player.min_dmg
    max_dmg = player.max_dmg
    return random.randint(min_dmg, max_dmg)

def get_enemy_dmg(enemy, player):

    damage_reduction = player.armor // 10

    min_dmg = enemy.min_dmg - damage_reduction
    max_dmg = enemy.max_dmg - damage_reduction

    if min_dmg < 1:
        min_dmg = 1
    if max_dmg < 1:
        max_dmg = 1

    return random.randint(min_dmg, max_dmg)


def player_dodge_hit(player, enemy):
    if enemy.dexterity >= player.dexterity:
        chance = 10
    else:
        chance = 10 + (player.dexterity - enemy.dexterity)

    if chance > 70:
        chance = 70
    return random.randint(1,100) <= chance


def enemy_dodge_hit(player, enemy):
    if player.dexterity >= enemy.dexterity:
        chance = 10
    else:
        chance = 10 + (enemy.dexterity - player.dexterity)

    if chance > 70:
        chance = 70
    return random.randint(1,100) <= chance

def player_deal_critical(player):
    return random.randint(1, 120) <= player.charisma





def get_reward(enemy, player):
    easy = random.randint(1,2)
    medium = random.randint(2,3)
    hard = random.randint(3,4)
    very_hard = random.randint(4,6)
    easy_gold = random.randint(50,100)
    medium_gold = random.randint(200,300)
    hard_gold = random.randint(350,500)
    very_hard_gold = random.randint(550,1000)

    if player.double_exp > 0:
        if enemy.level < 3:
            return (2*easy, easy_gold)
        elif 3 <= enemy.level < 6:
            return (2*medium, medium_gold)
        elif 6 <= enemy.level <= 10:
            return (2*hard, hard_gold)
        else:
            return (2*very_hard, very_hard_gold)
    else:
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
            if enemy_dodge_hit(player, enemy):
                result.append(f"Missed! {player.name} deals no damage")
            elif player_deal_critical(player):
                critical_dmg = get_player_dmg(player) * 2
                enemy.hp -= critical_dmg
                result.append(f'CRITICAL! {player.name} deals {critical_dmg} damage...{enemy.name} left HP: {enemy.hp}')
            else:
                player_dmg = get_player_dmg(player)
                enemy.hp -= player_dmg
                result.append(f'{player.name} deals {player_dmg} damage...{enemy.name} left HP: {enemy.hp}')

            if player_dodge_hit(player, enemy):
                result.append(f"Missed! {enemy.name} deals no damage")
            else:
                enemy_dmg = get_enemy_dmg(enemy, player)
                player.hp -= enemy_dmg
                result.append(f'{enemy.name} deals {enemy_dmg} damage...{player.name} left HP: {player.hp}')

            if enemy.hp <= 0:
                exp, gold = get_reward(enemy, player)
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
    