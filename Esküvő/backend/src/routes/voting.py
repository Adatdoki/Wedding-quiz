"""
Új szavazási API végpontok - 20 mp nyílt szavazás logika (gyorsított)
"""

from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.game import Game, Team, Player, Round, Vote
from src.models.game_settings import GameSettings, get_or_create_game_settings
from datetime import datetime, timedelta
import json

voting_bp = Blueprint('voting', __name__)

@voting_bp.route('/vote/submit', methods=['POST'])
def submit_vote():
    """Egyéni szavazat leadása vagy módosítása"""
    try:
        data = request.json
        player_id = data.get('player_id')
        number = data.get('number')
        
        if not all([player_id, number]):
            return jsonify({'error': 'Hiányzó adatok'}), 400
        
        # Játékos ellenőrzése
        player = Player.query.get(player_id)
        if not player or not player.is_active:
            return jsonify({'error': 'Játékos nem található vagy inaktív'}), 404
        
        # Aktív játék és beállítások
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        settings = get_or_create_game_settings(game.id)
        min_num, max_num = settings.get_number_range()
        
        if not (min_num <= int(number) <= max_num):
            return jsonify({'error': f'A szám {min_num} és {max_num} között kell legyen'}), 400
        
        current_round = Round.query.filter_by(
            game_id=game.id,
            round_number=game.current_round,
            state='voting'
        ).first()
        
        if not current_round:
            return jsonify({'error': 'Nincs aktív szavazási kör'}), 404
        
        # Szavazási idő ellenőrzése (dinamikus időtartam)
        voting_duration = settings.get_voting_duration()
        elapsed = (datetime.utcnow() - current_round.voting_start_time).total_seconds()
        grace_period = 0.3
        
        if elapsed > (voting_duration + grace_period):
            return jsonify({'error': 'Szavazási idő lejárt'}), 400
        
        # Meglévő szavazat keresése
        existing_vote = Vote.query.filter_by(
            player_id=player_id,
            round_id=current_round.id
        ).first()
        
        if existing_vote:
            existing_vote.number = int(number)
            existing_vote.updated_at = datetime.utcnow()
        else:
            new_vote = Vote(
                player_id=player_id,
                team_id=player.team_id,
                round_id=current_round.id,
                number=int(number)
            )
            db.session.add(new_vote)
        
        db.session.commit()
        
        # Csapat jelenlegi állapotának lekérése
        team_status = get_team_voting_status(player.team_id, current_round.id, settings)
        
        return jsonify({
            'success': True,
            'message': f'Szavazat leadva: {number}',
            'vote': {
                'player_id': player_id,
                'number': int(number),
                'updated_at': datetime.utcnow().isoformat()
            },
            'team_status': team_status,
            'settings': {
                'voting_duration': voting_duration,
                'number_range': settings.get_number_range(),
                'time_remaining': max(0, voting_duration - elapsed)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@voting_bp.route('/vote/team-status/<int:team_id>', methods=['GET'])
def get_team_vote_status(team_id):
    """Csapat szavazási állapotának lekérése"""
    try:
        # Aktív kör keresése
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        current_round = Round.query.filter_by(
            game_id=game.id,
            round_number=game.current_round,
            state='voting'
        ).first()
        
        if not current_round:
            return jsonify({'error': 'Nincs aktív szavazási kör'}), 404
        
        team_status = get_team_voting_status(team_id, current_round.id)
        
        return jsonify({
            'success': True,
            'team_status': team_status,
            'round_info': {
                'round_number': current_round.round_number,
                'is_voting_active': current_round.is_voting_active(),
                'time_remaining': max(0, current_round.voting_duration_seconds - 
                                    (datetime.utcnow() - current_round.voting_start_time).total_seconds())
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voting_bp.route('/vote/round-status', methods=['GET'])
def get_round_voting_status():
    """Teljes kör szavazási állapotának lekérése"""
    try:
        # Aktív kör keresése
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        current_round = Round.query.filter_by(
            game_id=game.id,
            round_number=game.current_round,
            state='voting'
        ).first()
        
        if not current_round:
            return jsonify({'error': 'Nincs aktív szavazási kör'}), 404
        
        # Minden csapat állapota
        all_teams_status = {}
        active_teams = Team.query.filter_by(is_active=True).all()
        
        for team in active_teams:
            all_teams_status[team.id] = get_team_voting_status(team.id, current_round.id)
        
        return jsonify({
            'success': True,
            'round_info': {
                'round_number': current_round.round_number,
                'is_voting_active': current_round.is_voting_active(),
                'time_remaining': max(0, current_round.voting_duration_seconds - 
                                    (datetime.utcnow() - current_round.voting_start_time).total_seconds()),
                'voting_start_time': current_round.voting_start_time.isoformat(),
                'voting_duration_seconds': current_round.voting_duration_seconds
            },
            'teams_status': all_teams_status
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voting_bp.route('/vote/finalize', methods=['POST'])
def finalize_voting():
    """Szavazás lezárása és nyertes meghatározása"""
    try:
        # Aktív kör keresése
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        current_round = Round.query.filter_by(
            game_id=game.id,
            round_number=game.current_round,
            state='voting'
        ).first()
        
        if not current_round:
            return jsonify({'error': 'Nincs aktív szavazási kör'}), 404
        
        # Szavazás lezárása
        current_round.voting_end_time = datetime.utcnow()
        current_round.state = 'calculating'
        
        # Nyertes kiszámítása
        winner_team_id, winning_number, winner_data = current_round.calculate_winner()
        
        if winner_team_id:
            current_round.winner_team_id = winner_team_id
            current_round.state = 'quiz'
            
            # Kvízkérdés kiválasztása
            from src.models.game import QuizQuestion
            quiz_question = QuizQuestion.query.filter_by(is_active=True).first()
            if quiz_question:
                current_round.quiz_question = quiz_question.question
                current_round.quiz_answer = quiz_question.answer
        else:
            # Döntetlen - mindenki iszik
            current_round.state = 'completed'
        
        db.session.commit()
        
        # Eredmény visszaadása
        team_votes = current_round.get_team_final_votes()
        
        return jsonify({
            'success': True,
            'winner_team_id': winner_team_id,
            'winning_number': winning_number,
            'winner_data': winner_data,
            'team_votes': team_votes,
            'is_tie': winner_team_id is None,
            'message': f'Nyertes: {winner_data["team_name"]} ({winning_number})' if winner_team_id else 'Döntetlen - mindenki iszik! 🍻'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_team_voting_status(team_id, round_id):
    """Csapat szavazási állapotának részletes lekérése"""
    team = Team.query.get(team_id)
    if not team:
        return None
    
    # Csapat tagjainak szavazatai
    member_votes = []
    votes_numbers = []
    
    for member in team.members:
        if member.is_active:
            last_vote = Vote.query.filter_by(
                player_id=member.id,
                round_id=round_id
            ).order_by(Vote.updated_at.desc()).first()
            
            if last_vote:
                member_votes.append({
                    'player_id': member.id,
                    'player_name': member.name,
                    'number': last_vote.number,
                    'voted_at': last_vote.updated_at.isoformat()
                })
                votes_numbers.append(last_vote.number)
            else:
                member_votes.append({
                    'player_id': member.id,
                    'player_name': member.name,
                    'number': None,
                    'voted_at': None
                })
    
    # Egyhangúság és legkisebb szám ellenőrzése
    is_unanimous = len(set(votes_numbers)) == 1 if votes_numbers else False
    smallest_number = min(votes_numbers) if votes_numbers else 20
    final_number = votes_numbers[0] if is_unanimous else smallest_number
    
    return {
        'team_id': team_id,
        'team_name': team.name,
        'member_votes': member_votes,
        'is_unanimous': is_unanimous,
        'smallest_number': smallest_number,
        'final_number': final_number,
        'votes_count': len([v for v in member_votes if v['number'] is not None]),
        'total_members': len(member_votes)
    }

