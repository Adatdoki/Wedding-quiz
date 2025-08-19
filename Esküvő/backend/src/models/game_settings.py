"""
Játék gyorsítási beállítások
"""

from datetime import datetime
from .user import db

class GameSettings(db.Model):
    """Játék beállítások - moderátor által állítható"""
    
    __tablename__ = 'game_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    
    # Időzítés beállítások
    voting_duration_seconds = db.Column(db.Integer, default=20)  # 20 mp (korábban 30)
    is_sprint_mode = db.Column(db.Boolean, default=False)  # Sprint mód: 15 mp
    
    # Játékgyorsítás beállítások
    protection_enabled = db.Column(db.Boolean, default=True)  # Védettség: visszarablás tiltása
    rescue_round_enabled = db.Column(db.Boolean, default=True)  # Mentőkör: 1 fős csapat védelme
    number_range_max = db.Column(db.Integer, default=20)  # Számmező: 1-20 vagy 1-25
    
    # Időbélyegek
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_voting_duration(self):
        """Aktuális szavazási idő lekérése"""
        if self.is_sprint_mode:
            return 15
        return self.voting_duration_seconds
    
    def get_number_range(self):
        """Aktuális számmező tartomány"""
        return (1, self.number_range_max)
    
    def should_eliminate_single_team(self):
        """1 fős csapat azonnali kiesésének ellenőrzése"""
        return not self.rescue_round_enabled
    
    def can_steal_back_immediately(self):
        """Azonnali visszarablás engedélyezésének ellenőrzése"""
        return not self.protection_enabled
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'voting_duration_seconds': self.voting_duration_seconds,
            'is_sprint_mode': self.is_sprint_mode,
            'protection_enabled': self.protection_enabled,
            'rescue_round_enabled': self.rescue_round_enabled,
            'number_range_max': self.number_range_max,
            'effective_voting_duration': self.get_voting_duration(),
            'number_range': self.get_number_range(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

def get_or_create_game_settings(game_id):
    """Játék beállítások lekérése vagy létrehozása"""
    settings = GameSettings.query.filter_by(game_id=game_id).first()
    if not settings:
        settings = GameSettings(game_id=game_id)
        db.session.add(settings)
        db.session.commit()
    return settings

