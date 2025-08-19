"""
Szurkolói token API végpontok
"""

from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.game import Game, Team, Player, Round
from src.models.supporter import SupporterToken, ModeratorAction
import uuid
import json

supporter_bp = Blueprint('supporter', __name__)

@supporter_bp.route('/supporter/tokens', methods=['GET'])
def get_supporter_tokens():
    """Aktív szurkolói tokenek lekérése"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        tokens = SupporterToken.query.filter_by(
            game_id=game.id,
            is_active=True
        ).all()
        
        return jsonify({
            'tokens': [token.to_dict() for token in tokens],
            'game': game.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@supporter_bp.route('/supporter/predict', methods=['POST'])
def submit_prediction():
    """Szurkolói tipp leadása"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        predicted_number = data.get('predicted_number')
        predicted_team_id = data.get('predicted_team_id')
        
        if not all([player_id, predicted_number, predicted_team_id]):
            return jsonify({'error': 'Hiányzó adatok'}), 400
        
        # Aktív játék ellenőrzése
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Játékos ellenőrzése
        player = Player.query.get(player_id)
        if not player:
            return jsonify({'error': 'Játékos nem található'}), 404
        
        # Csapat ellenőrzése
        team = Team.query.get(predicted_team_id)
        if not team or not team.is_active:
            return jsonify({'error': 'Érvénytelen csapat'}), 400
        
        # Aktív token keresése
        token = SupporterToken.query.filter_by(
            player_id=player_id,
            game_id=game.id,
            round_number=game.current_round,
            is_active=True
        ).first()
        
        if not token:
            return jsonify({'error': 'Nincs aktív szurkolói token'}), 404
        
        # Tipp frissítése
        token.predicted_number = int(predicted_number)
        token.predicted_team_id = predicted_team_id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'token': token.to_dict(),
            'message': f'Tipp leadva: {predicted_number} számra, {team.name} csapat nyerésére'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@supporter_bp.route('/supporter/evaluate', methods=['POST'])
def evaluate_predictions():
    """Szurkolói tippek kiértékelése kör után"""
    try:
        data = request.get_json()
        winning_team_id = data.get('winning_team_id')
        winning_number = data.get('winning_number')
        
        if not all([winning_team_id, winning_number]):
            return jsonify({'error': 'Hiányzó adatok'}), 400
        
        # Aktív játék ellenőrzése
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Aktuális kör tokenjeinek kiértékelése
        tokens = SupporterToken.query.filter_by(
            game_id=game.id,
            round_number=game.current_round,
            is_active=True
        ).all()
        
        correct_predictions = []
        
        for token in tokens:
            if (token.predicted_team_id == winning_team_id and 
                token.predicted_number == winning_number):
                
                token.is_prediction_correct = True
                token.used_at = db.datetime.utcnow()
                correct_predictions.append(token)
            else:
                token.is_prediction_correct = False
            
            token.is_active = False  # Token felhasználva
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'correct_predictions': len(correct_predictions),
            'total_predictions': len(tokens),
            'winners': [token.to_dict() for token in correct_predictions]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@supporter_bp.route('/supporter/rejoin', methods=['POST'])
