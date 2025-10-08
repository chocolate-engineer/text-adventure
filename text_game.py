"""
================================================================================
TEXT ADVENTURE RPG GAME - COMPLETE 10 FLOOR EDITION
================================================================================
Version: 6.0.0
Author: DEKU
Python: 3.13+
"""

import random
import json
import os
import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from difflib import get_close_matches
from dataclasses import dataclass, field

# Configure comprehensive logging (file only, no console output)
logging.basicConfig(
    filename='game.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(funcName)s:%(lineno)d - %(message)s',
    filemode='a'
)
logger = logging.getLogger(__name__)

#################################################################################
# GAME CONSTANTS & CONFIGURATION
#################################################################################
class GameConstants:
    """Central configuration class containing all game constants"""
    VERSION = "6.5.0"
    SAVE_FILE = "savegame.json"
    
    # Floor configuration
    NUM_FLOORS = 10
    MIN_ROOMS_PER_FLOOR = 10
    MAX_ROOMS_PER_FLOOR = 15
    
    # Class definitions with enhanced inventory
    CLASSES = {
        'warrior': {
            'base_health': 120, 'base_mana': 50,
            'base_stats': {'strength': 15, 'intelligence': 8, 'agility': 10},
            'health_per_level': 15, 'inventory_slots': 10,
            'weapon_types': ['melee'],
            'stat_growth': {'strength': 3, 'intelligence': 1, 'agility': 1}
        },
        'mage': {
            'base_health': 80, 'base_mana': 150,
            'base_stats': {'strength': 8, 'intelligence': 15, 'agility': 10},
            'health_per_level': 8, 'inventory_slots': 8,
            'weapon_types': ['magic'],
            'stat_growth': {'strength': 1, 'intelligence': 3, 'agility': 1}
        },
        'rogue': {
            'base_health': 100, 'base_mana': 75,
            'base_stats': {'strength': 10, 'intelligence': 10, 'agility': 15},
            'health_per_level': 12, 'inventory_slots': 12,
            'weapon_types': ['stealth'],
            'stat_growth': {'strength': 1, 'intelligence': 1, 'agility': 3}
        }
    }
    
    CLASS_NAMES = {
        1: {'warrior': 'Warrior', 'mage': 'Mage', 'rogue': 'Rogue'},
        2: {'warrior': 'Berserker', 'mage': 'Sorcerer', 'rogue': 'Assassin'},
        3: {'warrior': 'Paladin', 'mage': 'Archmage', 'rogue': 'Shadow Master'}
    }
    
    CLASS_UPGRADE_LEVELS = [5, 10, 15]
    RARITY_BOOST_PER_TIER = 0.05
    
    # Weapon rarity system
    WEAPON_RARITIES = {
        'common': {'multiplier': 1.0, 'color': 'WHITE'},
        'uncommon': {'multiplier': 1.3, 'color': 'GREEN'},
        'rare': {'multiplier': 1.6, 'color': 'BLUE'},
        'epic': {'multiplier': 2.0, 'color': 'PURPLE'},
        'legendary': {'multiplier': 2.5, 'color': 'GOLD'},
        'mythic': {'multiplier': 3.0, 'color': 'RED'},
        'divine': {'multiplier': 999.0, 'color': 'STAR'}
    }
    
    RARITY_ORDER = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic', 'divine']
    BETTER_WEAPON_RARITY_BOOST = 0.15  # 15% boost for better rarity
    
    WEAPON_TYPES = {
        'melee': ['Sword', 'Axe', 'Hammer', 'Spear', 'Blade', 'Greatsword', 'Mace'],
        'magic': ['Staff', 'Wand', 'Orb', 'Tome', 'Crystal', 'Scepter'],
        'stealth': ['Dagger', 'Bow', 'Claws', 'Shiv', 'Needle', 'Rapier']
    }
    
    WEAPON_MATERIALS = {
        'common': ['Iron', 'Steel', 'Bronze', 'Copper', 'Stone'],
        'uncommon': ['Silver', 'Enchanted', 'Sharp', 'Sturdy', 'Fine'],
        'rare': ['Mithril', 'Elven', 'Dwarven', 'Mystic', 'Ancient'],
        'epic': ['Dragon', 'Phoenix', 'Ethereal', 'Celestial', 'Infernal'],
        'legendary': ['Godforged', 'Divine', 'Eternal', 'Primordial', 'Void'],
        'mythic': ['Cosmos', 'Reality', 'Infinity', 'Quantum', 'Supreme']
    }
    
    GOLDEN_GUN_NAMES = [
        "Excalibur's Vengeance", "Dragonslayer Supreme", "Godkiller Mk.VII",
        "The Infinity Decimator", "Cosmos Ender", "Reality Ripper"
    ]
    GOLDEN_GUN_DROP_RATE = 0.0002
    
    # Complete enemy roster (20+ types)
    ENEMIES = {
        'sewer rat': {'health': 15, 'damage': 5, 'exp': 15, 'desc': 'A disease-ridden rat with glowing red eyes'},
        'goblin': {'health': 25, 'damage': 8, 'exp': 25, 'desc': 'A small, green-skinned creature wielding a crude club'},
        'skeleton': {'health': 30, 'damage': 10, 'exp': 30, 'desc': 'Animated bones held together by dark magic'},
        'prison guard': {'health': 40, 'damage': 12, 'exp': 35, 'desc': 'A corrupted guard in tattered armor'},
        'armored skeleton': {'health': 45, 'damage': 14, 'exp': 45, 'desc': 'A skeleton warrior clad in ancient armor'},
        'shadow wraith': {'health': 50, 'damage': 18, 'exp': 55, 'desc': 'A spectral being that feeds on fear'},
        'corrupted mage': {'health': 40, 'damage': 20, 'exp': 60, 'desc': 'A once-noble mage consumed by forbidden magic'},
        'ghoul': {'health': 55, 'damage': 16, 'exp': 50, 'desc': 'A flesh-eating undead creature'},
        'fire elemental': {'health': 60, 'damage': 22, 'exp': 70, 'desc': 'A being of pure flame and rage'},
        'ice elemental': {'health': 58, 'damage': 20, 'exp': 68, 'desc': 'A crystalline creature radiating freezing cold'},
        'lightning wisp': {'health': 50, 'damage': 25, 'exp': 75, 'desc': 'Crackling energy given form'},
        'stone golem': {'health': 80, 'damage': 18, 'exp': 65, 'desc': 'A massive construct of animated stone'},
        'lesser demon': {'health': 70, 'damage': 26, 'exp': 85, 'desc': 'A horned creature from the abyss'},
        'dark cultist': {'health': 65, 'damage': 24, 'exp': 80, 'desc': 'A fanatic devoted to dark powers'},
        'shadow beast': {'health': 75, 'damage': 28, 'exp': 90, 'desc': 'A monstrous predator born of darkness'},
        'void spawn': {'health': 80, 'damage': 30, 'exp': 95, 'desc': 'An aberration from beyond reality'},
        'ancient guardian': {'health': 90, 'damage': 32, 'exp': 110, 'desc': 'An eternal sentinel of forgotten secrets'},
        'cosmic horror': {'health': 85, 'damage': 35, 'exp': 120, 'desc': 'An incomprehensible being from the void'},
        'titan spawn': {'health': 100, 'damage': 30, 'exp': 105, 'desc': 'Offspring of the primordial titans'},
        'celestial knight': {'health': 95, 'damage': 34, 'exp': 115, 'desc': 'A fallen warrior of the heavens'},
        'treasure guardian': {'health': 60, 'damage': 20, 'exp': 65, 'desc': 'A magical construct protecting valuable treasure'}
    }
    
    FLOOR_THEMES = {
        1: ['sewer rat', 'goblin', 'skeleton', 'prison guard'],
        2: ['goblin', 'skeleton', 'prison guard', 'armored skeleton'],
        3: ['armored skeleton', 'shadow wraith', 'corrupted mage', 'ghoul'],
        4: ['shadow wraith', 'corrupted mage', 'ghoul', 'armored skeleton'],
        5: ['fire elemental', 'ice elemental', 'lightning wisp', 'stone golem'],
        6: ['fire elemental', 'ice elemental', 'stone golem', 'lightning wisp'],
        7: ['lesser demon', 'dark cultist', 'shadow beast', 'void spawn'],
        8: ['lesser demon', 'dark cultist', 'shadow beast', 'void spawn'],
        9: ['ancient guardian', 'cosmic horror', 'titan spawn', 'celestial knight'],
        10: ['ancient guardian', 'cosmic horror', 'titan spawn', 'celestial knight']
    }
    
    # Item definitions
    HEALING_ITEMS = {
        'health potion': {'heal': 30, 'type': 'health'},
        'ultimate health potion': {'heal': 'full', 'type': 'health'},
        'magic scroll': {'heal': 25, 'type': 'mana'},
        'ice crystal': {'heal': 50, 'type': 'mana'},
        'energy drink': {'heal': 20, 'type': 'health'},
        'vitality tonic': {'heal': 35, 'type': 'health'},
        'elixir of life': {'heal': 50, 'type': 'health'}
    }
    
    EXPERIENCE_ITEMS = {
        'experience gem': {'amount': 50},
        'victory scroll': {'amount': 75},
        'wisdom gem': {'amount': 100},
        'frozen artifact': {'amount': 100},
        'soul crystal': {'amount': 150}
    }
    
    WEARABLE_ITEMS = {
        'armor piece': {'stat': 'strength', 'bonus': 5},
        'cursed amulet': {'stat': 'intelligence', 'bonus': 3},
        "nature's blessing": {'stat': 'agility', 'bonus': 4},
        'healing herb': {'stat': 'agility', 'bonus': 2},
        'mana flower': {'stat': 'intelligence', 'bonus': 4},
        'power ring': {'stat': 'strength', 'bonus': 4},
        'warrior charm': {'stat': 'strength', 'bonus': 3},
        'swift boots': {'stat': 'agility', 'bonus': 5},
        'leather bracer': {'stat': 'agility', 'bonus': 3},
        'arcane pendant': {'stat': 'intelligence', 'bonus': 6},
        'titan gauntlet': {'stat': 'strength', 'bonus': 7},
        'shadow cloak': {'stat': 'agility', 'bonus': 6}
    }
    
    ACTIONABLE_ITEMS = {
        'rusty key': 'key',
        'bone key': 'key',
        'torch': 'light',
        'old map': 'map',
        'ancient medallion': 'offering'
    }
    
    QUEST_ITEMS = ['rusty key', 'old map', 'legendary artifact', 'bone key', 
                   'ancient medallion', 'crystal shard', 'demon seal', 'void essence', 'primordial rune']
    
    SHOP_ITEMS = {
        'health potion': 5, 'magic scroll': 8, 'energy drink': 6,
        'experience gem': 15, 'armor piece': 20, 'power ring': 25,
        'swift boots': 25, 'elixir of life': 30, 'soul crystal': 40
    }
    
    # Drop rates
    WEAPON_DROP_CHANCE = 0.4
    ITEM_DROP_BASE_CHANCE = 0.35
    GOLD_DROP_CHANCE = 0.6
    GOLD_DROP_MIN = 2
    GOLD_DROP_MAX = 10
    
    # Progression
    BASE_EXPERIENCE_NEEDED = 100
    EXPERIENCE_MULTIPLIER = 1.4
    MANA_PER_LEVEL = 10
    INVENTORY_SLOTS_PER_LEVEL = 1
    INVENTORY_SLOTS_PER_TIER = 3
    
    # Combat
    BOSS_DEFEND_REDUCTION = 2
    BOSS_SPECIAL_TURN_FREQUENCY = 3
    BOSS_SPECIAL_HEALTH_THRESHOLD = 0.5
    MIN_ENEMY_DAMAGE = 1
    MIN_BOSS_DAMAGE = 5
    MAGIC_MANA_COST = 15
    MAGIC_DAMAGE_RANGE = (10, 25)

