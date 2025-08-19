"""
Játék beállítások API végpontok - moderátor által állítható
"""

from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.game import Game
from src.models.game_settings import GameSettings, get_or_create_game_settings

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings/get', methods=['GET'])
def get_game_settings():
    """Aktuális játék beállítások lekérése"""
    try:
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        settings = get_or_create_game_settings(game.id)
        
        return jsonify({
            'success': True,
            'settings': settings.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/update', methods=['POST'])
def update_game_settings():
    """Játék beállítások frissítése (moderátor)"""
    try:
        data = request.json
        
        # Moderátor autentikáció ellenőrzése
        secret_code = data.get('secret_code')
        if secret_code != 'MODERATOR2025':
            return jsonify({'error': 'Hibás moderátor kód'}), 403
        
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        settings = get_or_create_game_settings(game.id)
        
        # Beállítások frissítése
        if 'voting_duration_seconds' in data:
            duration = int(data['voting_duration_seconds'])
            if 10 <= duration <= 60:  # 10-60 mp között
                settings.voting_duration_seconds = duration
        
        if 'is_sprint_mode' in data:
            settings.is_sprint_mode = bool(data['is_sprint_mode'])
        
        if 'protection_enabled' in data:
            settings.protection_enabled = bool(data['protection_enabled'])
        
        if 'rescue_round_enabled' in data:
            settings.rescue_round_enabled = bool(data['rescue_round_enabled'])
        
        if 'number_range_max' in data:
            max_num = int(data['number_range_max'])
            if 15 <= max_num <= 50:  # 1-15 és 1-50 között
                settings.number_range_max = max_num
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Beállítások frissítve',
            'settings': settings.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/settings/presets', methods=['GET'])
def get_preset_configurations():
    """Előre beállított konfigurációk lekérése"""
    presets = {
        'normal': {
            'name': 'Normál Játék',
            'description': '20 mp szavazás, védettség be, mentőkör be, 1-20 számok',
            'voting_duration_seconds': 20,
            'is_sprint_mode': False,
            'protection_enabled': True,
            'rescue_round_enabled': True,
            'number_range_max': 20
        },
        'sprint': {
            'name': 'Sprint Mód',
            'description': '15 mp szavazás, védettség ki, mentőkör ki, 1-25 számok',
            'voting_duration_seconds': 20,
            'is_sprint_mode': True,  # 15 mp
            'protection_enabled': False,
            'rescue_round_enabled': False,
            'number_range_max': 25
        },
        'fast': {
            'name': 'Gyors Játék',
            'description': '20 mp szavazás, védettség ki, mentőkör be, 1-25 számok',
            'voting_duration_seconds': 20,
            'is_sprint_mode': False,
            'protection_enabled': False,
            'rescue_round_enabled': True,
            'number_range_max': 25
        },
        'casual': {
            'name': 'Lassú Játék',
            'description': '25 mp szavazás, védettség be, mentőkör be, 1-20 számok',
            'voting_duration_seconds': 25,
            'is_sprint_mode': False,
            'protection_enabled': True,
            'rescue_round_enabled': True,
            'number_range_max': 20
        }
    }
    
    return jsonify({
        'success': True,
        'presets': presets
    })

@settings_bp.route('/settings/apply-preset', methods=['POST'])
def apply_preset_configuration():
    """Előre beállított konfiguráció alkalmazása"""
    try:
        data = request.json
        
        # Moderátor autentikáció
        secret_code = data.get('secret_code')
        if secret_code != 'MODERATOR2025':
            return jsonify({'error': 'Hibás moderátor kód'}), 403
        
        preset_name = data.get('preset_name')
        if not preset_name:
            return jsonify({'error': 'Preset név hiányzik'}), 400
        
        # Preset konfigurációk
        presets = {
            'normal': {
                'voting_duration_seconds': 20,
                'is_sprint_mode': False,
                'protection_enabled': True,
                'rescue_round_enabled': True,
                'number_range_max': 20
            },
            'sprint': {
                'voting_duration_seconds': 20,
                'is_sprint_mode': True,
                'protection_enabled': False,
                'rescue_round_enabled': False,
                'number_range_max': 25
            },
            'fast': {
                'voting_duration_seconds': 20,
                'is_sprint_mode': False,
                'protection_enabled': False,
                'rescue_round_enabled': True,
                'number_range_max': 25
            },
            'casual': {
                'voting_duration_seconds': 25,
                'is_sprint_mode': False,
                'protection_enabled': True,
                'rescue_round_enabled': True,
                'number_range_max': 20
            }
        }
        
        if preset_name not in presets:
            return jsonify({'error': 'Ismeretlen preset'}), 400
        
        game = Game.query.filter_by(is_active=True).first()
        if not game:
            return jsonify({'error': 'Nincs aktív játék'}), 404
        
        settings = get_or_create_game_settings(game.id)
        preset_config = presets[preset_name]
        
        # Preset alkalmazása
        for key, value in preset_config.items():
            setattr(settings, key, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{preset_name.title()} preset alkalmazva',
            'settings': settings.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

