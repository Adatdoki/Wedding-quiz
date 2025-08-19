from flask import Blueprint, jsonify, request
from src.models.game import Player, Team, Game, Round, Vote, QuizQuestion, db
import random
import uuid
from collections import Counter

game_bp = Blueprint('game', __name__)

# Vicces esküvői becenevek
WEDDING_NICKNAMES = [
    'Nászmester', 'Koszorúslány', 'Vőfély', 'Menyasszonytáncoltató', 'Anyós-álom',
    'Torta-őrző', 'Pezsgő-nyitó', 'Rizs-szóró', 'Csokor-fogó', 'Gyűrű-hordó',
    'Tánc-király', 'Ital-kóstoló', 'Fotó-bombázó', 'Köszöntő-mester', 'Parti-állat',
    'Menyasszonyi-ruha-őr', 'Vőlegény-segéd', 'Esküvői-DJ', 'Torta-kóstoló', 'Virágszóró'
]

# Vicces csapatnevek
TEAM_NAMES = [
    'Tüllkommandó', 'Csokornyakkendő-maffia', 'Lakodalmas Lámák', 'A Gyűrűk Urai',
    'Váltságdíj a Menyasszonyért', 'Pezsgőpukkantók', 'Torta-kommandó', 'Az Igen Bajnokai',
    'Csokor-dobó Brigád', 'Rizsszórás Mesterei', 'A Házasság Huszárjai', 'Parti-piramisok',
    'Esküvői Elit', 'Menyasszonyi Maffia', 'Vőlegény Vikingek', 'Lakodalmas Legendák'
]

@game_bp.route('/register', methods=['POST'])
def register_player():
    """Játékos regisztráció"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'error': 'A név megadása kötelező'}), 400
        
        # Egyedi session ID generálása
        session_id = str(uuid.uuid4())
        
        # Véletlenszerű becenév választása
        used_nicknames = [p.nickname for p in Player.query.filter_by(is_active=True).all()]
        available_nicknames = [n for n in WEDDING_NICKNAMES if n not in used_nicknames]
        
        if not available_nicknames:
            # Ha elfogytak a becenevek, újra használjuk őket
            available_nicknames = WEDDING_NICKNAMES
        
        nickname = random.choice(available_nicknames)
        
        # Aktív játék keresése vagy létrehozása
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            game = Game(name="Esküvői Kvíz", state="registration")
            db.session.add(game)
            db.session.commit()
        
        # Játékos létrehozása
        player = Player(
            name=name,
            nickname=nickname,
            session_id=session_id
        )
        
        db.session.add(player)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'player': player.to_dict(),
            'game': game.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/players', methods=['GET'])
def get_players():
    """Aktív játékosok listája"""
    try:
        players = Player.query.filter_by(is_active=True).all()
        return jsonify({
            'players': [player.to_dict() for player in players]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_bp.route('/pair', methods=['POST'])
def create_pair():
    """Pár létrehozása"""
    try:
        data = request.json
        player1_id = data.get('player1_id')
        player2_id = data.get('player2_id')
        
        if not player1_id or not player2_id:
            return jsonify({'error': 'Mindkét játékos ID szükséges'}), 400
        
        if player1_id == player2_id:
            return jsonify({'error': 'Egy játékos nem párosíthatja magát'}), 400
        
        # Játékosok lekérése
        player1 = Player.query.get(player1_id)
        player2 = Player.query.get(player2_id)
        
        if not player1 or not player2:
            return jsonify({'error': 'Játékos nem található'}), 404
        
        if player1.team_id or player2.team_id:
            return jsonify({'error': 'Az egyik játékos már csapatban van'}), 400
        
        # Aktív játék lekérése
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Csapatnév választása
        used_team_names = [t.name for t in Team.query.filter_by(game_id=game.id, is_active=True).all()]
        available_team_names = [n for n in TEAM_NAMES if n not in used_team_names]
        
        if not available_team_names:
            available_team_names = TEAM_NAMES
        
        team_name = random.choice(available_team_names)
        
        # Csapat létrehozása
        team = Team(
            name=team_name,
            game_id=game.id
        )
        
        db.session.add(team)
        db.session.commit()
        
        # Játékosok hozzáadása a csapathoz
        player1.team_id = team.id
        player2.team_id = team.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'team': team.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/game/state', methods=['GET'])
def get_game_state():
    """Játék állapotának lekérése"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        return jsonify({
            'game': game.to_dict()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_bp.route('/game/start-pairing', methods=['POST'])