#################################################################################
# DATA-DRIVEN ROOM TEMPLATES
#################################################################################
@dataclass
class RoomTemplate:
    """Data class for room templates"""
    name: str
    description: str
    atmosphere: str
    items: List[str] = field(default_factory=list)
    enemy_count: int = 2
    special_type: Optional[str] = None

class RoomTemplateConfig:
    """Configuration for themed room templates"""
    
    THEME_CONFIG = {
        'dungeon': {
            'floors': (1, 2),
            'enemies': ['sewer rat', 'goblin', 'skeleton', 'prison guard'],
            'templates': [
                RoomTemplate("Damp Prison Cell", "Rusted bars line the walls of this forgotten cell. Water drips from cracked stone.",
                           "The air is thick with the stench of decay and despair.", ['rusty key', 'health potion']),
                RoomTemplate("Guard Barracks", "Overturned bunks and scattered weapons suggest a hasty retreat.",
                           "Bloodstains on the floor tell a grim tale.", ['weapon cache', 'armor piece']),
                RoomTemplate("Torture Chamber", "Chains hang from the ceiling. Ancient implements of pain line the walls.",
                           "Echoes of past suffering seem to whisper in the darkness.", ['cursed amulet', 'bone key']),
                RoomTemplate("Sewage Tunnel", "Putrid water flows through channels in the floor.",
                           "The stench is overwhelming. Rats scurry in the shadows.", ['energy drink', 'torch'])
            ]
        },
        'crypt': {
            'floors': (3, 4),
            'enemies': ['armored skeleton', 'shadow wraith', 'corrupted mage', 'ghoul'],
            'templates': [
                RoomTemplate("Ancient Crypt", "Stone sarcophagi line the walls, their lids cracked and displaced.",
                           "An unnatural chill fills the air as the dead stir restlessly.", ['soul crystal', 'weapon cache']),
                RoomTemplate("Necromancer's Study", "Forbidden tomes and ritual circles cover every surface.",
                           "Dark energy crackles around ancient spell books.", ['magic scroll', 'arcane pendant']),
                RoomTemplate("Burial Chamber", "Rows of burial niches stretch into the darkness.",
                           "The dead do not rest peacefully here.", ['health potion', 'wisdom gem']),
                RoomTemplate("Ossuary", "Bones are stacked floor to ceiling in intricate patterns.",
                           "The bones seem to shift and rearrange when you're not looking.", ['bone key', 'cursed amulet'])
            ]
        },
        'elemental': {
            'floors': (5, 6),
            'enemies': ['fire elemental', 'ice elemental', 'lightning wisp', 'stone golem'],
            'templates': [
                RoomTemplate("Inferno Chamber", "Waves of heat emanate from pools of bubbling lava.",
                           "The very air shimmers with intense heat.", ['weapon cache', 'elixir of life']),
                RoomTemplate("Frozen Cavern", "Icicles the size of spears hang from the ceiling.",
                           "Your breath freezes instantly in the frigid air.", ['ice crystal', 'frozen artifact']),
                RoomTemplate("Storm Hall", "Lightning arcs between metal pillars in this charged chamber.",
                           "Static electricity makes your hair stand on end.", ['magic scroll', 'power ring']),
                RoomTemplate("Elemental Nexus", "All four elements clash in chaotic harmony here.",
                           "Fire, ice, lightning, and stone war for dominance.", ['weapon cache', 'titan gauntlet'])
            ]
        },
        'dark_magic': {
            'floors': (7, 8),
            'enemies': ['lesser demon', 'dark cultist', 'shadow beast', 'void spawn'],
            'templates': [
                RoomTemplate("Ritual Chamber", "Blasphemous symbols cover every inch of floor and wall.",
                           "Reality seems to warp and twist at the edges of your vision.", ['demon seal', 'weapon cache']),
                RoomTemplate("Shadow Realm Gate", "A portal to darkness pulses with malevolent energy.",
                           "Whispers from beyond beckon you closer.", ['shadow cloak', 'soul crystal']),
                RoomTemplate("Corrupted Sanctum", "What was once a holy place now serves darker powers.",
                           "Desecrated altars radiate profane energy.", ['weapon cache', 'ultimate health potion']),
                RoomTemplate("Abyssal Pit", "A bottomless chasm yawns before you, bridged by bone.",
                           "Screams echo up from unfathomable depths.", ['demon seal', 'arcane pendant'])
            ]
        },
        'cosmic': {
            'floors': (9, 10),
            'enemies': ['ancient guardian', 'cosmic horror', 'titan spawn', 'celestial knight'],
            'templates': [
                RoomTemplate("Primordial Vault", "Ancient stone predating civilization stretches endlessly upward.",
                           "The weight of eons presses down upon you.", ['primordial rune', 'titan gauntlet']),
                RoomTemplate("Cosmic Observatory", "Stars that shouldn't exist shine through impossible windows.",
                           "Your mind struggles to comprehend the geometry of this place.", ['weapon cache', 'wisdom gem']),
                RoomTemplate("Hall of Eternity", "Time flows strangely in this ageless corridor.",
                           "Past, present, and future seem to overlap here.", ['soul crystal', 'legendary artifact']),
                RoomTemplate("Reality Fracture", "The laws of physics break down in this impossible space.",
                           "You see things that cannot be and yet are.", ['void essence', 'ultimate health potion'])
            ]
        }
    }
    
    SPECIAL_ROOMS = [
        RoomTemplate("Long Hallway", "A long corridor stretches before you, lit by flickering torches.",
                   "Shadows dance menacingly on the walls.", ['torch', 'weapon cache']),
        RoomTemplate("Treasure Room", "Glittering wealth fills this chamber, but it's well guarded.",
                   "Gold and gems reflect torchlight in dazzling patterns.", 
                   ['golden coin', 'weapon cache', 'experience gem'], 2, 'treasure'),
        RoomTemplate("Hidden Alcove", "A dark alcove with a single torch sconce on the wall.",
                   "The sconce looks like it could hold a torch. Something feels hidden here.",
                   ['torch'], 1, 'secret'),
        RoomTemplate("Sacred Shrine", "An ancient shrine with a stone altar in the center.",
                   "The altar has a circular indentation. Strange energy emanates from it.",
                   ['health potion', 'golden coin'], 1, 'altar'),
        RoomTemplate("Locked Vault", "A sealed vault with an ornate chest at its center.",
                   "The chest has an old rusty keyhole. It hasn't been opened in centuries.",
                   ['weapon cache', 'golden coin'], 2, 'vault')
    ]
    
    @classmethod
    def get_templates_for_floor(cls, floor: int) -> List[RoomTemplate]:
        """Get room templates for specified floor"""
        templates = []
        for theme_name, config in cls.THEME_CONFIG.items():
            if config['floors'][0] <= floor <= config['floors'][1]:
                templates.extend(config['templates'])
                break
        templates.extend(cls.SPECIAL_ROOMS)
        return templates
    
    @classmethod
    def get_enemies_for_floor(cls, floor: int) -> List[str]:
        """Get enemy pool for floor"""
        return GameConstants.FLOOR_THEMES.get(floor, ['goblin'])

#################################################################################
# BOSS CONFIGURATION GENERATOR
#################################################################################
class BossConfig:
    """Generate boss configurations dynamically"""
    
    BOSS_DATA = {
        1: {'name': 'Arena Champion', 'special': "CHAMPION'S FURY", 
            'weapons': {'warrior': ('Gladius of Victory', 32), 'mage': ("Champion's Scepter", 28), 'rogue': ('Twin Blades of Honor', 30)}},
        2: {'name': 'Necromancer Lord', 'special': 'DEATH CURSE',
            'weapons': {'warrior': ('Soul Reaper', 35), 'mage': ('Death Staff', 32), 'rogue': ('Shadow Fang', 33)}},
        3: {'name': 'Crypt Overlord', 'special': 'SOUL DRAIN',
            'weapons': {'warrior': ('Bone Crusher', 38), 'mage': ('Crypt Scepter', 35), 'rogue': ('Grave Shiv', 36)}},
        4: {'name': 'Shadow King', 'special': 'SHADOW STRIKE',
            'weapons': {'warrior': ('Shadowbane', 41), 'mage': ('Dark Orb', 38), 'rogue': ('Night Piercer', 39)}},
        5: {'name': 'Flame Lord', 'special': 'INFERNO',
            'weapons': {'warrior': ('Flamebringer', 44), 'mage': ('Inferno Staff', 41), 'rogue': ('Cinder Bow', 42)}},
        6: {'name': 'Frost Titan', 'special': 'GLACIAL STORM',
            'weapons': {'warrior': ('Frostbane Greatsword', 47), 'mage': ('Staff of Eternal Winter', 44), 'rogue': ('Icicle Piercer', 45)}},
        7: {'name': 'Demon Prince', 'special': 'HELLFIRE',
            'weapons': {'warrior': ("Demon's Edge", 50), 'mage': ('Abyssal Staff', 47), 'rogue': ('Soul Piercer', 48)}},
        8: {'name': 'Void Archon', 'special': 'VOID RIFT',
            'weapons': {'warrior': ('Voidreaver', 53), 'mage': ('Reality Staff', 50), 'rogue': ('Oblivion Blade', 51)}},
        9: {'name': 'Primordial Beast', 'special': 'ANCIENT WRATH',
            'weapons': {'warrior': ('Titan Slayer', 56), 'mage': ('Primordial Staff', 53), 'rogue': ('Beast Fang', 54)}},
        10: {'name': 'Reality Breaker', 'special': 'COSMIC ANNIHILATION',
             'weapons': {'warrior': ('Worldender', 60), 'mage': ('Cosmos Staff', 57), 'rogue': ('Reality Ripper', 58)}}
    }
    
    BOSS_ROOMS = {
        1: ("Gladiator Arena", "A massive circular arena with sand-covered floors.", 
            "Ghostly cheers echo from unseen crowds. The Arena Champion awaits!"),
        2: ("Necromancer's Sanctum", "Dark energy swirls around an obsidian throne.",
            "Death itself seems to bow before the Necromancer Lord!"),
        3: ("Tomb of the Overlord", "A vast crypt dominated by a massive stone sarcophagus.",
            "Ancient power radiates from the awakening Crypt Overlord!"),
        4: ("Shadow Throne Room", "Darkness coalesces into a throne of pure shadow.",
            "The Shadow King emerges from the void itself!"),
        5: ("Infernal Throne", "Rivers of lava flow around a platform of volcanic rock.",
            "The Flame Lord rises in a pillar of fire!"),
        6: ("Frozen Cavern", "A bone-chilling cavern covered in ancient ice.",
            "The Frost Titan awakens from its eternal slumber!"),
        7: ("Abyssal Gate", "A massive portal to the demonic realm dominates this chamber.",
            "The Demon Prince steps through from the abyss!"),
        8: ("Void Nexus", "Reality fractures and bends around this impossible space.",
            "The Void Archon manifests from nothingness!"),
        9: ("Primordial Chamber", "Ancient stone predating time itself forms this vast arena.",
            "The Primordial Beast, older than the world, awakens!"),
        10: ("Reality's Edge", "The fabric of existence itself unravels in this final chamber.",
             "The Reality Breaker threatens to unmake all creation!")
    }
    
    @classmethod
    def generate(cls, floor: int) -> Dict[str, Any]:
        """Generate complete boss configuration"""
        data = cls.BOSS_DATA[floor]
        return {
            'floor': floor,
            'name': data['name'],
            'base_health': 120 + (floor - 1) * 20,
            'health_scaling': 8 + (floor - 1),
            'damage': 22 + (floor - 1) * 2,
            'exp_reward': 150 + (floor - 1) * 30,
            'special_attack': data['special'],
            'special_bonus': 12 + (floor - 1) * 2,
            'stat_bonus': 2 + (floor - 1) // 2,
            'min_level': floor * 2,
            'weapons': data['weapons']
        }
    
    @classmethod
    def get_boss_room_template(cls, floor: int) -> RoomTemplate:
        """Get boss room template"""
        room_data = cls.BOSS_ROOMS[floor]
        return RoomTemplate(
            room_data[0], room_data[1], room_data[2],
            ["champion's prize", 'ultimate health potion'],
            enemy_count=0, special_type='boss'
        )

