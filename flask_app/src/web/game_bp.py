import logging

from flask import (
    Blueprint, abort, flash, jsonify, redirect,
    render_template, request, session, url_for,
)
from flask import current_app as app

from src.web.forms import MessageForm

logger = logging.getLogger(__name__)
game_bp = Blueprint("game", __name__)


def _require_login():  # type: ignore[no-untyped-def]
    if "user_id" not in session:
        abort(401)


def _game_service():  # type: ignore[no-untyped-def]
    return app.extensions["game_service"]


def _npc_manager():  # type: ignore[no-untyped-def]
    return app.extensions["npc_manager"]


def _world():  # type: ignore[no-untyped-def]
    return app.extensions["world"]


@game_bp.route("/")
def index():  # type: ignore[return]
    _require_login()
    player = session.get("player", {"location": "таверна", "hp": 100, "gold": 50})
    w = _world()
    loc_info = w.get_location_info(player["location"])
    npcs = [n.to_dict() for n in _npc_manager().get_by_location(player["location"])]
    return render_template(
        "game/index.html",
        player=player,
        world=w.get_state(),
        location={"name": player["location"], **loc_info},
        npcs=npcs,
    )


@game_bp.route("/move", methods=["POST"])
def move():
    _require_login()
    dest = request.json.get("location", "") if request.is_json else request.form.get("location", "")  # type: ignore[union-attr]
    w = _world()
    player = session.get("player", {"location": "таверна", "hp": 100, "gold": 50})
    loc = w.get_location_info(player["location"])

    if dest not in loc.get("connected_to", []):
        return jsonify({"ok": False, "error": "Нельзя пройти отсюда туда."})

    player["location"] = dest
    session["player"] = player
    npcs = [n.to_dict() for n in _npc_manager().get_by_location(dest)]
    new_loc = w.get_location_info(dest)
    return jsonify({"ok": True, "location": {"name": dest, **new_loc}, "npcs": npcs})


@game_bp.route("/dialogue/<npc_id>", methods=["GET", "POST"])
def dialogue(npc_id: str):
    _require_login()
    npc = _npc_manager().get(npc_id)
    if npc is None:
        abort(404)

    form = MessageForm()
    reply: dict[str, object] | None = None

    if form.validate_on_submit():
        player = session.get("player", {"location": "таверна", "hp": 100, "gold": 50})
        w = _world()

        npc_data: dict[str, object] = {
            "npc_id":               npc.id,
            "npc_name":             npc.name,
            "npc_role":             npc.role,
            "npc_personality":      npc.personality,
            "npc_state":            npc.state.value,
            "npc_long_term_memory": npc.long_term_memory,
            "conversation_history": npc.memory,        
        }
        player_context: dict[str, object] = {
            "game_hour":   w.hour,
            "player_name": session["username"],
            "player_hp":   int(player["hp"]),
            "player_gold": int(player["gold"]),
        }
        reply = _game_service().talk_to_npc(
            user_id=session["user_id"],
            npc_data=npc_data,
            player_context=player_context,
            player_message=form.message.data,
        )
        npc.add_to_memory("user",      form.message.data)
        npc.add_to_memory("assistant", str(reply.get("dialogue", "")))

    return render_template("game/dialogue.html", npc=npc.to_dict(), form=form, reply=reply)

@game_bp.route("/history")
def history():
    _require_login()
    records = _game_service().get_history(session["user_id"])
    return render_template("game/history.html", records=records)


@game_bp.route("/tick", methods=["POST"])
def tick():
    _require_login()
    w = _world()
    w.advance_time(1)
    _npc_manager().tick_all(w.hour)
    return jsonify(w.get_state())