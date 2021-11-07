import time
import flask_login

from flask_migrate import current
from app import db, routes
from app.models import Player, User, load_user
from flask_login import login_required

# regenerate 1 expedition point every 5mins
@login_required
def regenerate_expedtion_points():
    user = flask_login.current_user
    player = user.gladiator[0]
    if player.expedition_points < 12:
        time.sleep(300)
        player.expedition_points += 1

        db.session.commit()
        print(player.expedition_points)

while True:
    regenerate_expedtion_points()