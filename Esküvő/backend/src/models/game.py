from src.models.user import db
from datetime import datetime
import json

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Player {self.name} ({self.nickname})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nickname': self.nickname,
            'session_id': self.session_id,
            'team_id': self.team_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Kapcsolatok
    players = db.relationship('Player', backref='team', lazy=True)
    votes = db.relationship('Vote', backref='team', lazy=True)

    def __repr__(self):
        return f'<Team {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'game_id': self.game_id,
            'score': self.score,
            'is_active': self.is_active,
            'member_count': len(self.players),
            'members': [player.to_dict() for player in self.players if player.is_active],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="Esküvői Kvíz")
    state = db.Column(db.String(20), nullable=False, default="registration")  # registration, pairing, playing, quiz, finished
    current_round = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Moderátor beállítások
    is_paused = db.Column(db.Boolean, default=False)
    moderator_secret = db.Column(db.String(100), nullable=True)  # Rejtett moderátor kód
    
    # Kapcsolatok
    teams = db.relationship('Team', backref='game', lazy=True)
    rounds = db.relationship('Round', backref='game', lazy=True)

    def __repr__(self):
        return f'<Game {self.name} - {self.state}>'
    
    def get_smallest_team(self):
        """Legkisebb létszámú aktív csapat visszaadása"""
        active_teams = [team for team in self.teams if team.is_active and len(team.players) > 0]
        if not active_teams:
            return None
        return min(active_teams, key=lambda t: len([p for p in t.players if p.is_active]))
    
    def get_eliminated_players(self):
        """Kiesett játékosok listája (akiknek nincs aktív csapatuk)"""
        from .supporter import SupporterToken
        all_players = Player.query.filter_by(is_active=True).all()
        eliminated = []
        
        for player in all_players:
            # Ha nincs csapata vagy a csapata inaktív
            if not player.team or not player.team.is_active:
                # Ellenőrizzük, hogy van-e már aktív token-je
                existing_token = SupporterToken.query.filter_by(
                    player_id=player.id,
                    game_id=self.id,
                    round_number=self.current_round,
                    is_active=True
                ).first()
                
                if not existing_token:
                    eliminated.append(player)
        
        return eliminated
    
    def create_supporter_tokens(self):
        """Szurkolói tokenek létrehozása kiesett játékosoknak"""
        from .supporter import SupporterToken
        eliminated_players = self.get_eliminated_players()
        tokens_created = 0
        
        for player in eliminated_players:
            token = SupporterToken(
                player_id=player.id,
                game_id=self.id,
                round_number=self.current_round
            )
            db.session.add(token)
            tokens_created += 1
        
        if tokens_created > 0:
            db.session.commit()
        
        return tokens_created

    def get_smallest_team(self):
        """Legkisebb aktív csapat megkeresése"""
        active_teams = [team for team in self.teams if team.is_active and team.member_count > 0]
        
        if not active_teams:
            return None
        
        # Legkisebb tagszámú csapat keresése
        smallest_team = min(active_teams, key=lambda team: team.member_count)
        return smallest_team
    
    def balance_teams(self):
        """Csapatok kiegyensúlyozása - nagy különbségek csökkentése"""
        active_teams = [team for team in self.teams if team.is_active and team.member_count > 0]
        
        if len(active_teams) < 2:
            return False
        
        # Csapatok rendezése tagszám szerint
        active_teams.sort(key=lambda team: team.member_count)
        smallest_team = active_teams[0]
        largest_team = active_teams[-1]
        
        # Ha a különbség túl nagy (több mint 2 fő), balansz szükséges
        if largest_team.member_count - smallest_team.member_count > 2:
            return True
        
        return False
    
    def prevent_snowball_effect(self):
        """Snowball effect megelőzése - túl erős csapatok korlátozása"""
        active_teams = [team for team in self.teams if team.is_active and team.member_count > 0]
        
        if not active_teams:
            return False
        
        total_players = sum(team.member_count for team in active_teams)
        average_team_size = total_players / len(active_teams)
        
        # Ha van csapat, amely 50%-kal nagyobb az átlagnál
        for team in active_teams:
            if team.member_count > average_team_size * 1.5:
                return True
        
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'current_round': self.current_round,
            'is_active': self.is_active,
            'is_paused': self.is_paused,
            'team_count': len([team for team in self.teams if team.is_active]),
            'teams': [team.to_dict() for team in self.teams if team.is_active],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(20), nullable=False, default="voting")  # voting, quiz, completed
    winner_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    quiz_question = db.Column(db.Text, nullable=True)
    quiz_answer = db.Column(db.String(500), nullable=True)
    quiz_correct = db.Column(db.Boolean, nullable=True)
    
    # Új szavazási logika mezők
    voting_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    voting_end_time = db.Column(db.DateTime, nullable=True)
    voting_duration_seconds = db.Column(db.Integer, default=30)  # 30 másodperc
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Kapcsolatok
    votes = db.relationship('Vote', backref='round', lazy=True)
    winner_team = db.relationship('Team', foreign_keys=[winner_team_id])
    
    def get_team_final_votes(self):
        """Minden csapat végső szavazatait adja vissza (csapattagok utolsó szavazata alapján)"""
        team_votes = {}
        
        # Minden csapat aktív tagjai
        game = Game.query.get(self.game_id)
        active_teams = [team for team in game.teams if team.is_active]
        
        for team in active_teams:
            team_member_votes = []
            
            # Csapat minden aktív tagjának utolsó szavazata
            for member in team.members:
                if member.is_active:
                    last_vote = Vote.query.filter_by(
                        player_id=member.id,
                        round_id=self.id
                    ).order_by(Vote.updated_at.desc()).first()
                    
                    if last_vote:
                        team_member_votes.append(last_vote.number)
                    else:
                        # Ha nem szavazott, fallback = 20
                        team_member_votes.append(20)
            
            if team_member_votes:
                # Egyhangúság ellenőrzése
                if len(set(team_member_votes)) == 1:
                    # Egyhangú szavazat
                    team_votes[team.id] = {
                        'final_number': team_member_votes[0],
                        'is_unanimous': True,
                        'member_votes': team_member_votes,
                        'team_name': team.name
                    }
                else:
                    # Nem egyhangú -> legkisebb szám
                    team_votes[team.id] = {
                        'final_number': min(team_member_votes),
                        'is_unanimous': False,
                        'member_votes': team_member_votes,
                        'team_name': team.name
                    }
            else:
                # Nincs aktív tag -> fallback
                team_votes[team.id] = {
                    'final_number': 20,
                    'is_unanimous': False,
                    'member_votes': [],
                    'team_name': team.name
                }
        
        return team_votes
    
    def calculate_winner(self):
        """Nyertes csapat kiszámítása az új logika szerint"""
        team_votes = self.get_team_final_votes()
        
        if not team_votes:
            return None
        
        # Legkisebb egyedi szám keresése
        all_numbers = [vote_data['final_number'] for vote_data in team_votes.values()]
        number_counts = {}
        
        for number in all_numbers:
            number_counts[number] = number_counts.get(number, 0) + 1
        
        # Egyedi számok (csak egy csapat szavazott rá)
        unique_numbers = [num for num, count in number_counts.items() if count == 1]
        
        if unique_numbers:
            winning_number = min(unique_numbers)
            # Nyertes csapat keresése
            for team_id, vote_data in team_votes.items():
                if vote_data['final_number'] == winning_number:
                    return team_id, winning_number, vote_data
        
        return None, None, None
    
    def is_voting_active(self):
        """Szavazás még aktív-e (30 mp + grace period)"""
        if not self.voting_start_time:
            return False
        
        elapsed = datetime.utcnow() - self.voting_start_time
        grace_period = 0.3  # 300ms grace period
        
        return elapsed.total_seconds() <= (self.voting_duration_seconds + grace_period)

    def to_dict(self):
        team_votes = self.get_team_final_votes()
        
        return {
            'id': self.id,
            'game_id': self.game_id,
            'round_number': self.round_number,
            'state': self.state,
            'winner_team_id': self.winner_team_id,
            'quiz_question': self.quiz_question,
            'quiz_answer': self.quiz_answer,
            'quiz_correct': self.quiz_correct,
            'voting_start_time': self.voting_start_time.isoformat() if self.voting_start_time else None,
            'voting_end_time': self.voting_end_time.isoformat() if self.voting_end_time else None,
            'voting_duration_seconds': self.voting_duration_seconds,
            'is_voting_active': self.is_voting_active(),
            'team_votes': team_votes,
            'votes': [vote.to_dict() for vote in self.votes],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)  # Új: egyéni szavazatok
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Új: utolsó módosítás
    
    # Kapcsolatok
    player = db.relationship('Player', backref='votes')

    def __repr__(self):
        return f'<Vote {self.number} - Player {self.player_id} - Team {self.team_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'player_id': self.player_id,
            'round_id': self.round_id,
            'number': self.number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'player_name': self.player.name if self.player else None
        }

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), default="general")
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<QuizQuestion {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'is_active': self.is_active
        }