def rejoin_game():
    """Szurkolói token felhasználása - visszatérés a játékba"""
    try:
        data = request.get_json()
        token_id = data.get('token_id')
        
        if not token_id:
            return jsonify({'error': 'Token ID hiányzik'}), 400
        
        # Token ellenőrzése
        token = SupporterToken.query.get(token_id)
        if not token:
            return jsonify({'error': 'Token nem található'}), 404
        
        if not token.is_prediction_correct:
            return jsonify({'error': 'Helytelen tipp, nem használható fel'}), 400
        
        if token.used_at:
            return jsonify({'error': 'Token már felhasználva'}), 400
        
        # Játék és játékos ellenőrzése
        game = Game.query.get(token.game_id)
        player = Player.query.get(token.player_id)
        
        if not game or not game.is_active:
            return jsonify({'error': 'Játék nem aktív'}), 404
        
        if not player:
            return jsonify({'error': 'Játékos nem található'}), 404
        
        # Legkisebb csapat megkeresése
        smallest_team = game.get_smallest_team()
        if not smallest_team:
            return jsonify({'error': 'Nincs elérhető csapat'}), 404
        
        # Játékos hozzáadása a legkisebb csapathoz
        old_team_id = player.team_id
        player.team_id = smallest_team.id
        player.is_active = True
        
        # Csapat tagszámok frissítése
        smallest_team.member_count += 1
        
        # Ha a játékos korábban másik csapatban volt, csökkentjük annak tagszámát
        if old_team_id and old_team_id != smallest_team.id:
            old_team = Team.query.get(old_team_id)
            if old_team:
                old_team.member_count = max(0, old_team.member_count - 1)
                if old_team.member_count <= 0:
                    old_team.is_active = False
        
        # Token felhasználás jelölése
        token.used_at = db.datetime.utcnow()
        
        # Moderátor akció rögzítése
        action = ModeratorAction(
            game_id=game.id,
            action_type='supporter_rejoin',
            description=f'{player.name} visszatért a {smallest_team.name} csapatba szurkolói tokennel'
        )
        db.session.add(action)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{player.name} ({player.nickname}) visszatért a {smallest_team.name} csapatba!',
            'player': player.to_dict(),
            'team': smallest_team.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@supporter_bp.route('/moderator/secret', methods=['POST'])
def generate_moderator_secret():
    """Moderátor titkos kód generálása"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Titkos kód generálása
        secret = str(uuid.uuid4())[:8].upper()
        game.moderator_secret = secret
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'secret': secret,
            'message': 'Moderátor kód generálva'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@supporter_bp.route('/moderator/verify', methods=['POST'])
def verify_moderator():
    """Moderátor kód ellenőrzése"""
    try:
        data = request.get_json()
        secret = data.get('secret')
        
        if not secret:
            return jsonify({'error': 'Titkos kód hiányzik'}), 400
        
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        if game.moderator_secret != secret:
            return jsonify({'error': 'Érvénytelen moderátor kód'}), 403
        
        return jsonify({
            'success': True,
            'message': 'Moderátor hozzáférés engedélyezve',
            'game': game.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@supporter_bp.route('/moderator/pause', methods=['POST'])
def toggle_game_pause():
    """Játék szüneteltetése/folytatása"""
    try:
        data = request.get_json()
        secret = data.get('secret')
        
        # Moderátor ellenőrzés
        game = Game.query.filter_by(is_active=True).first()
        if not game or game.moderator_secret != secret:
            return jsonify({'error': 'Nincs moderátor jogosultság'}), 403
        
        # Szünet állapot váltása
        game.is_paused = not game.is_paused
        
        # Moderátori művelet naplózása
        action = ModeratorAction(
            game_id=game.id,
            action_type='pause_game' if game.is_paused else 'resume_game',
            action_data=json.dumps({'paused': game.is_paused})
        )
        db.session.add(action)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_paused': game.is_paused,
            'message': 'Játék szüneteltetve' if game.is_paused else 'Játék folytatva'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@supporter_bp.route('/moderator/authenticate', methods=['POST'])
def authenticate_moderator():
    """Moderátor autentikáció titkos kóddal"""
    try:
        data = request.json
        secret_code = data.get('secret_code', '').strip()
        
        if not secret_code:
            return jsonify({'error': 'Titkos kód megadása kötelező'}), 400
        
        # Egyszerű titkos kód ellenőrzése (éles környezetben komplexebb legyen)
        if secret_code == 'MODERATOR2025':
            return jsonify({
                'success': True,
                'message': 'Moderátor hozzáférés engedélyezve',
                'role': 'moderator'
            })
        else:
            return jsonify({'error': 'Hibás titkos kód'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