#################################################################################
# UNIFIED ITEM HANDLER
#################################################################################
class ItemHandler:
    """Centralized item management system"""
    
    @staticmethod
    def use_item(player: 'Player', category: str, item_name: Optional[str] = None) -> bool:
        """Generic item usage"""
        item_dict = ItemHandler._get_item_dict(category)
        
        if not item_name:
            available = [i for i in player.inventory if i in item_dict]
            if not available:
                print(f"No {category} items!")
                return False
            item_name = ItemHandler._show_menu(available, item_dict, category)
            if not item_name:
                return False
        
        if item_name in player.inventory and item_name in item_dict:
            player.inventory.remove(item_name)
            return ItemHandler._apply_effect(player, item_name, item_dict[item_name], category)
        
        print(f"You don't have '{item_name}' or it's not a {category} item.")
        return False
    
    @staticmethod
    def _get_item_dict(category: str) -> Dict:
        """Get item dictionary by category"""
        return {
            'healing': GameConstants.HEALING_ITEMS,
            'experience': GameConstants.EXPERIENCE_ITEMS,
            'wearable': GameConstants.WEARABLE_ITEMS
        }.get(category, {})
    
    @staticmethod
    def _show_menu(items: List[str], item_dict: Dict, category: str) -> Optional[str]:
        """Show item selection menu"""
        print(f"Available {category} items:")
        for i, item in enumerate(items, 1):
            effect = item_dict[item]
            desc = ItemHandler._format_effect(effect)
            print(f"{i}. {item} - {desc}")
        
        try:
            choice = int(input(f"Choose (1-{len(items)}): ")) - 1
            return items[choice] if 0 <= choice < len(items) else None
        except (ValueError, KeyboardInterrupt):
            print("Cancelled.")
            return None
    
    @staticmethod
    def _format_effect(effect: Dict) -> str:
        """Format effect description"""
        if 'heal' in effect:
            heal_text = "full heal" if effect['heal'] == 'full' else f"+{effect['heal']}"
            return f"{heal_text} {effect['type']}"
        elif 'amount' in effect:
            return f"+{effect['amount']} exp"
        elif 'bonus' in effect:
            return f"+{effect['bonus']} {effect['stat']}"
        return "special"
    
    @staticmethod
    def _apply_effect(player: 'Player', item_name: str, effect: Dict, category: str) -> bool:
        """Apply item effect"""
        if category == 'healing':
            if effect['type'] == 'health':
                if effect['heal'] == 'full':
                    heal = player.max_health - player.health
                    player.health = player.max_health
                else:
                    heal = min(effect['heal'], player.max_health - player.health)
                    player.health += heal
                print(f"+ Restored {heal} health!")
            else:  # mana
                mana = min(effect['heal'], player.max_mana - player.mana)
                player.mana += mana
                print(f"+ Restored {mana} mana!")
        
        elif category == 'experience':
            player.gain_experience(effect['amount'])
        
        elif category == 'wearable':
            player.stats[effect['stat']] += effect['bonus']
            player.wearables.append({'item': item_name, 'stat': effect['stat'], 'bonus': effect['bonus']})
            print(f"*** Equipped {item_name}! +{effect['bonus']} {effect['stat']}")
        
        return True

