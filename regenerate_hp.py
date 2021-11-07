import time
from app import db, login_manager
from app.models import Player, User, UserMixin
from flask_login import current_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# regenerate 1% HP every 30secs
def regenerate_hp():
    user = current_user
    print(user)
    '''
    if player.hp < player.max_hp:
        time.sleep(2)
        player.hp += player.max_hp//100
        if player.hp > player.max_hp:
            player.hp = player.max_hp

        db.session.commit()
        print(player.hp)
    '''
if __name__ == "__main__":
    
        regenerate_hp()