def start_pairing():
    """Párválasztás fázis indítása"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        game.state = "pairing"
        db.session.commit()
        
        return jsonify({
            'success': True,
            'game': game.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/game/start-playing', methods=['POST'])
def start_playing():
    """Játék fázis indítása"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Ellenőrizzük, hogy van-e legalább egy csapat
        active_teams = Team.query.filter_by(game_id=game.id, is_active=True).all()
        if len(active_teams) < 1:
            return jsonify({'error': 'Legalább egy csapat szükséges a játék indításához'}), 400
        
        game.state = "playing"
        game.current_round = 1
        
        # Első kör létrehozása
        round1 = Round(
            game_id=game.id,
            round_number=1,
            state="voting"
        )
        
        db.session.add(round1)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'game': game.to_dict(),
            'round': round1.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/vote', methods=['POST'])
def submit_vote():
    """Szavazat leadása"""
    try:
        data = request.json
        team_id = data.get('team_id')
        number = data.get('number')
        
        if not team_id or not number:
            return jsonify({'error': 'Csapat ID és szám megadása kötelező'}), 400
        
        if not isinstance(number, int) or number <= 0:
            return jsonify({'error': 'A számnak pozitív egész számnak kell lennie'}), 400
        
        # Csapat ellenőrzése
        team = Team.query.get(team_id)
        if not team or not team.is_active:
            return jsonify({'error': 'Csapat nem található'}), 404
        
        # Aktív kör lekérése
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        current_round = Round.query.filter_by(
            game_id=game.id,
            round_number=game.current_round,
            state="voting"
        ).first()
        
        if not current_round:
            return jsonify({'error': 'Nincs aktív szavazási kör'}), 404
        
        # Ellenőrizzük, hogy a csapat már szavazott-e
        existing_vote = Vote.query.filter_by(
            team_id=team_id,
            round_id=current_round.id
        ).first()
        
        if existing_vote:
            return jsonify({'error': 'Ez a csapat már leadta a szavazatát'}), 400
        
        # Szavazat létrehozása
        vote = Vote(
            team_id=team_id,
            round_id=current_round.id,
            number=number
        )
        
        db.session.add(vote)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'vote': vote.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/round/evaluate', methods=['POST'])
