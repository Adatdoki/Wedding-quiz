"""
Szurkolói token model
"""

from datetime import datetime
from .user import db

class SupporterToken(db.Model):
    """Szurkolói token model - kiesett játékosok tippelési lehetősége"""
    
    __tablename__ = 'supporter_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    
    # Token állapot
    is_active = db.Column(db.Boolean, default=True)
    predicted_number = db.Column(db.Integer, nullable=True)  # Tippelt szám
    predicted_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)  # Tippelt nyerő csapat
    
    # Eredmény
    is_prediction_correct = db.Column(db.Boolean, nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)  # Mikor használta fel
    
    # Időbélyegek
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Kapcsolatok
    player = db.relationship('Player', backref='supporter_tokens')
    game = db.relationship('Game', backref='supporter_tokens')
    predicted_team = db.relationship('Team', backref='predicted_by_supporters')
    
    def __repr__(self):
        return f'<SupporterToken {self.id}: Player {self.player_id} -> Team {self.predicted_team_id}>'
    
    def to_dict(self):
        """Szurkolói token adatok dictionary formában"""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'game_id': self.game_id,
            'round_number': self.round_number,
            'is_active': self.is_active,
            'predicted_number': self.predicted_number,
            'predicted_team_id': self.predicted_team_id,
            'is_prediction_correct': self.is_prediction_correct,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat(),
            'player': self.player.to_dict() if self.player else None,
            'predicted_team': self.predicted_team.to_dict() if self.predicted_team else None
        }

class ModeratorAction(db.Model):
    """Moderátori műveletek naplózása"""
    
    __tablename__ = 'moderator_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # 'pause_round', 'approve_quiz', 'manual_steal', stb.
    action_data = db.Column(db.Text, nullable=True)  # JSON formátumban további adatok
    
    # Időbélyeg
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Kapcsolat
    game = db.relationship('Game', backref='moderator_actions')
    
    def __repr__(self):
        return f'<ModeratorAction {self.id}: {self.action_type}>'
    
    def to_dict(self):
        """Moderátori művelet adatok dictionary formában"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'action_type': self.action_type,
            'action_data': self.action_data,
            'created_at': self.created_at.isoformat()
        }