#################################################################################
# CENTRALIZED DAMAGE CALCULATOR
#################################################################################
class DamageCalculator:
    """Unified damage calculation system"""
    
    @staticmethod
    def calculate_player_damage(player: 'Player') -> int:
        """Calculate player damage with all modifiers"""
        # Golden Gun instant kill
        if player.weapon and player.weapon.get('special') == 'instant_kill':
            if player.weapon.get('uses_remaining', 0) > 0:
                player.weapon['uses_remaining'] -= 1
                remaining = player.weapon['uses_remaining']
                print(f"*** THE {player.weapon['base_name'].upper()} FIRES!")
                print(f"*** INSTANT OBLITERATION! ({remaining}/6 remaining)")
                if remaining <= 0:
                    print(f"The {player.weapon['base_name']} crumbles to dust...")
                    player.weapon = None
                return 99999
        
        # No weapon
        if not player.weapon:
            return random.randint(1, 5)
        
        # Normal damage calculation
        base = player.weapon['damage']
        strength_bonus = random.randint(1, player.stats['strength'] // 3)
        rarity = player.weapon.get('rarity', 'common')
        multiplier = GameConstants.WEAPON_RARITIES[rarity]['multiplier']
        
        return int((base + strength_bonus) * multiplier)
    
    @staticmethod
    def calculate_enemy_damage(base_damage: int, player: 'Player', is_boss: bool = False) -> int:
        """Calculate enemy damage with agility defense"""
        agility_defense = random.randint(1, player.stats['agility'] // (2 if is_boss else 3))
        final = base_damage - agility_defense
        min_damage = GameConstants.MIN_BOSS_DAMAGE if is_boss else GameConstants.MIN_ENEMY_DAMAGE
        return max(min_damage, final)

#################################################################################
# WEAPON COMPARISON SYSTEM
#################################################################################
class WeaponComparison:
    """Compare weapons and show detailed stats"""
    
    @staticmethod
    def compare_weapons(new_weapon: Dict, current_weapon: Optional[Dict], player: 'Player') -> str:
        """Generate detailed weapon comparison"""
        lines = []
        lines.append("\n" + "="*50)
        lines.append("WEAPON COMPARISON")
        lines.append("="*50)
        
        # New weapon stats
        new_dmg = new_weapon['damage']
        new_rarity = new_weapon.get('rarity', 'common')
        new_mult = GameConstants.WEAPON_RARITIES[new_rarity]['multiplier']
        
        # Calculate effective damage with strength bonus
        str_bonus_avg = player.stats['strength'] // 3
        new_effective = int((new_dmg + str_bonus_avg) * new_mult)
        
        lines.append(f"\nNEW: {new_weapon['name']}")
        lines.append(f"  Rarity: {new_rarity.upper()}")
        lines.append(f"  Base Damage: {new_dmg}")
        lines.append(f"  Rarity Multiplier: {new_mult}x")
        lines.append(f"  Avg Effective Damage: ~{new_effective}")
        
        if current_weapon:
            curr_dmg = current_weapon['damage']
            curr_rarity = current_weapon.get('rarity', 'common')
            curr_mult = GameConstants.WEAPON_RARITIES[curr_rarity]['multiplier']
            curr_effective = int((curr_dmg + str_bonus_avg) * curr_mult)
            
            lines.append(f"\nCURRENT: {current_weapon['name']}")
            lines.append(f"  Rarity: {curr_rarity.upper()}")
            lines.append(f"  Base Damage: {curr_dmg}")
            lines.append(f"  Rarity Multiplier: {curr_mult}x")
            lines.append(f"  Avg Effective Damage: ~{curr_effective}")
            
            diff = new_effective - curr_effective
            if diff > 0:
                lines.append(f"\n>>> UPGRADE: +{diff} damage ({'+' if diff > 0 else ''}{int((diff/curr_effective)*100)}%)")
            elif diff < 0:
                lines.append(f"\n>>> DOWNGRADE: {diff} damage ({int((diff/curr_effective)*100)}%)")
            else:
                lines.append(f"\n>>> SAME: No damage difference")
        else:
            lines.append(f"\nCURRENT: None (unarmed)")
            lines.append(f">>> HUGE UPGRADE!")
        
        lines.append("="*50)
        return '\n'.join(lines)

#################################################################################
# VISUAL MAP GENERATOR
#################################################################################
class MapGenerator:
    """Generate ASCII visual map of explored rooms"""
    
    @staticmethod
    def generate_visual_map(floors: Dict[int, Dict[str, 'Room']], 
                           current_floor: int, 
                           current_room: str,
                           visited_rooms: Set[str]) -> str:
        """Generate ASCII map for current floor"""
        floor_rooms = floors[current_floor]
        visited_floor = [r for r in visited_rooms if r in floor_rooms]
        
        if not visited_floor:
            return "No rooms explored on this floor yet!"
        
        # Build room graph
        room_graph = {}
        for room_id in visited_floor:
            room = floor_rooms[room_id]
            room_graph[room_id] = {
                'name': room.name[:15],
                'exits': {d: floor_rooms[room.exits[d]].name[:15] 
                         for d in room.exits if room.exits[d] in visited_floor}
            }
        
        # Start building map from starting room
        lines = []
        lines.append("=" * 70)
        lines.append(f"FLOOR {current_floor} MAP - Explored Rooms")
        lines.append("=" * 70)
        
        for room_id in sorted(visited_floor):
            room = floor_rooms[room_id]
            is_current = (room_id == current_room)
            
            # Draw room box
            marker = ">>>" if is_current else "   "
            lines.append(f"\n{marker} ┌─────────────────────────────────┐")
            lines.append(f"{marker} │ {room.name[:29]:<29} │")
            lines.append(f"{marker} └─────────────────────────────────┘")
            
            # Show exits
            exits_list = []
            if 'north' in room.exits and room.exits['north'] in visited_floor:
                exits_list.append("↑N")
            if 'south' in room.exits and room.exits['south'] in visited_floor:
                exits_list.append("↓S")
            if 'east' in room.exits and room.exits['east'] in visited_floor:
                exits_list.append("→E")
            if 'west' in room.exits and room.exits['west'] in visited_floor:
                exits_list.append("←W")
            if 'up' in room.exits:
                exits_list.append("↑UP")
            if 'down' in room.exits:
                exits_list.append("↓DOWN")
            if 'secret' in room.exits and room.exits['secret'] in visited_floor:
                exits_list.append("★SECRET")
            
            if exits_list:
                lines.append(f"    Exits: {' '.join(exits_list)}")
            
            # Show contents
            if room.enemies:
                lines.append(f"    Enemies: {', '.join(room.enemies)}")
            if room.items:
                lines.append(f"    Items: {', '.join(room.items[:3])}" + 
                           (" ..." if len(room.items) > 3 else ""))
        
        lines.append("\n" + "=" * 70)
        lines.append(f"Explored: {len(visited_floor)}/{len(floor_rooms)} rooms")
        lines.append(">>> = Current Location")
        lines.append("=" * 70)
        
        return '\n'.join(lines)

#################################################################################
# PLAYER CLASS
#################################################################################
class Player:
    """Player character with stats and inventory"""
    
    def __init__(self, name: str, character_class: str = "warrior"):
        self.name = name
        self.character_class = character_class
        self.class_tier = 1
        self.level = 1
        self.experience = 0
        self.experience_to_next = GameConstants.BASE_EXPERIENCE_NEEDED
        
        config = GameConstants.CLASSES[character_class]
        self.stats = config['base_stats'].copy()
        self.rarity_boost = 0.0
        
        self.health = config['base_health']
        self.max_health = self.health
        self.mana = config['base_mana']
        self.max_mana = self.mana
        
        self.inventory: List[str] = []
        self.inventory_weapons: List[Dict] = []
        self.weapon: Optional[Dict] = None
        self.wearables: List[Dict] = []
        self.max_inventory = config['inventory_slots']
        
        self.special_items: List[str] = []
        
        self.current_floor = 1
        self.current_room = "start"
        self.visited_rooms: Set[str] = set()
        
        self.bosses_defeated: List[str] = []
        self.gold_coins = 0
        self.secret_room_unlocked = False
    
    def gain_experience(self, amount: int) -> None:
        """Add experience and handle level ups"""
        self.experience += amount
        print(f"+ {amount} experience!")
        logger.info(f"Player gained {amount} XP. Total: {self.experience}/{self.experience_to_next}")
        
        while self.experience >= self.experience_to_next:
            self._level_up()
    
    def _level_up(self) -> None:
        """Handle level up"""
        self.experience -= self.experience_to_next
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * GameConstants.EXPERIENCE_MULTIPLIER)
        
        config = GameConstants.CLASSES[self.character_class]
        old_max_inv = self.max_inventory
        
        self.max_inventory = config['inventory_slots'] + (self.level - 1) * GameConstants.INVENTORY_SLOTS_PER_LEVEL + (self.class_tier - 1) * GameConstants.INVENTORY_SLOTS_PER_TIER
        
        growth = config['stat_growth']
        for stat, bonus in growth.items():
            self.stats[stat] += bonus
        
        health_gain = config['health_per_level']
        self.max_health += health_gain
        self.max_mana += GameConstants.MANA_PER_LEVEL
        self.health = self.max_health
        self.mana = self.max_mana
        
        logger.info(f"LEVEL UP: {self.name} reached level {self.level}. HP: {self.max_health}, MP: {self.max_mana}")
        
        print(f"\n*** LEVEL UP! Now level {self.level}!")
        print(f"Health +{health_gain} (now {self.max_health}) | Mana +{GameConstants.MANA_PER_LEVEL} (now {self.max_mana})")
        if self.max_inventory > old_max_inv:
            print(f"Inventory: {old_max_inv} → {self.max_inventory} slots")
        print("Fully healed!")
    
    def can_upgrade_class(self) -> bool:
        """Check if class upgrade available"""
        if self.class_tier >= 3:
            return False
        return self.level >= GameConstants.CLASS_UPGRADE_LEVELS[self.class_tier - 1]
    
    def get_class_title(self) -> str:
        """Get current class title"""
        return GameConstants.CLASS_NAMES[self.class_tier][self.character_class]
    
    def upgrade_class(self) -> bool:
        """Upgrade class tier"""
        if not self.can_upgrade_class():
            return False
        
        old_tier = self.class_tier
        self.class_tier += 1
        self.rarity_boost += GameConstants.RARITY_BOOST_PER_TIER
        
        config = GameConstants.CLASSES[self.character_class]
        tier_bonus = (self.class_tier - 1) * 5
        
        self.stats = {k: v + tier_bonus for k, v in config['base_stats'].items()}
        
        growth = config['stat_growth']
        for stat, bonus in growth.items():
            self.stats[stat] += bonus * (self.level - 1)
        
        old_health = self.max_health
        old_mana = self.max_mana
        
        self.max_health = config['base_health'] + (self.class_tier - 1) * 30 + (self.level - 1) * config['health_per_level']
        self.max_mana = config['base_mana'] + (self.class_tier - 1) * 25 + (self.level - 1) * GameConstants.MANA_PER_LEVEL
        self.health = self.max_health
        self.mana = self.max_mana
        
        logger.info(f"CLASS UPGRADE: {self.name} advanced from tier {old_tier} to {self.class_tier} ({self.get_class_title()})")
        
        print(f"\n*** CLASS UPGRADE! Now a {self.get_class_title()}!")
        print(f"All stats +5 | Health +{self.max_health - old_health} | Mana +{self.max_mana - old_mana}")
        print(f"Loot drop boost: +{self.rarity_boost * 100}%")
        print("Fully healed!")
        return True
    
    def add_item(self, item: str) -> bool:
        """Add item to inventory"""
        if item == 'old map':
            if 'old map' not in self.special_items:
                self.special_items.append('old map')
                print(f"+ {item} (★ doesn't use inventory space)")
                print("  Use 'use old map' to view the dungeon, or 'map' as shortcut")
                logger.debug(f"Player picked up map (special item)")
                return True
            else:
                print("You already have a map!")
                return False
        
        if len(self.inventory) >= self.max_inventory:
            print(f"X Inventory full! ({self.max_inventory} slots)")
            return False
        self.inventory.append(item)
        print(f"+ {item}")
        return True
    
    def add_weapon_to_inventory(self, weapon: Dict) -> bool:
        """Store weapon in inventory"""
        if len(self.inventory) >= self.max_inventory:
            print(f"X Inventory full!")
            return False
        self.inventory_weapons.append(weapon)
        self.inventory.append(f"WEAPON: {weapon['name']}")
        print(f"Stored: {weapon['name']}")
        return True
    
    def equip_weapon(self, weapon: Dict) -> None:
        """Equip weapon"""
        self.weapon = weapon
        print(f"Equipped: {weapon['name']}")
    
    def switch_weapon(self, identifier: Optional[str] = None) -> bool:
        """Switch to different weapon"""
        if not self.inventory_weapons:
            print("No spare weapons!")
            return False
        
        target = None
        if identifier:
            for w in self.inventory_weapons:
                if identifier.lower() in w['name'].lower():
                    target = w
                    break
            if not target:
                print(f"No weapon matching '{identifier}'")
                return False
        else:
            print("Available weapons:")
            for i, w in enumerate(self.inventory_weapons, 1):
                print(f"{i}. {w['name']} ({w['damage']} dmg)")
            try:
                choice = int(input("Choose: ")) - 1
                target = self.inventory_weapons[choice] if 0 <= choice < len(self.inventory_weapons) else None
            except (ValueError, KeyboardInterrupt):
                print("Cancelled")
                return False
        
        if target:
            if self.weapon:
                self.inventory_weapons.append(self.weapon)
                self.inventory.append(f"WEAPON: {self.weapon['name']}")
            self.inventory_weapons.remove(target)
            self.inventory.remove(f"WEAPON: {target['name']}")
            self.weapon = target
            print(f"Equipped: {target['name']} ({target['damage']} dmg)")
            return True
        return False
    
    def can_add_item(self) -> bool:
        """Check if there's space in inventory"""
        return len(self.inventory) < self.max_inventory
    
    def get_inventory_count(self) -> int:
        """Get current number of items in inventory"""
        return len(self.inventory)
    
    def has_map(self) -> bool:
        """Check if player has a map"""
        return 'old map' in self.special_items
    
    def discard_special_item(self, item_name: str) -> bool:
        """Discard a special item"""
        if item_name in self.special_items:
            self.special_items.remove(item_name)
            logger.info(f"Player discarded special item: {item_name} on floor {self.current_floor}")
            return True
        return False
    
    def show_stats(self) -> None:
        """Display character sheet"""
        weapon = self.weapon['name'] if self.weapon else "None"
        print(f"\n=== {self.name} the {self.get_class_title()} ===")
        print(f"Level {self.level} (Tier {self.class_tier}/3) | XP: {self.experience}/{self.experience_to_next}")
        print(f"Health: {self.health}/{self.max_health} | Mana: {self.mana}/{self.max_mana}")
        print(f"Gold: {self.gold_coins} | Weapon: {weapon}")
        print(f"STR: {self.stats['strength']} | INT: {self.stats['intelligence']} | AGI: {self.stats['agility']}")
        print(f"Inventory: {len(self.inventory)}/{self.max_inventory} | Floor: {self.current_floor}/{GameConstants.NUM_FLOORS}")
        print(f"Bosses: {len(self.bosses_defeated)}/{GameConstants.NUM_FLOORS}")
        
        if self.wearables:
            print("\nWearables:")
            for w in self.wearables:
                print(f"  {w['item']}: +{w['bonus']} {w['stat']}")
        
        if self.can_upgrade_class():
            next_title = GameConstants.CLASS_NAMES[self.class_tier + 1][self.character_class]
            print(f"\n*** CLASS UPGRADE AVAILABLE! → {next_title}")
    
    def show_status_summary(self) -> None:
        """Quick status"""
        weapon = self.weapon['name'] if self.weapon else "None"
        print(f"\n[F{self.current_floor}] HP:{self.health}/{self.max_health} MP:{self.mana}/{self.max_mana} W:{weapon}")
    
    def to_dict(self) -> Dict:
        """Serialize for saving"""
        return {
            'name': self.name, 'character_class': self.character_class, 'class_tier': self.class_tier,
            'level': self.level, 'experience': self.experience, 'experience_to_next': self.experience_to_next,
            'stats': self.stats, 'health': self.health, 'max_health': self.max_health,
            'mana': self.mana, 'max_mana': self.max_mana, 'inventory': self.inventory,
            'inventory_weapons': self.inventory_weapons, 'weapon': self.weapon, 'wearables': self.wearables,
            'max_inventory': self.max_inventory, 'current_floor': self.current_floor,
            'current_room': self.current_room, 'visited_rooms': list(self.visited_rooms),
            'bosses_defeated': self.bosses_defeated, 'rarity_boost': self.rarity_boost,
            'gold_coins': self.gold_coins, 'secret_room_unlocked': self.secret_room_unlocked,
            'special_items': self.special_items
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Deserialize from save"""
        player = cls(data['name'], data['character_class'])
        for key, value in data.items():
            if key == 'visited_rooms':
                setattr(player, key, set(value))
            elif key == 'special_items':
                setattr(player, key, value if value else [])
            else:
                setattr(player, key, value)
        return player

#################################################################################
# ROOM CLASS
#################################################################################
class Room:
    """Dungeon room"""
    def __init__(self, name: str, description: str, floor: int,
                 items: List[str] = None, exits: Dict[str, str] = None,
                 enemies: List[str] = None, atmosphere: str = ""):
        self.name = name
        self.description = description
        self.floor = floor
        self.items = items or []
        self.exits = exits or {}
        self.enemies = enemies or []
        self.visited = False
        self.atmosphere = atmosphere
    
    def describe(self) -> None:
        """Show room description"""
        if not self.visited:
            print(f"\n{self.description}")
            if self.atmosphere:
                print(f"{self.atmosphere}")
            self.visited = True
        else:
            print(f"\nYou are in {self.name}")
            if 'merchant' in self.atmosphere.lower():
                print("A merchant is here. Use 'shop' to trade.")
        
        if self.enemies:
            print(f"\n*** ENEMIES:")
            for enemy in self.enemies:
                info = GameConstants.ENEMIES.get(enemy.lower())
                if info:
                    print(f"  - {enemy}: {info['desc']}")
        
        if self.items:
            print(f"\nItems: {', '.join(self.items)}")
        if self.exits:
            print(f"Exits: {', '.join(self.exits.keys())}")

#################################################################################
# WEAPON SYSTEM
#################################################################################
class WeaponSystem:
    """Weapon generation and management"""
    
    @classmethod
    def generate_weapon(cls, player: Player, force_rarity: Optional[str] = None) -> Dict:
        """Generate random weapon"""
        if not force_rarity and random.random() < GameConstants.GOLDEN_GUN_DROP_RATE:
            logger.warning(f"GOLDEN GUN GENERATED for {player.name} at level {player.level}!")
            return cls._create_golden_gun()
        
        equipped_rarity = None
        if player.weapon and not force_rarity:
            equipped_rarity = player.weapon.get('rarity', 'common')
        
        rarity = force_rarity or cls._calculate_rarity(player.level, player.rarity_boost, equipped_rarity)
        weapon_type = random.choice(GameConstants.CLASSES[player.character_class]['weapon_types'])
        
        material = random.choice(GameConstants.WEAPON_MATERIALS[rarity])
        weapon_name = random.choice(GameConstants.WEAPON_TYPES[weapon_type])
        
        base_damage = random.randint(8, 15) + (player.level * 2)
        multiplier = GameConstants.WEAPON_RARITIES[rarity]['multiplier']
        final_damage = int(base_damage * multiplier)
        
        weapon = {
            'name': f"{material} {weapon_name}",
            'damage': final_damage,
            'type': weapon_type,
            'rarity': rarity,
            'base_name': f"{material} {weapon_name}"
        }
        
        logger.debug(f"Generated {rarity} weapon: {weapon['name']} ({final_damage} dmg) for level {player.level} player")
        
        return weapon
    
    @classmethod
    def _calculate_rarity(cls, level: int, boost: float, equipped_rarity: Optional[str] = None) -> str:
        """Calculate weapon rarity with boost for better than equipped"""
        boost_val = int(boost * 100)
        chances = {
            'common': max(50 - (level * 2) - boost_val, 10),
            'uncommon': min(25 + level, 35),
            'rare': min(15 + level // 2 + boost_val // 3, 25),
            'epic': min(8 + level // 3 + boost_val // 3, 15),
            'legendary': min(2 + level // 4 + boost_val // 3, 8),
            'mythic': min(level // 6 + boost_val // 3, 2)
        }
        
        if equipped_rarity and equipped_rarity in GameConstants.RARITY_ORDER:
            equipped_idx = GameConstants.RARITY_ORDER.index(equipped_rarity)
            boost_amount = int(GameConstants.BETTER_WEAPON_RARITY_BOOST * 100)
            
            for rarity in GameConstants.RARITY_ORDER:
                if rarity == 'divine':
                    continue
                rarity_idx = GameConstants.RARITY_ORDER.index(rarity)
                if rarity_idx > equipped_idx:
                    chances[rarity] = min(chances[rarity] + boost_amount // (rarity_idx - equipped_idx), 40)
                elif rarity_idx < equipped_idx:
                    chances[rarity] = max(chances[rarity] - boost_amount // 2, 5)
        
        total = sum(chances.values())
        if total != 100:
            adjustment = 100 - total
            chances['common'] += adjustment
        
        rand = random.randint(1, 100)
        cumulative = 0
        for rarity, chance in chances.items():
            cumulative += chance
            if rand <= cumulative:
                return rarity
        
        return 'common'
    
    @classmethod
    def _create_golden_gun(cls) -> Dict:
        """Create Golden Gun"""
        name = random.choice(GameConstants.GOLDEN_GUN_NAMES)
        return {
            'name': f"*** {name}",
            'damage': 99999,
            'type': 'divine',
            'rarity': 'divine',
            'base_name': name,
            'uses_remaining': 6,
            'max_uses': 6,
            'special': 'instant_kill'
        }
    
    @classmethod
    def create_starting_weapons(cls) -> Dict[str, List[Dict]]:
        """Create starting weapon choices"""
        return {
            'warrior': [
                {'name': 'Iron Sword', 'damage': 18, 'type': 'melee', 'rarity': 'common', 'base_name': 'Iron Sword'},
                {'name': 'Steel Axe', 'damage': 20, 'type': 'melee', 'rarity': 'common', 'base_name': 'Steel Axe'},
                {'name': 'Bronze Hammer', 'damage': 22, 'type': 'melee', 'rarity': 'common', 'base_name': 'Bronze Hammer'}
            ],
            'mage': [
                {'name': 'Wooden Staff', 'damage': 14, 'type': 'magic', 'rarity': 'common', 'base_name': 'Wooden Staff'},
                {'name': 'Apprentice Wand', 'damage': 13, 'type': 'magic', 'rarity': 'common', 'base_name': 'Apprentice Wand'},
                {'name': 'Crystal Orb', 'damage': 16, 'type': 'magic', 'rarity': 'common', 'base_name': 'Crystal Orb'}
            ],
            'rogue': [
                {'name': 'Steel Dagger', 'damage': 16, 'type': 'stealth', 'rarity': 'common', 'base_name': 'Steel Dagger'},
                {'name': 'Short Bow', 'damage': 17, 'type': 'stealth', 'rarity': 'common', 'base_name': 'Short Bow'},
                {'name': 'Assassin Blade', 'damage': 18, 'type': 'stealth', 'rarity': 'common', 'base_name': 'Assassin Blade'}
            ]
        }

#################################################################################
# COMBAT SYSTEM
#################################################################################
class CombatSystem:
    """Combat handler"""
    def __init__(self, game: 'Game'):
        self.game = game
    
    def fight_enemy(self, enemy_name: str, player: Player, room: Room) -> bool:
        """Regular enemy combat"""
        enemy = GameConstants.ENEMIES.get(enemy_name.lower())
        if not enemy:
            logger.warning(f"Unknown enemy attempted: {enemy_name}")
            print(f"Unknown enemy: {enemy_name}")
            return True
        
        hp = enemy['health']
        dmg = enemy['damage']
        
        logger.info(f"Combat started: {player.name} (Lvl {player.level}, HP {player.health}) vs {enemy_name} (HP {hp})")
        
        print(f"\n*** Combat: {enemy_name}!")
        print(f"{enemy['desc']}")
        
        turn = 0
        while hp > 0 and player.health > 0:
            turn += 1
            damage = DamageCalculator.calculate_player_damage(player)
            hp -= damage
            weapon = player.weapon.get('base_name', player.weapon['name']) if player.weapon else 'fists'
            print(f"You strike with {weapon} for {damage} damage!")
            
            if hp <= 0:
                logger.info(f"Victory: {player.name} defeated {enemy_name} in {turn} turns. Gained {enemy['exp']} XP")
                print(f"*** Defeated {enemy_name}!")
                room.enemies.remove(enemy_name)
                player.gain_experience(enemy['exp'])
                self._handle_drops(enemy_name, room, player)
                return True
            
            hit = DamageCalculator.calculate_enemy_damage(dmg, player)
            player.health -= hit
            print(f"{enemy_name} hits for {hit} damage!")
            
            if player.health <= 0:
                logger.error(f"PLAYER DEATH: {player.name} (Lvl {player.level}) killed by {enemy_name} on floor {player.current_floor}")
                print("*** DEFEATED! GAME OVER!")
                return False
        
        return True
    
    def _handle_drops(self, enemy_name: str, room: Room, player: Player) -> None:
        """Handle enemy drops"""
        rarity = player.weapon.get('rarity', 'common') if player.weapon else 'common'
        multiplier = GameConstants.WEAPON_RARITIES[rarity]['multiplier']
        drop_chance = GameConstants.ITEM_DROP_BASE_CHANCE + (multiplier * 0.1)
        
        if random.random() < GameConstants.GOLD_DROP_CHANCE:
            coins = random.randint(GameConstants.GOLD_DROP_MIN, GameConstants.GOLD_DROP_MAX)
            player.gold_coins += coins
            print(f"+ {coins} gold coins!")
        
        if random.random() < drop_chance:
            if random.random() < GameConstants.WEAPON_DROP_CHANCE:
                print(f"+ Weapon cache dropped!")
                room.items.append("weapon cache")
            else:
                if player.character_class == 'mage':
                    drops = ["health potion", "magic scroll", "ice crystal"]
                else:
                    drops = ["health potion", "energy drink", "vitality tonic", "power ring", "swift boots"]
                item = random.choice(drops)
                room.items.append(item)
                print(f"+ {item}")
    
    def fight_boss(self, boss_name: str, player: Player, room: Room) -> bool:
        """Boss combat"""
        floor = player.current_floor
        boss_config = BossConfig.generate(floor)
        
        logger.info(f"BOSS FIGHT: {player.name} (Lvl {player.level}, HP {player.health}) vs {boss_name} on floor {floor}")
        
        print("\n" + "="*60)
        print(f"*** BOSS FIGHT: {boss_name.upper()}!")
        print("="*60)
        
        if player.level < boss_config['min_level']:
            logger.warning(f"Player {player.name} (Lvl {player.level}) attempting {boss_name} (recommended Lvl {boss_config['min_level']})")
            print(f"! WARNING: Recommended level {boss_config['min_level']}+!")
            try:
                if input("Continue? (y/n): ").strip().lower() not in ['y', 'yes']:
                    return True
            except KeyboardInterrupt:
                return True
        
        hp = boss_config['base_health'] + (player.level * boss_config['health_scaling'])
        max_hp = hp
        dmg = boss_config['damage']
        
        print(f"\n{boss_name}: {hp} HP")
        
        turn = 1
        while hp > 0 and player.health > 0:
            print(f"\n--- Turn {turn} ---")
            print(f"You: {player.health}/{player.max_health} | {boss_name}: {hp}/{max_hp}")
            
            print("\n1.Attack | 2.Magic | 3.Defend", end="")
            if any(i in GameConstants.HEALING_ITEMS for i in player.inventory):
                print(" | 4.Heal", end="")
            print()
            
            try:
                action = input("Action: ").strip()
            except KeyboardInterrupt:
                action = "1"
            
            player_dmg = 0
            defend = False
            
            if action == "1":
                player_dmg = DamageCalculator.calculate_player_damage(player)
                print(f"*** {player_dmg} damage!")
            elif action == "2":
                if player.mana >= GameConstants.MAGIC_MANA_COST:
                    player.mana -= GameConstants.MAGIC_MANA_COST
                    player_dmg = player.stats['intelligence'] + random.randint(*GameConstants.MAGIC_DAMAGE_RANGE)
                    print(f"*** Magic: {player_dmg} damage!")
                else:
                    print("Not enough mana!")
                    player_dmg = player.weapon['damage'] if player.weapon else 5
            elif action == "3":
                defend = True
                print("*** Defending!")
            elif action == "4":
                ItemHandler.use_item(player, 'healing')
            
            hp -= player_dmg
            if hp <= 0:
                break
            
            use_special = (hp < max_hp * GameConstants.BOSS_SPECIAL_HEALTH_THRESHOLD and
                          turn % GameConstants.BOSS_SPECIAL_TURN_FREQUENCY == 0)
            
            if use_special:
                boss_dmg = dmg + boss_config['special_bonus']
                if defend:
                    boss_dmg //= GameConstants.BOSS_DEFEND_REDUCTION
                print(f"*** {boss_config['special_attack']}! {boss_dmg} damage!")
            else:
                boss_dmg = dmg + random.randint(1, 10)
                boss_dmg = DamageCalculator.calculate_enemy_damage(boss_dmg, player, True)
                if defend:
                    boss_dmg //= GameConstants.BOSS_DEFEND_REDUCTION
                print(f"Boss attacks: {boss_dmg} damage!")
            
            player.health -= boss_dmg
            if player.health <= 0:
                logger.error(f"BOSS DEATH: {player.name} (Lvl {player.level}) defeated by {boss_name} on turn {turn}")
                print(f"\n*** Defeated by {boss_name}! GAME OVER!")
                return False
            
            turn += 1
        
        logger.info(f"BOSS VICTORY: {player.name} defeated {boss_name} in {turn} turns on floor {floor}")
        
        print("\n" + "="*60)
        print("*** VICTORY!")
        print("="*60)
        
        room.enemies.remove(boss_name)
        player.bosses_defeated.append(boss_name)
        player.gain_experience(boss_config['exp_reward'])
        
        weapon_data = boss_config['weapons'][player.character_class]
        weapon_type = GameConstants.CLASSES[player.character_class]['weapon_types'][0]
        boss_weapon = {
            'name': weapon_data[0],
            'damage': weapon_data[1],
            'type': weapon_type,
            'rarity': 'legendary',
            'base_name': weapon_data[0]
        }
        
        logger.info(f"Boss reward: {player.name} received {boss_weapon['name']} ({boss_weapon['damage']} dmg)")
        
        print(f"\n*** Legendary Reward: {boss_weapon['name']}!")
        print(f"Damage: {boss_weapon['damage']} | Rarity: Legendary")
        player.equip_weapon(boss_weapon)
        
        bonus = boss_config['stat_bonus']
        for stat in player.stats:
            player.stats[stat] += bonus
        
        player.health = player.max_health
        player.mana = player.max_mana
        
        print(f"\n*** All stats +{bonus}! Fully healed!")
        return True

#################################################################################
# COMMAND HANDLER WITH DECORATOR PATTERN
#################################################################################
class CommandRegistry:
    """Command registration system"""
    def __init__(self):
        self.commands = {}
    
    def register(self, *names):
        """Decorator for registering commands"""
        def decorator(func):
            for name in names:
                self.commands[name.lower()] = func
            return func
        return decorator
    
    def execute(self, command: str, args: List[str], game: 'Game') -> None:
        """Execute command with fuzzy matching"""
        cmd = command.lower()
        
        if cmd in self.commands:
            try:
                self.commands[cmd](game, *args)
            except Exception as e:
                logging.error(f"Command error: {e}", exc_info=True)
                print(f"Error: {e}")
            return
        
        matches = get_close_matches(cmd, self.commands.keys(), n=1, cutoff=0.6)
        if matches:
            print(f"Did you mean '{matches[0]}'?")
        else:
            print("Unknown command. Type 'help'")

#################################################################################
# GAME CLASS
#################################################################################
class Game:
    """Main game controller"""
    
    def __init__(self):
        self.player: Optional[Player] = None
        self.floors: Optional[Dict[int, Dict[str, Room]]] = None
        self.running = True
        self.combat = None
        self.registry = CommandRegistry()
        self._register_commands()
        
    def _register_commands(self):
        """Register all game commands"""
        r = self.registry.register
        
        @r('help', 'h')
        def cmd_help(g): g.show_help()
        
        @r('look', 'l')
        def cmd_look(g): g.look_around()
        
        @r('go')
        def cmd_go(g, direction): g.move(direction)
        
        @r('north', 'n')
        def cmd_north(g): g.move('north')
        
        @r('south', 's')
        def cmd_south(g): g.move('south')
        
        @r('east', 'e')
        def cmd_east(g): g.move('east')
        
        @r('west', 'w')
        def cmd_west(g): g.move('west')
        
        @r('up')
        def cmd_up(g): g.move('up')
        
        @r('down')
        def cmd_down(g): g.move('down')
        
        @r('take', 'get')
        def cmd_take(g, *args): g.take_item(' '.join(args))
        
        @r('takeall')
        def cmd_takeall(g): g.take_all_items()
        
        @r('inventory', 'inv', 'i')
        def cmd_inventory(g): g.show_inventory()
        
        @r('stats', 'status')
        def cmd_stats(g): g.player.show_stats()
        
        @r('fight', 'attack')
        def cmd_fight(g, *args): g.fight_enemy(' '.join(args))
        
        @r('fightall', 'attackall')
        def cmd_fightall(g): g.fight_all_enemies()
        
        @r('heal')
        def cmd_heal(g, *args): ItemHandler.use_item(g.player, 'healing', ' '.join(args) if args else None)
        
        @r('exp', 'experience')
        def cmd_exp(g, *args): ItemHandler.use_item(g.player, 'experience', ' '.join(args) if args else None)
        
        @r('equip', 'wear')
        def cmd_equip(g, *args): g.equip_wearable(' '.join(args) if args else None)
        
        @r('switch')
        def cmd_switch(g, *args): g.player.switch_weapon(' '.join(args) if args else None)
        
        @r('discard', 'drop')
        def cmd_discard(g, *args): g.discard_item(' '.join(args))
        
        @r('use')
        def cmd_use(g, *args): g.use_special_item(' '.join(args))
        
        @r('upgrade')
        def cmd_upgrade(g): g.upgrade_class()
        
        @r('shop', 'buy')
        def cmd_shop(g): g.open_shop()
        
        @r('map')
        def cmd_map(g): 
            if g.player.has_map():
                g.show_map()
            else:
                print("You need a map to use this command!")
                print("Look for one on the ground or buy one from a merchant.")
        
        @r('save')
        def cmd_save(g): g.save_game()
        
        @r('load')
        def cmd_load(g): g.load_game()
        
        @r('quit', 'exit')
        def cmd_quit(g): g.quit_game()
    
    def start_game(self):
        """Start game"""
        print("="*50)
        print(" TEXT ADVENTURE RPG - 10 FLOOR EDITION")
        print(f" Version {GameConstants.VERSION}")
        print("="*50)
        print("\n1.New Game | 2.Load Game")
        
        while True:
            try:
                choice = input("Choice: ").strip()
                if choice == '1':
                    self._create_character()
                    break
                elif choice == '2':
                    if self.load_game():
                        break
                    print("No save found. Starting new...")
                    self._create_character()
                    break
            except KeyboardInterrupt:
                print("\nInterrupted")
                return
        
        self.combat = CombatSystem(self)
        print("\nType 'help' for commands")
        self.look_around()
        self._game_loop()
    
    def _game_loop(self):
        """Main game loop"""
        while self.running:
            try:
                cmd_input = input("\n> ").strip().lower()
                if not cmd_input:
                    continue
                
                parts = cmd_input.split()
                command = parts[0]
                args = parts[1:]
                
                self.registry.execute(command, args, self)
                
                if self.player:
                    self.player.show_status_summary()
                    
            except KeyboardInterrupt:
                logger.info("Game interrupted by user")
                print("\n\nInterrupted. Save before quitting!")
                break
            except Exception as e:
                logging.error(f"Game loop error: {e}", exc_info=True)
                print(f"Error: {e}")
    
    def _create_character(self):
        """Create new character"""
        try:
            name = input("Name: ").strip() or "Adventurer"
            
            print("\n1.Warrior | 2.Mage | 3.Rogue")
            choice = input("Class: ").strip()
            char_class = {'1': 'warrior', '2': 'mage', '3': 'rogue'}.get(choice, 'warrior')
            
            self.player = Player(name, char_class)
            
            weapons = WeaponSystem.create_starting_weapons()[char_class]
            print("\nWeapons:")
            for i, w in enumerate(weapons, 1):
                print(f"{i}. {w['name']} ({w['damage']} dmg)")
            choice = input("Choose: ").strip()
            weapon = weapons[int(choice) - 1] if choice in ['1', '2', '3'] else weapons[0]
            self.player.equip_weapon(weapon.copy())
            
            logger.info(f"New character: {name} ({char_class}) with {weapon['name']}")
            
            self._generate_dungeon()
            
            print(f"\nWelcome, {name} the {char_class.title()}!")
            print(f"Weapon: {weapon['name']}")
            print(f"{GameConstants.NUM_FLOORS} floors await!")
            
        except Exception as e:
            logging.error(f"Character creation error: {e}", exc_info=True)
            self.player = Player("Adventurer", "warrior")
            self._generate_dungeon()
    
    def _generate_dungeon(self):
        """Generate complete dungeon"""
        logger.info("Starting dungeon generation...")
        print("\n*** Generating dungeon...")
        self.floors = {}
        
        total_rooms = 0
        for floor_num in range(1, GameConstants.NUM_FLOORS + 1):
            print(f"Floor {floor_num}...", end=" ")
            rooms = {}
            
            if floor_num == 1:
                start_id = 'start'
                rooms[start_id] = Room("Entrance Hall", "The dungeon entrance awaits.", floor_num,
                                      ['rusty key', 'health potion', 'old map'], {}, [], 
                                      "A merchant has set up shop here. Use 'shop' to trade.")
            else:
                start_id = f"floor{floor_num}_start"
                rooms[start_id] = Room(f"Floor {floor_num} Entrance", f"You arrive at floor {floor_num}.",
                                      floor_num, ['health potion'], {}, [], 
                                      "A merchant has set up shop here. Use 'shop' to trade.")
            
            templates = RoomTemplateConfig.get_templates_for_floor(floor_num)
            enemies = RoomTemplateConfig.get_enemies_for_floor(floor_num)
            num_rooms = random.randint(GameConstants.MIN_ROOMS_PER_FLOOR - 2, GameConstants.MAX_ROOMS_PER_FLOOR - 2)
            
            selected = random.sample(templates, min(num_rooms, len(templates)))
            for i, template in enumerate(selected):
                room_id = f"floor{floor_num}_room{i+1}"
                room_enemies = self._get_unique_enemies(enemies, template.enemy_count)
                
                if template.special_type == 'treasure':
                    room_enemies = ['treasure guardian'] + room_enemies[:1]
                
                items = self._filter_items_by_class(template.items.copy())
                
                rooms[room_id] = Room(template.name, template.description, floor_num,
                                     items, {}, room_enemies, template.atmosphere)
            
            boss_template = BossConfig.get_boss_room_template(floor_num)
            boss_config = BossConfig.generate(floor_num)
            boss_room_id = f"floor{floor_num}_boss"
            rooms[boss_room_id] = Room(boss_template.name, boss_template.description, floor_num,
                                       self._filter_items_by_class(boss_template.items),
                                       {}, [boss_config['name']], boss_template.atmosphere)
            
            if floor_num < GameConstants.NUM_FLOORS:
                stairs_id = f"floor{floor_num}_stairs"
                rooms[stairs_id] = Room("Ancient Stairway", "Stone stairs descend deeper.", floor_num)
            
            self._connect_rooms(rooms, start_id)
            
            self.floors[floor_num] = rooms
            total_rooms += len(rooms)
            print(f"{len(rooms)} rooms")
        
        for floor_num in range(1, GameConstants.NUM_FLOORS):
            stairs_id = f"floor{floor_num}_stairs"
            next_start = f"floor{floor_num+1}_start"
            if stairs_id in self.floors[floor_num] and next_start in self.floors.get(floor_num + 1, {}):
                self.floors[floor_num][stairs_id].exits['down'] = next_start
                self.floors[floor_num + 1][next_start].exits['up'] = stairs_id
        
        logger.info(f"Dungeon generated: {GameConstants.NUM_FLOORS} floors, {total_rooms} total rooms")
        print("*** Complete!")
    
    def _get_unique_enemies(self, pool: List[str], count: int) -> List[str]:
        """Get unique enemies from pool"""
        available = pool.copy()
        random.shuffle(available)
        return available[:min(count, len(available))]
    
    def _filter_items_by_class(self, items: List[str]) -> List[str]:
        """Replace mana items for non-mages"""
        if self.player.character_class == 'mage':
            return items
        
        replacements = {
            'magic scroll': 'energy drink',
            'ice crystal': 'power ring',
            'mana flower': 'armor piece'
        }
        return [replacements.get(i, i) for i in items]
    
    def _connect_rooms(self, rooms: Dict[str, Room], start_id: str):
        """Connect all rooms in floor"""
        directions = ['north', 'south', 'east', 'west']
        reverse = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        
        room_ids = list(rooms.keys())
        connected = {start_id}
        unconnected = set(room_ids) - connected
        
        while unconnected:
            current = random.choice(list(connected))
            target = random.choice(list(unconnected))
            
            available = [d for d in directions if d not in rooms[current].exits]
            if not available:
                continue
            
            direction = random.choice(available)
            rooms[current].exits[direction] = target
            rooms[target].exits[reverse[direction]] = current
            
            connected.add(target)
            unconnected.remove(target)
        
        for _ in range(len(room_ids) // 3):
            r1, r2 = random.sample(room_ids, 2)
            if r2 not in rooms[r1].exits.values():
                available = [d for d in directions if d not in rooms[r1].exits]
                if available:
                    direction = random.choice(available)
                    if reverse[direction] not in rooms[r2].exits:
                        rooms[r1].exits[direction] = r2
                        rooms[r2].exits[reverse[direction]] = r1
    
    def get_current_room(self) -> Room:
        """Get player's current room"""
        return self.floors[self.player.current_floor][self.player.current_room]
    
    def show_help(self):
        """Context-aware help"""
        room = self.get_current_room()
        
        print("\n" + "="*40)
        print("COMMANDS")
        print("="*40)
        print("look | go <dir> (n/s/e/w/up/down)")
        
        if room.enemies:
            print("fight <enemy> | fightall")
        
        if room.items or self.player.inventory:
            print("take <item> | takeall")
        
        print("inventory | stats")
        
        if any(i in GameConstants.HEALING_ITEMS for i in self.player.inventory):
            print("heal")
        if any(i in GameConstants.EXPERIENCE_ITEMS for i in self.player.inventory):
            print("exp")
        if any(i in GameConstants.WEARABLE_ITEMS for i in self.player.inventory):
            print("equip")
        if any(i in GameConstants.ACTIONABLE_ITEMS for i in self.player.inventory) or self.player.special_items:
            print("use <item>")
        if self.player.inventory_weapons:
            print("switch")
        if self.player.inventory or self.player.special_items:
            print("discard <item>")
        
        if self.player.current_floor == 1 and self.player.current_room == 'start':
            print("shop - Merchant available HERE")
        elif self.player.current_floor > 1 and 'start' in self.player.current_room:
            print("shop - Merchant available HERE")
        elif self.player.gold_coins > 0:
            print("shop - Visit floor start for merchant")
        
        if self.player.can_upgrade_class():
            print("upgrade")
        
        print("map | save | load | quit")
        
        if self.player.has_map():
            print("\n★ Map doesn't use inventory space")
        if room.enemies and len(room.enemies) > 1:
            print("★ Use 'fightall' to fight all enemies")
        
        print("="*40)
    
    def look_around(self):
        """Look at current room"""
        room = self.get_current_room()
        room.describe()
        self.player.visited_rooms.add(self.player.current_room)
    
    def move(self, direction: str):
        """Move in direction"""
        room = self.get_current_room()
        
        if direction not in room.exits:
            print("Can't go that way!")
            return
        
        next_id = room.exits[direction]
        
        if direction == 'down':
            boss_floor = self.player.current_floor
            boss_config = BossConfig.generate(boss_floor)
            if boss_config['name'] not in self.player.bosses_defeated:
                print(f"! Blocked! Defeat {boss_config['name']} first!")
                return
        
        old_floor = self.player.current_floor
        
        if direction in ['down', 'up'] and 'floor' in next_id:
            next_floor = int(next_id.split('_')[0].replace('floor', ''))
            if next_floor != self.player.current_floor:
                self.player.current_floor = next_floor
                print(f"→ Floor {self.player.current_floor}")
                
                if not self.player.has_map() and old_floor != next_floor:
                    start_room_id = f"floor{next_floor}_start"
                    if start_room_id in self.floors[next_floor]:
                        start_room = self.floors[next_floor][start_room_id]
                        if 'old map' not in start_room.items:
                            start_room.items.append('old map')
                            logger.info(f"Spawned new map in floor {next_floor} start room (player left previous map behind)")
                            print("★ You notice a map on the ground here!")
        
        self.player.current_room = next_id
        self.player.visited_rooms.add(next_id)
        print(f"You go {direction}.")
        self.look_around()
    
    def show_inventory(self):
        """Show organized inventory"""
        print(f"\n=== INVENTORY ({len(self.player.inventory)}/{self.player.max_inventory}) ===")
        
        if self.player.weapon:
            print(f"Equipped: {self.player.weapon['name']} ({self.player.weapon['damage']} dmg)")
        
        if self.player.special_items:
            print("\n[Special Items - No inventory space]")
            for item in self.player.special_items:
                print(f"  ★ {item}")
        
        if not self.player.inventory and not self.player.special_items:
            print("Empty")
            return
        
        categories = {
            'Healing': [i for i in self.player.inventory if i in GameConstants.HEALING_ITEMS],
            'Experience': [i for i in self.player.inventory if i in GameConstants.EXPERIENCE_ITEMS],
            'Wearables': [i for i in self.player.inventory if i in GameConstants.WEARABLE_ITEMS],
            'Special': [i for i in self.player.inventory if i in GameConstants.ACTIONABLE_ITEMS],
            'Weapons': [i for i in self.player.inventory if i.startswith("WEAPON:")],
            'Other': [i for i in self.player.inventory if not any([
                i in GameConstants.HEALING_ITEMS, i in GameConstants.EXPERIENCE_ITEMS,
                i in GameConstants.WEARABLE_ITEMS, i in GameConstants.ACTIONABLE_ITEMS,
                i.startswith("WEAPON:")
            ])]
        }
        
        for category, items in categories.items():
            if items:
                print(f"\n{category}:")
                for item in items:
                    display = item[8:] if item.startswith("WEAPON:") else item
                    print(f"  - {display}")
    
    def take_item(self, item_name: str):
        """Take item from room"""
        if not item_name:
            print("Take what?")
            return
        
        room = self.get_current_room()
        
        if room.enemies:
            print("! Defeat enemies first!")
            return
        
        if item_name not in room.items:
            print(f"No '{item_name}' here.")
            return
        
        if not self.player.can_add_item() and item_name not in GameConstants.WEARABLE_ITEMS and item_name != 'old map':
            print("Inventory full!")
            return
        
        room.items.remove(item_name)
        
        if item_name == "weapon cache":
            self._handle_weapon_cache()
        elif item_name == "champion's prize":
            self._handle_champions_prize()
        else:
            self._handle_regular_item(item_name)
    
    def take_all_items(self):
        """Pick up all items in the room"""
        room = self.get_current_room()
        
        if room.enemies:
            print("! Defeat enemies first!")
            return
        
        if not room.items:
            print("No items here.")
            return
        
        taken = 0
        for item in room.items[:]:
            if item == 'old map' or item in GameConstants.WEARABLE_ITEMS or self.player.can_add_item():
                room.items.remove(item)
                if item == "weapon cache":
                    self._handle_weapon_cache()
                elif item == "champion's prize":
                    self._handle_champions_prize()
                else:
                    self._handle_regular_item(item)
                taken += 1
        
        if taken:
            print(f"\n+ Picked up {taken} item(s)")
        if room.items:
            print(f"X Inventory full! Left: {', '.join(room.items)}")
    
    def _handle_weapon_cache(self):
        """Handle opening a weapon cache"""
        new_weapon = WeaponSystem.generate_weapon(self.player)
        
        if new_weapon.get('special') == 'instant_kill':
            print("\n*** LEGENDARY GOLDEN GUN! 6 INSTANT KILLS! ***")
        
        comparison = WeaponComparison.compare_weapons(new_weapon, self.player.weapon, self.player)
        print(comparison)
        
        if not self.player.weapon or new_weapon['damage'] > self.player.weapon['damage']:
            try:
                if input("\nEquip this weapon? (y/n): ").strip().lower() in ['y', 'yes']:
                    if self.player.weapon:
                        print(f"Replaced {self.player.weapon['name']}")
                    self.player.equip_weapon(new_weapon)
                else:
                    self.player.add_weapon_to_inventory(new_weapon)
            except KeyboardInterrupt:
                self.player.add_weapon_to_inventory(new_weapon)
        else:
            try:
                if input("\nWeaker weapon. Take anyway? (y/n): ").strip().lower() in ['y', 'yes']:
                    self.player.add_weapon_to_inventory(new_weapon)
                else:
                    print("Left weapon behind.")
            except KeyboardInterrupt:
                print("Left weapon behind.")
    
    def _handle_champions_prize(self):
        """Handle champion's prize"""
        weapon = WeaponSystem.generate_weapon(self.player, random.choice(['epic', 'legendary']))
        
        print("\n*** CHAMPION'S PRIZE! ***")
        comparison = WeaponComparison.compare_weapons(weapon, self.player.weapon, self.player)
        print(comparison)
        
        try:
            if input("\nEquip this weapon? (y/n): ").strip().lower() in ['y', 'yes']:
                if self.player.weapon:
                    print(f"Replaced {self.player.weapon['name']}")
                self.player.equip_weapon(weapon)
            else:
                self.player.add_weapon_to_inventory(weapon)
        except KeyboardInterrupt:
            self.player.add_weapon_to_inventory(weapon)
    
    def _handle_regular_item(self, item: str):
        """Handle picking up a regular item"""
        if item in GameConstants.EXPERIENCE_ITEMS:
            self.player.gain_experience(GameConstants.EXPERIENCE_ITEMS[item]['amount'])
            return
        
        if item == 'golden coin':
            coins = random.randint(3, 10)
            self.player.gold_coins += coins
            print(f"+ {coins} gold coins!")
            return
        
        if item in GameConstants.WEARABLE_ITEMS:
            self.player.inventory.append(item)
            print(f"+ {item} (wearable)")
            return
        
        self.player.add_item(item)
    
    def fight_enemy(self, enemy_name: str):
        """Fight enemy"""
        if not enemy_name:
            print("Fight what?")
            return
        
        room = self.get_current_room()
        
        matching = None
        for e in room.enemies:
            if e.lower() == enemy_name.lower():
                matching = e
                break
        
        if not matching:
            print(f"No '{enemy_name}' here!")
            if room.enemies:
                print(f"Enemies: {', '.join(room.enemies)}")
            return
        
        if not self.player.weapon:
            print("! No weapon!")
            try:
                if input("Fight anyway? (y/n): ").strip().lower() not in ['y', 'yes']:
                    return
            except KeyboardInterrupt:
                return
        
        is_boss = any(matching == BossConfig.generate(f)['name'] for f in range(1, 11))
        
        if is_boss:
            success = self.combat.fight_boss(matching, self.player, room)
        else:
            success = self.combat.fight_enemy(matching, self.player, room)
        
        if not success:
            self.running = False
    
    def fight_all_enemies(self):
        """Fight all enemies in room sequentially"""
        room = self.get_current_room()
        
        if not room.enemies:
            print("No enemies here!")
            return
        
        if not self.player.weapon:
            print("! No weapon!")
            try:
                if input("Fight anyway? (y/n): ").strip().lower() not in ['y', 'yes']:
                    return
            except KeyboardInterrupt:
                return
        
        bosses = [e for e in room.enemies if any(e == BossConfig.generate(f)['name'] for f in range(1, 11))]
        if bosses:
            print(f"! Cannot use 'fightall' on bosses: {', '.join(bosses)}")
            print("Fight bosses individually with 'fight <boss name>'")
            return
        
        total_enemies = len(room.enemies)
        print(f"\n*** Fighting all {total_enemies} enemies! ***")
        print(f"Starting HP: {self.player.health}/{self.player.max_health}\n")
        
        defeated = 0
        enemies_copy = room.enemies.copy()
        
        for enemy_name in enemies_copy:
            if enemy_name not in room.enemies:
                continue
            
            print(f"\n--- Enemy {defeated + 1}/{total_enemies}: {enemy_name} ---")
            
            enemy_stats = GameConstants.ENEMIES.get(enemy_name.lower())
            if enemy_stats:
                estimated_damage = enemy_stats['damage'] - (self.player.stats['agility'] // 3)
                estimated_damage = max(1, estimated_damage)
                
                if self.player.health <= estimated_damage * 2:
                    print(f"\n! WARNING: Low health ({self.player.health} HP)")
                    print(f"! {enemy_name} deals ~{estimated_damage} damage per hit")
                    print("! Consider:")
                    print("  - Use 'heal' to restore health")
                    print("  - Fight enemies one at a time")
                    try:
                        choice = input("Continue fighting? (y/n): ").strip().lower()
                        if choice not in ['y', 'yes']:
                            print("Stopped fighting. Enemies remaining.")
                            return
                    except KeyboardInterrupt:
                        print("\nStopped fighting.")
                        return
            
            success = self.combat.fight_enemy(enemy_name, self.player, room)
            
            if not success:
                self.running = False
                return
            
            defeated += 1
        
        print(f"\n*** VICTORY! Defeated all {defeated} enemies! ***")
        print(f"Final HP: {self.player.health}/{self.player.max_health}")
    
    def equip_wearable(self, item_name: Optional[str]):
        """Equip wearable item"""
        if not item_name:
            wearables = [i for i in self.player.inventory if i in GameConstants.WEARABLE_ITEMS]
            if not wearables:
                print("No wearables!")
                return
            
            print("Wearables:")
            for i, item in enumerate(wearables, 1):
                effect = GameConstants.WEARABLE_ITEMS[item]
                print(f"{i}. {item} (+{effect['bonus']} {effect['stat']})")
            
            try:
                choice = int(input("Choose: ")) - 1
                if 0 <= choice < len(wearables):
                    item_name = wearables[choice]
            except (ValueError, KeyboardInterrupt):
                print("Cancelled")
                return
        
        if item_name and item_name in self.player.inventory:
            self.player.inventory.remove(item_name)
            ItemHandler.use_item(self.player, 'wearable', item_name)
            self.player.inventory.append(item_name)
            self.player.inventory.remove(item_name)
        else:
            print(f"You don't have '{item_name}'")
    
    def discard_item(self, item_name: str):
        """Discard item"""
        if not item_name:
            print("Discard what?")
            return
        
        for item in self.player.special_items:
            if item.lower() == item_name.lower() or item_name.lower() in item.lower():
                if self.player.discard_special_item(item):
                    print(f"Discarded: {item} (can find a new one on next floor)")
                    return
        
        for item in self.player.inventory:
            if item.lower() == item_name.lower() or item_name.lower() in item.lower():
                if item.startswith("WEAPON:"):
                    weapon_name = item[8:]
                    for i, w in enumerate(self.player.inventory_weapons):
                        if w['name'] == weapon_name:
                            self.player.inventory_weapons.pop(i)
                            break
                self.player.inventory.remove(item)
                print(f"Discarded: {item}")
                return
        print(f"Don't have '{item_name}'")
    
    def use_special_item(self, item_name: str):
        """Use special actionable items"""
        if not item_name:
            print("Use what?")
            return
        
        if item_name == 'old map' and item_name in self.player.special_items:
            print("You study the old map...")
            self.show_map()
            return
        
        if item_name not in self.player.inventory:
            print(f"Don't have '{item_name}'")
            return
        
        if item_name not in GameConstants.ACTIONABLE_ITEMS:
            print(f"Can't use '{item_name}' like that")
            return
        
        action_type = GameConstants.ACTIONABLE_ITEMS[item_name]
        room = self.get_current_room()
        
        if action_type == 'light' and item_name == 'torch':
            if 'Hidden Alcove' in room.name and not self.player.secret_room_unlocked:
                print("\n*** You place the torch in the wall sconce...")
                print("A hidden door slides open!")
                
                self.player.secret_room_unlocked = True
                self.player.inventory.remove('torch')
                
                secret_id = f"floor{self.player.current_floor}_secret"
                room.exits['secret'] = secret_id
                
                if secret_id not in self.floors[self.player.current_floor]:
                    self.floors[self.player.current_floor][secret_id] = Room(
                        "Secret Treasure Vault",
                        "A hidden vault glitters with treasures!",
                        self.player.current_floor,
                        ['weapon cache', 'weapon cache', 'ultimate health potion',
                         'experience gem', 'wisdom gem', 'legendary artifact'],
                        {'out': self.player.current_room},
                        [],
                        "Countless riches await!"
                    )
                
                print("\nUse 'go secret' to enter!")
            else:
                print("You hold up the torch. Nothing unusual here.")
        
        elif action_type == 'key' and item_name == 'rusty key':
            if 'Vault' in room.name:
                print("\n*** The key fits perfectly! The chest opens!")
                self.player.inventory.remove('rusty key')
                
                treasures = ['weapon cache', 'weapon cache', 'legendary artifact',
                            'ultimate health potion', 'experience gem', 'power ring']
                for t in treasures:
                    if t not in room.items:
                        room.items.append(t)
                
                print(f"\nTreasures: {', '.join(treasures)}")
                print("The key crumbles to dust...")
            else:
                print("You examine the key. It looks like it would fit a large lock...")
        
        elif action_type == 'map':
            print("You study the old map...")
            self.show_map()
        
        elif action_type == 'offering' and item_name == 'ancient medallion':
            if 'Shrine' in room.name:
                print("\n*** The altar erupts with brilliant light!")
                print("Ancient power flows through you!")
                
                self.player.inventory.remove('ancient medallion')
                
                if self.player.character_class == 'warrior':
                    self.player.stats['strength'] += 8
                    self.player.stats['agility'] += 3
                    print("*** Strength +8! Agility +3!")
                elif self.player.character_class == 'mage':
                    self.player.stats['intelligence'] += 8
                    self.player.stats['strength'] += 3
                    print("*** Intelligence +8! Strength +3!")
                else:
                    self.player.stats['agility'] += 8
                    self.player.stats['intelligence'] += 3
                    print("*** Agility +8! Intelligence +3!")
                
                self.player.max_health += 20
                self.player.health = self.player.max_health
                self.player.max_mana += 15
                self.player.mana = self.player.max_mana
                
                print(f"*** Max health +20! Max mana +15! Fully healed!")
            else:
                print("You hold the medallion. It should be placed on an altar...")
    
    def upgrade_class(self):
        """Upgrade class tier"""
        if not self.player.can_upgrade_class():
            if self.player.class_tier >= 3:
                print("Already max tier!")
            else:
                next_level = GameConstants.CLASS_UPGRADE_LEVELS[self.player.class_tier - 1]
                print(f"Need level {next_level}")
            return
        
        current = self.player.get_class_title()
        next_title = GameConstants.CLASS_NAMES[self.player.class_tier + 1][self.player.character_class]
        
        print(f"\n*** CLASS UPGRADE!")
        print(f"Current: {current} (Tier {self.player.class_tier})")
        print(f"Upgrade to: {next_title} (Tier {self.player.class_tier + 1})")
        print("\nBenefits: +5 all stats, +30 HP, +25 MP, +5% loot")
        
        try:
            if input(f"\nUpgrade to {next_title}? (y/n): ").strip().lower() in ['y', 'yes']:
                if self.player.upgrade_class():
                    print("Upgrade successful!")
        except KeyboardInterrupt:
            print("Cancelled")
    
    def open_shop(self):
        """Open shop"""
        if self.player.current_floor > 1 and 'start' not in self.player.current_room:
            print("! No shop here. Visit the floor's starting room to find a merchant.")
            return
        
        if self.player.current_floor == 1 and self.player.current_room != 'start':
            print("! No shop here. Return to the entrance hall to find a merchant.")
            return
        
        print("\n" + "="*40)
        print("*** MERCHANT ***")
        print("="*40)
        print(f"Gold: {self.player.gold_coins}")
        
        items = [(k, v) for k, v in GameConstants.SHOP_ITEMS.items()
                if k != 'magic scroll' or self.player.character_class == 'mage']
        
        print("\nShop:")
        for i, (item, price) in enumerate(items, 1):
            print(f"{i}. {item} - {price}g")
        print(f"{len(items) + 1}. Leave")
        
        try:
            choice = int(input("\nBuy: ").strip())
            if choice == len(items) + 1:
                return
            
            if 1 <= choice <= len(items):
                item, price = items[choice - 1]
                if self.player.gold_coins >= price:
                    if self.player.can_add_item() or item in GameConstants.WEARABLE_ITEMS:
                        self.player.gold_coins -= price
                        if item in GameConstants.WEARABLE_ITEMS:
                            self.player.inventory.append(item)
                        else:
                            self.player.add_item(item)
                        print(f"Purchased {item} for {price}g!")
                        print(f"Gold remaining: {self.player.gold_coins}")
                    else:
                        print("Inventory full!")
                else:
                    print(f"Not enough gold! Need {price}g, have {self.player.gold_coins}g")
        except (ValueError, KeyboardInterrupt):
            print("Cancelled")
    
    def show_map(self):
        """Display visual dungeon map"""
        visual_map = MapGenerator.generate_visual_map(
            self.floors,
            self.player.current_floor,
            self.player.current_room,
            self.player.visited_rooms
        )
        print(visual_map)
    
    def save_game(self):
        """Save game state"""
        try:
            save_data = {
                'version': GameConstants.VERSION,
                'player': self.player.to_dict(),
                'floors': {}
            }
            
            for floor_num, floor_rooms in self.floors.items():
                save_data['floors'][str(floor_num)] = {
                    room_id: {
                        'items': room.items,
                        'enemies': room.enemies,
                        'visited': room.visited,
                        'exits': room.exits
                    } for room_id, room in floor_rooms.items()
                }
            
            with open(GameConstants.SAVE_FILE, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            logger.info(f"Game saved: {self.player.name} (Lvl {self.player.level}, Floor {self.player.current_floor})")
            print("✓ Game saved!")
        except Exception as e:
            logging.error(f"Save error: {e}", exc_info=True)
            print(f"✗ Save failed: {e}")
    
    def load_game(self) -> bool:
        """Load game state"""
        try:
            if not os.path.exists(GameConstants.SAVE_FILE):
                logger.debug("No save file found")
                return False
            
            with open(GameConstants.SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            
            if save_data.get('version') != GameConstants.VERSION:
                logger.warning(f"Save version mismatch: {save_data.get('version')} vs {GameConstants.VERSION}")
                print("! Save version mismatch")
                return False
            
            self.player = Player.from_dict(save_data['player'])
            
            if self.player.weapon and self.player.weapon.get('special') == 'instant_kill':
                if self.player.weapon.get('uses_remaining', 0) <= 0:
                    logger.info("Golden Gun depleted on load")
                    print("! Your Golden Gun has depleted...")
                    self.player.weapon = None
            
            self.floors = {}
            for floor_str, floor_data in save_data['floors'].items():
                floor_num = int(floor_str)
                self.floors[floor_num] = {}
                
                for room_id, room_data in floor_data.items():
                    if room_id == 'start':
                        name, desc, atmo = "Entrance Hall", "The dungeon entrance.", "A merchant has set up shop here. Use 'shop' to trade."
                    elif 'boss' in room_id:
                        template = BossConfig.get_boss_room_template(floor_num)
                        name, desc, atmo = template.name, template.description, template.atmosphere
                    elif 'stairs' in room_id:
                        name, desc, atmo = "Ancient Stairway", "Stone stairs descend deeper.", ""
                    elif 'secret' in room_id:
                        name, desc, atmo = "Secret Treasure Vault", "A hidden vault glitters with treasures!", "Countless riches!"
                    else:
                        templates = RoomTemplateConfig.get_templates_for_floor(floor_num)
                        if templates:
                            template = random.choice(templates)
                            name, desc, atmo = template.name, template.description, template.atmosphere
                        else:
                            name, desc, atmo = "Mysterious Room", "A dark room.", ""
                    
                    self.floors[floor_num][room_id] = Room(
                        name, desc, floor_num,
                        room_data['items'], room_data['exits'],
                        room_data['enemies'], atmo
                    )
                    self.floors[floor_num][room_id].visited = room_data['visited']
            
            logger.info(f"Game loaded: {self.player.name} (Lvl {self.player.level}, Floor {self.player.current_floor})")
            print(f"✓ Welcome back, {self.player.name} the {self.player.get_class_title()}!")
            return True
            
        except Exception as e:
            logging.error(f"Load error: {e}", exc_info=True)
            print(f"✗ Load failed: {e}")
            return False
    
    def quit_game(self):
        """Exit game"""
        try:
            if input("\nSave before quitting? (y/n): ").strip().lower() in ['y', 'yes']:
                self.save_game()
        except KeyboardInterrupt:
            pass
        
        print(f"\nThanks for playing, {self.player.name if self.player else 'Adventurer'}!")
        print("See you next time!")
        self.running = False

#################################################################################
# MAIN ENTRY POINT
#################################################################################
def main():
    """Main entry point"""
    try:
        game = Game()
        game.start_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n\nFatal error: {e}")
        print("Please report this bug!")

if __name__ == "__main__":
    main()