def evaluate_round():
    """Kör kiértékelése"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        current_round = Round.query.filter_by(
            game_id=game.id,
            round_number=game.current_round,
            state="voting"
        ).first()
        
        if not current_round:
            return jsonify({'error': 'Nincs aktív szavazási kör'}), 404
        
        # Szavazatok lekérése
        votes = Vote.query.filter_by(round_id=current_round.id).all()
        
        if not votes:
            return jsonify({'error': 'Nincsenek szavazatok'}), 400
        
        # Számok számlálása
        vote_counts = Counter([vote.number for vote in votes])
        
        # Legkisebb egyedi szám keresése
        winner_team_id = None
        winning_number = None
        
        # Rendezzük a számokat növekvő sorrendben
        sorted_numbers = sorted(vote_counts.keys())
        
        for number in sorted_numbers:
            if vote_counts[number] == 1:  # Egyedi szám
                # Megkeressük a csapatot, aki ezt a számot választotta
                winning_vote = Vote.query.filter_by(
                    round_id=current_round.id,
                    number=number
                ).first()
                
                if winning_vote:
                    winner_team_id = winning_vote.team_id
                    winning_number = number
                    break
        
        # Kör állapotának frissítése
        if winner_team_id:
            current_round.winner_team_id = winner_team_id
            current_round.state = "quiz"
        else:
            # Döntetlen - mindenki iszik
            current_round.state = "completed"
        
        db.session.commit()
        
        result = {
            'success': True,
            'round': current_round.to_dict(),
            'winner_team_id': winner_team_id,
            'winning_number': winning_number,
            'vote_counts': dict(vote_counts),
            'is_tie': winner_team_id is None
        }
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/quiz/question', methods=['GET'])
def get_quiz_question():
    """Kvízkérdés lekérése"""
    try:
        # Véletlenszerű kérdés választása
        questions = QuizQuestion.query.filter_by(is_active=True).all()
        
        if not questions:
            # Ha nincsenek kérdések az adatbázisban, alapértelmezett kérdéseket használunk
            default_questions = [
                "Hol volt az első randijuk?",
                "Ki mondta ki először: 'Szeretlek'?",
                "Mi a pár közös kedvenc sorozata?",
                "Hány gyereket terveznek?",
                "Melyikük a rendetlenebb otthon?"
            ]
            question_text = random.choice(default_questions)
        else:
            question = random.choice(questions)
            question_text = question.question
        
        return jsonify({
            'question': question_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_bp.route('/quiz/answer', methods=['POST'])
def submit_quiz_answer():
    """Kvíz válasz leadása"""
    try:
        data = request.json
        team_id = data.get('team_id')
        answer = data.get('answer', '').strip()
        is_correct = data.get('is_correct', False)  # Manuálisan adjuk meg, hogy helyes-e
        
        if not team_id:
            return jsonify({'error': 'Csapat ID megadása kötelező'}), 400
        
        # Aktív kör lekérése
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        current_round = Round.query.filter_by(
            game_id=game.id,
            round_number=game.current_round,
            state="quiz"
        ).first()
        
        if not current_round or current_round.winner_team_id != team_id:
            return jsonify({'error': 'Ez a csapat nem válaszolhat a kvízre'}), 400
        
        # Válasz mentése
        current_round.quiz_answer = answer
        current_round.quiz_correct = is_correct
        
        if is_correct:
            current_round.state = "completed"
            # Itt történne a csapattag rablás logika
        else:
            current_round.state = "completed"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'round': current_round.to_dict(),
            'can_steal': is_correct
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/steal-player', methods=['POST'])
def steal_player():
    """Játékos elrablása másik csapattól"""
    try:
        data = request.json
        stealing_team_id = data.get('stealing_team_id')
        target_player_id = data.get('target_player_id')
        
        if not stealing_team_id or not target_player_id:
            return jsonify({'error': 'Csapat ID és célpont játékos ID megadása kötelező'}), 400
        
        # Csapatok és játékos ellenőrzése
        stealing_team = Team.query.get(stealing_team_id)
        target_player = Player.query.get(target_player_id)
        
        if not stealing_team or not target_player:
            return jsonify({'error': 'Csapat vagy játékos nem található'}), 404
        
        if target_player.team_id == stealing_team_id:
            return jsonify({'error': 'Nem rabolhatod el a saját csapattagodat'}), 400
        
        old_team_id = target_player.team_id
        
        # Játékos áthelyezése
        target_player.team_id = stealing_team_id
        
        # Ha a régi csapat 1 főre csökkent, kiesik
        if old_team_id:
            old_team = Team.query.get(old_team_id)
            remaining_players = Player.query.filter_by(team_id=old_team_id, is_active=True).count()
            
            if remaining_players <= 1:
                old_team.is_active = False
                # Az utolsó játékos is kiesik
                for player in old_team.players:
                    if player.is_active:
                        player.is_active = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{target_player.name} átkerült a {stealing_team.name} csapatba!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# Moderátor funkciók
@game_bp.route('/moderator/start-round', methods=['POST'])
def start_round():
    """Új kör indítása (moderátor funkció)"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Kör számának növelése
        game.current_round += 1
        game.state = 'playing'
        game.is_paused = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{game.current_round}. kör elkezdődött!',
            'round': game.current_round
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/moderator/pause-game', methods=['POST'])
def pause_game():
    """Játék szüneteltetése (moderátor funkció)"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        game.is_paused = not game.is_paused
        db.session.commit()
        
        status = 'szüneteltetve' if game.is_paused else 'folytatva'
        
        return jsonify({
            'success': True,
            'message': f'Játék {status}!',
            'is_paused': game.is_paused
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/moderator/drink-break', methods=['POST'])
def drink_break():
    """Ital szünet bejelentése (moderátor funkció)"""
    try:
        data = request.json
        message = data.get('message', 'Ital szünet! 🍻')
        
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Moderátor akció rögzítése
        from src.models.supporter import ModeratorAction
        action = ModeratorAction(
            game_id=game.id,
            action_type='drink_break',
            description=message
        )
        db.session.add(action)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'action': 'drink_break'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/moderator/manual-team-change', methods=['POST'])
def manual_team_change():
    """Manuális csapatváltás (moderátor funkció)"""
    try:
        data = request.json
        player_id = data.get('player_id')
        target_team_id = data.get('target_team_id')
        
        if not player_id or not target_team_id:
            return jsonify({'error': 'Játékos és célcsapat megadása kötelező'}), 400
        
        player = Player.query.get(player_id)
        target_team = Team.query.get(target_team_id)
        
        if not player or not target_team:
            return jsonify({'error': 'Játékos vagy csapat nem található'}), 404
        
        old_team_id = player.team_id
        player.team_id = target_team_id
        
        # Csapat tagszámok frissítése
        if old_team_id:
            old_team = Team.query.get(old_team_id)
            if old_team:
                old_team.member_count -= 1
                # Ha a csapat üres lett, inaktiváljuk
                if old_team.member_count <= 0:
                    old_team.is_active = False
        
        target_team.member_count += 1
        
        # Moderátor akció rögzítése
        from src.models.supporter import ModeratorAction
        action = ModeratorAction(
            game_id=target_team.game_id,
            action_type='manual_team_change',
            description=f'{player.name} áthelyezve {target_team.name} csapatba'
        )
        db.session.add(action)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{player.name} sikeresen áthelyezve!',
            'player': {
                'id': player.id,
                'name': player.name,
                'team_id': player.team_id
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/moderator/reset-game', methods=['POST'])
def reset_game():
    """Játék újraindítása (moderátor funkció)"""
    try:
        # Összes aktív játék inaktiválása
        games = Game.query.filter_by(is_active=True).all()
        for game in games:
            game.is_active = False
        
        # Összes játékos inaktiválása
        players = Player.query.filter_by(is_active=True).all()
        for player in players:
            player.is_active = False
        
        # Összes csapat inaktiválása
        teams = Team.query.filter_by(is_active=True).all()
        for team in teams:
            team.is_active = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Játék sikeresen újraindítva!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/moderator/stats', methods=['GET'])
def get_game_stats():
    """Játék statisztikák lekérése (moderátor funkció)"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Statisztikák összegyűjtése
        total_players = Player.query.filter_by(is_active=True).count()
        active_teams = Team.query.filter_by(is_active=True).count()
        
        # Szurkolói tokenek
        from src.models.supporter import SupporterToken
        active_tokens = SupporterToken.query.filter(SupporterToken.used_at.is_(None)).count()
        
        # Moderátor akciók
        from src.models.supporter import ModeratorAction
        recent_actions = ModeratorAction.query.filter_by(game_id=game.id)\
            .order_by(ModeratorAction.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_players': total_players,
                'active_teams': active_teams,
                'current_round': game.current_round,
                'game_state': game.state,
                'is_paused': game.is_paused,
                'active_tokens': active_tokens
            },
            'recent_actions': [{
                'type': action.action_type,
                'description': action.description,
                'created_at': action.created_at.isoformat()
            } for action in recent_actions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Csapat balansz és ital szünet funkciók
@game_bp.route('/balance/check', methods=['GET'])
def check_team_balance():
    """Csapat egyensúly ellenőrzése"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        needs_balance = game.balance_teams()
        snowball_risk = game.prevent_snowball_effect()
        smallest_team = game.get_smallest_team()
        
        active_teams = [team for team in game.teams if team.is_active and team.member_count > 0]
        team_sizes = [team.member_count for team in active_teams]
        
        return jsonify({
            'success': True,
            'needs_balance': needs_balance,
            'snowball_risk': snowball_risk,
            'smallest_team': smallest_team.to_dict() if smallest_team else None,
            'team_count': len(active_teams),
            'team_sizes': team_sizes,
            'size_difference': max(team_sizes) - min(team_sizes) if team_sizes else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_bp.route('/balance/auto-balance', methods=['POST'])
def auto_balance_teams():
    """Automatikus csapat kiegyensúlyozás"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        active_teams = [team for team in game.teams if team.is_active and team.member_count > 0]
        
        if len(active_teams) < 2:
            return jsonify({'error': 'Nincs elég aktív csapat a kiegyensúlyozáshoz'}), 400
        
        # Csapatok rendezése tagszám szerint
        active_teams.sort(key=lambda team: team.member_count)
        smallest_team = active_teams[0]
        largest_team = active_teams[-1]
        
        moves_made = 0
        max_moves = 3  # Maximális áthelyezések száma
        
        while (largest_team.member_count - smallest_team.member_count > 1 and 
               moves_made < max_moves):
            
            # Egy játékos áthelyezése a legnagyobb csapatból a legkisebbbe
            players_to_move = [p for p in Player.query.filter_by(team_id=largest_team.id, is_active=True).all()]
            
            if not players_to_move:
                break
            
            player_to_move = random.choice(players_to_move)
            
            # Áthelyezés
            player_to_move.team_id = smallest_team.id
            largest_team.member_count -= 1
            smallest_team.member_count += 1
            
            moves_made += 1
            
            # Frissítés a következő iterációhoz
            active_teams.sort(key=lambda team: team.member_count)
            smallest_team = active_teams[0]
            largest_team = active_teams[-1]
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'moves_made': moves_made,
            'message': f'{moves_made} játékos áthelyezve a kiegyensúlyozáshoz',
            'teams': [team.to_dict() for team in active_teams]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/drink/coordinate', methods=['POST'])
def coordinate_drink_break():
    """Ital szünet koordinálása - csapatok értesítése"""
    try:
        data = request.json
        message = data.get('message', 'Ital szünet! 🍻')
        duration_seconds = data.get('duration', 60)  # Alapértelmezett: 1 perc
        
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Játék szüneteltetése
        game.is_paused = True
        
        # Moderátor akció rögzítése
        from src.models.supporter import ModeratorAction
        action = ModeratorAction(
            game_id=game.id,
            action_type='drink_break',
            description=f'{message} (időtartam: {duration_seconds}s)'
        )
        db.session.add(action)
        
        db.session.commit()
        
        # Aktív csapatok és játékosok száma
        active_teams = [team for team in game.teams if team.is_active]
        total_players = sum(team.member_count for team in active_teams)
        
        return jsonify({
            'success': True,
            'message': message,
            'duration_seconds': duration_seconds,
            'teams_notified': len(active_teams),
            'players_notified': total_players,
            'game_paused': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/drink/resume', methods=['POST'])
def resume_after_drink():
    """Játék folytatása ital szünet után"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        # Játék folytatása
        game.is_paused = False
        
        # Moderátor akció rögzítése
        from src.models.supporter import ModeratorAction
        action = ModeratorAction(
            game_id=game.id,
            action_type='resume_game',
            description='Játék folytatva ital szünet után'
        )
        db.session.add(action)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Játék folytatva! Következő kör kezdődhet.',
            'game_paused': False
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_bp.route('/teams/smallest', methods=['GET'])
def get_smallest_team():
    """Legkisebb csapat lekérése"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        smallest_team = game.get_smallest_team()
        
        if not smallest_team:
            return jsonify({'error': 'Nincs elérhető csapat'}), 404
        
        return jsonify({
            'success': True,
            'smallest_team': smallest_team.to_dict(),
            'member_count': smallest_team.member_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

