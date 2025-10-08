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
from typing import Dict, List, Optional, Set, Tuple, Any
from difflib import get_close_matches

# Configure logging to track errors
logging.basicConfig(
    filename='game.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

#################################################################################
# CONFIGURATION & CONSTANTS
#################################################################################
class GameConstants:
    """
    Central configuration class containing all game constants and balance values.
    Modify these values to adjust game difficulty and behavior.
    """
    VERSION = "5.0.0"
    SAVE_FILE = "savegame.json"
    
    # Floor configuration - expanded to 10 floors
    NUM_FLOORS = 10
    MIN_ROOMS_PER_FLOOR = 10  # Increased from 8
    MAX_ROOMS_PER_FLOOR = 15  # Increased from 10
    
    # Class definitions with base stats and growth rates
    CLASSES = {
        'warrior': {
            'base_health': 120,
            'base_mana': 50,
            'base_stats': {'strength': 15, 'intelligence': 8, 'agility': 10},
            'health_per_level': 15,
            'inventory_slots': 8,
            'weapon_types': ['melee']
        },
        'mage': {
            'base_health': 80,
            'base_mana': 150,
            'base_stats': {'strength': 8, 'intelligence': 15, 'agility': 10},
            'health_per_level': 8,
            'inventory_slots': 6,
            'weapon_types': ['magic']
        },
        'rogue': {
            'base_health': 100,
            'base_mana': 75,
            'base_stats': {'strength': 10, 'intelligence': 10, 'agility': 15},
            'health_per_level': 12,
            'inventory_slots': 10,
            'weapon_types': ['stealth']
        }
    }
    
    # Class progression titles
    CLASS_NAMES = {
        1: {'warrior': 'Warrior', 'mage': 'Mage', 'rogue': 'Rogue'},
        2: {'warrior': 'Berserker', 'mage': 'Sorcerer', 'rogue': 'Assassin'},
        3: {'warrior': 'Paladin', 'mage': 'Archmage', 'rogue': 'Shadow Master'}
    }
    
    # Class upgrade levels - now supports progression to level 15+
    CLASS_UPGRADE_LEVELS = [5, 10, 15]
    RARITY_BOOST_PER_TIER = 0.05  # 5% better drop rates per tier
    
    # Weapon rarity system
    WEAPON_RARITIES = {
        'common': {'multiplier': 1.0, 'color': 'WHITE'},
        'uncommon': {'multiplier': 1.3, 'color': 'GREEN'},
        'rare': {'multiplier': 1.6, 'color': 'BLUE'},
        'epic': {'multiplier': 2.0, 'color': 'PURPLE'},
        'legendary': {'multiplier': 2.5, 'color': 'GOLD'},
        'mythic': {'multiplier': 3.0, 'color': 'RED'},
        'divine': {'multiplier': 999.0, 'color': 'STAR'}  # Golden Gun only
    }
    
    # Weapon type names by class
    WEAPON_TYPES = {
        'melee': ['Sword', 'Axe', 'Hammer', 'Spear', 'Blade', 'Greatsword', 'Mace'],
        'magic': ['Staff', 'Wand', 'Orb', 'Tome', 'Crystal', 'Scepter'],
        'stealth': ['Dagger', 'Bow', 'Claws', 'Shiv', 'Needle', 'Rapier']
    }
    
    # Material names by rarity level
    WEAPON_MATERIALS = {
        'common': ['Iron', 'Steel', 'Bronze', 'Copper', 'Stone'],
        'uncommon': ['Silver', 'Enchanted', 'Sharp', 'Sturdy', 'Fine'],
        'rare': ['Mithril', 'Elven', 'Dwarven', 'Mystic', 'Ancient'],
        'epic': ['Dragon', 'Phoenix', 'Ethereal', 'Celestial', 'Infernal'],
        'legendary': ['Godforged', 'Divine', 'Eternal', 'Primordial', 'Void'],
        'mythic': ['Cosmos', 'Reality', 'Infinity', 'Quantum', 'Supreme']
    }
    
    # Golden Gun - ultra rare instant kill weapon
    GOLDEN_GUN_NAMES = [
        "Excalibur's Vengeance", "Dragonslayer Supreme", "Godkiller Mk.VII",
        "The Infinity Decimator", "Cosmos Ender", "Reality Ripper"
    ]
    GOLDEN_GUN_DROP_RATE = 0.0002  # 0.02% chance
    
    # Complete enemy roster - 20+ unique enemies organized by floor theme
    ENEMIES = {
        # Floors 1-2: Dungeon/Prison Theme
        'sewer rat': {
            'health': 15, 'damage': 5, 'exp': 15, 
            'desc': 'A disease-ridden rat with glowing red eyes'
        },
        'goblin': {
            'health': 25, 'damage': 8, 'exp': 25, 
            'desc': 'A small, green-skinned creature wielding a crude club'
        },
        'skeleton': {
            'health': 30, 'damage': 10, 'exp': 30, 
            'desc': 'Animated bones held together by dark magic'
        },
        'prison guard': {
            'health': 40, 'damage': 12, 'exp': 35, 
            'desc': 'A corrupted guard in tattered armor'
        },
        
        # Floors 3-4: Crypt/Necromancy Theme
        'armored skeleton': {
            'health': 45, 'damage': 14, 'exp': 45, 
            'desc': 'A skeleton warrior clad in ancient armor'
        },
        'shadow wraith': {
            'health': 50, 'damage': 18, 'exp': 55, 
            'desc': 'A spectral being that feeds on fear'
        },
        'corrupted mage': {
            'health': 40, 'damage': 20, 'exp': 60, 
            'desc': 'A once-noble mage consumed by forbidden magic'
        },
        'ghoul': {
            'health': 55, 'damage': 16, 'exp': 50, 
            'desc': 'A flesh-eating undead creature'
        },
        
        # Floors 5-6: Elemental Theme
        'fire elemental': {
            'health': 60, 'damage': 22, 'exp': 70, 
            'desc': 'A being of pure flame and rage'
        },
        'ice elemental': {
            'health': 58, 'damage': 20, 'exp': 68, 
            'desc': 'A crystalline creature radiating freezing cold'
        },
        'lightning wisp': {
            'health': 50, 'damage': 25, 'exp': 75, 
            'desc': 'Crackling energy given form'
        },
        'stone golem': {
            'health': 80, 'damage': 18, 'exp': 65, 
            'desc': 'A massive construct of animated stone'
        },
        
        # Floors 7-8: Dark Magic Theme
        'lesser demon': {
            'health': 70, 'damage': 26, 'exp': 85, 
            'desc': 'A horned creature from the abyss'
        },
        'dark cultist': {
            'health': 65, 'damage': 24, 'exp': 80, 
            'desc': 'A fanatic devoted to dark powers'
        },
        'shadow beast': {
            'health': 75, 'damage': 28, 'exp': 90, 
            'desc': 'A monstrous predator born of darkness'
        },
        'void spawn': {
            'health': 80, 'damage': 30, 'exp': 95, 
            'desc': 'An aberration from beyond reality'
        },
        
        # Floors 9-10: Ancient/Cosmic Theme
        'ancient guardian': {
            'health': 90, 'damage': 32, 'exp': 110, 
            'desc': 'An eternal sentinel of forgotten secrets'
        },
        'cosmic horror': {
            'health': 85, 'damage': 35, 'exp': 120, 
            'desc': 'An incomprehensible being from the void'
        },
        'titan spawn': {
            'health': 100, 'damage': 30, 'exp': 105, 
            'desc': 'Offspring of the primordial titans'
        },
        'celestial knight': {
            'health': 95, 'damage': 34, 'exp': 115, 
            'desc': 'A fallen warrior of the heavens'
        },
        
        # Special enemies (can appear on any floor)
        'treasure guardian': {
            'health': 60, 'damage': 20, 'exp': 65, 
            'desc': 'A magical construct protecting valuable treasure'
        }
    }
    
    # Floor themes for enemy spawning - ensures thematically appropriate encounters
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
    
    # Ten boss encounters - one per floor with progressive difficulty
    BOSSES = {
        'Arena Champion': {
            'floor': 1,
            'base_health': 120, 
            'health_scaling': 8, 
            'damage': 22, 
            'exp_reward': 150,
            'special_attack': "CHAMPION'S FURY", 
            'special_bonus': 12, 
            'stat_bonus': 2, 
            'min_level': 2
        },
        'Necromancer Lord': {
            'floor': 2,
            'base_health': 140, 
            'health_scaling': 9, 
            'damage': 24, 
            'exp_reward': 180,
            'special_attack': 'DEATH CURSE', 
            'special_bonus': 14, 
            'stat_bonus': 2, 
            'min_level': 4
        },
        'Crypt Overlord': {
            'floor': 3,
            'base_health': 160, 
            'health_scaling': 10, 
            'damage': 26, 
            'exp_reward': 210,
            'special_attack': 'SOUL DRAIN', 
            'special_bonus': 16, 
            'stat_bonus': 3, 
            'min_level': 6
        },
        'Shadow King': {
            'floor': 4,
            'base_health': 180, 
            'health_scaling': 11, 
            'damage': 28, 
            'exp_reward': 240,
            'special_attack': 'SHADOW STRIKE', 
            'special_bonus': 18, 
            'stat_bonus': 3, 
            'min_level': 8
        },
        'Flame Lord': {
            'floor': 5,
            'base_health': 200, 
            'health_scaling': 12, 
            'damage': 30, 
            'exp_reward': 270,
            'special_attack': 'INFERNO', 
            'special_bonus': 20, 
            'stat_bonus': 4, 
            'min_level': 10
        },
        'Frost Titan': {
            'floor': 6,
            'base_health': 220, 
            'health_scaling': 13, 
            'damage': 32, 
            'exp_reward': 300,
            'special_attack': 'GLACIAL STORM', 
            'special_bonus': 22, 
            'stat_bonus': 4, 
            'min_level': 12
        },
        'Demon Prince': {
            'floor': 7,
            'base_health': 240, 
            'health_scaling': 14, 
            'damage': 34, 
            'exp_reward': 330,
            'special_attack': 'HELLFIRE', 
            'special_bonus': 24, 
            'stat_bonus': 5, 
            'min_level': 14
        },
        'Void Archon': {
            'floor': 8,
            'base_health': 260, 
            'health_scaling': 15, 
            'damage': 36, 
            'exp_reward': 360,
            'special_attack': 'VOID RIFT', 
            'special_bonus': 26, 
            'stat_bonus': 5, 
            'min_level': 16
        },
        'Primordial Beast': {
            'floor': 9,
            'base_health': 280, 
            'health_scaling': 16, 
            'damage': 38, 
            'exp_reward': 390,
            'special_attack': 'ANCIENT WRATH', 
            'special_bonus': 28, 
            'stat_bonus': 6, 
            'min_level': 18
        },
        'Reality Breaker': {
            'floor': 10,
            'base_health': 300, 
            'health_scaling': 18, 
            'damage': 40, 
            'exp_reward': 450,
            'special_attack': 'COSMIC ANNIHILATION', 
            'special_bonus': 30, 
            'stat_bonus': 7, 
            'min_level': 20
        }
    }
    
    # Healing items - restore health or mana
    HEALING_ITEMS = {
        'health potion': {'heal': 30, 'type': 'health'},
        'ultimate health potion': {'heal': 'full', 'type': 'health'},
        'magic scroll': {'heal': 25, 'type': 'mana'},
        'ice crystal': {'heal': 50, 'type': 'mana'},
        'energy drink': {'heal': 20, 'type': 'health'},
        'vitality tonic': {'heal': 35, 'type': 'health'},
        'elixir of life': {'heal': 50, 'type': 'health'}
    }
    
    # Experience items - instant XP gain
    IMMEDIATE_EFFECT_ITEMS = {
        'experience gem': {'type': 'exp', 'amount': 50},
        'victory scroll': {'type': 'exp', 'amount': 75},
        'wisdom gem': {'type': 'exp', 'amount': 100},
        'frozen artifact': {'type': 'exp', 'amount': 100},
        'soul crystal': {'type': 'exp', 'amount': 150}
    }
    
    # Wearable items - permanent stat boosts
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
    
    # Quest items - used for puzzles and special interactions
    QUEST_ITEMS = [
        'rusty key', 'old map', 'legendary artifact', 'bone key', 'ancient medallion', 
        'crystal shard', 'demon seal', 'void essence', 'primordial rune'
    ]
    
    # Actionable items - items that can be "used" with special effects
    ACTIONABLE_ITEMS = {
        'rusty key': 'key',      # Opens Locked Vault
        'bone key': 'key',       # Quest item
        'torch': 'light',        # Opens Hidden Alcove secret room
        'old map': 'map',        # Shows dungeon map
        'ancient medallion': 'offering'  # Sacred Shrine offering
    }
    
    # Gold coin shop prices
    SHOP_ITEMS = {
        'health potion': 5,
        'magic scroll': 8,
        'energy drink': 6,
        'experience gem': 15,
        'armor piece': 20,
        'power ring': 25,
        'swift boots': 25,
        'elixir of life': 30,
        'soul crystal': 40
    }
    
    # Drop rate configuration
    WEAPON_DROP_CHANCE = 0.4  # 40% chance for weapon cache from enemies
    ITEM_DROP_BASE_CHANCE = 0.35  # 35% base chance for item drops
    GOLD_DROP_CHANCE = 0.6  # 60% chance for gold coins
    GOLD_DROP_MIN = 2
    GOLD_DROP_MAX = 10
    
    # Progression configuration
    BASE_EXPERIENCE_NEEDED = 100
    EXPERIENCE_MULTIPLIER = 1.4  # Reduced from 1.5 for better pacing
    MANA_PER_LEVEL = 10
    INVENTORY_SLOTS_PER_2_LEVELS = 1
    INVENTORY_SLOTS_PER_TIER = 2
    
    # Combat configuration
    BOSS_DEFEND_REDUCTION = 2  # Defending halves boss damage
    BOSS_SPECIAL_TURN_FREQUENCY = 3  # Boss uses special every 3 turns
    BOSS_SPECIAL_HEALTH_THRESHOLD = 0.5  # Boss uses special below 50% HP
    MIN_ENEMY_DAMAGE = 1  # Minimum damage from regular enemies
    MIN_BOSS_DAMAGE = 5  # Minimum damage from bosses
    MAGIC_MANA_COST = 15
    MAGIC_DAMAGE_RANGE = (10, 25)  # Random damage range for magic

#################################################################################
# PLAYER CLASS
#################################################################################
class Player:
    """
    Represents the player character with all stats, inventory, and progression.
    Handles leveling, class upgrades, inventory management, and equipment.
    """
    def __init__(self, name: str, character_class: str = "warrior"):
        self.name = name
        self.character_class = character_class
        self.class_tier = 1  # Starts at tier 1, can upgrade to 2 and 3
        self.level = 1
        self.experience = 0
        self.experience_to_next = GameConstants.BASE_EXPERIENCE_NEEDED
        self.stats = self._get_base_stats()
        self.rarity_boost = 0.0  # Increases with class tier for better loot
        
        # Health and mana
        self.health = self._get_base_health()
        self.max_health = self.health
        self.mana = self._get_base_mana()
        self.max_mana = self.mana
        
        # Inventory system
        self.inventory: List[str] = []
        self.inventory_weapons: List[Dict] = []  # Stored weapons
        self.weapon: Optional[Dict] = None  # Currently equipped weapon
        self.wearables: List[Dict] = []  # Equipped wearable items
        self.max_inventory = self._calculate_max_inventory()
        
        # Location tracking
        self.current_floor = 1
        self.current_room = "start"
        self.visited_rooms: Set[str] = set()
        
        # Progression tracking
        self.boss_defeated = False
        self.bosses_defeated: List[str] = []
        
        # Economy and special states
        self.gold_coins = 0
        self.secret_room_unlocked = False  # Track if secret vault is unlocked

    def _get_base_health(self) -> int:
        """Calculate base health based on class and tier"""
        config = GameConstants.CLASSES[self.character_class]
        base = config['base_health']
        tier_bonus = (self.class_tier - 1) * 30
        return base + tier_bonus

    def _get_base_mana(self) -> int:
        """Calculate base mana based on class and tier"""
        config = GameConstants.CLASSES[self.character_class]
        base = config['base_mana']
        tier_bonus = (self.class_tier - 1) * 25
        return base + tier_bonus

    def _get_base_stats(self) -> Dict[str, int]:
        """Calculate base stats based on class and tier"""
        config = GameConstants.CLASSES[self.character_class]
        stats = config['base_stats'].copy()
        tier_bonus = (self.class_tier - 1) * 5
        for stat in stats:
            stats[stat] += tier_bonus
        return stats

    def _calculate_max_inventory(self) -> int:
        """Calculate maximum inventory slots based on level and tier"""
        config = GameConstants.CLASSES[self.character_class]
        base = config['inventory_slots']
        level_bonus = (self.level - 1) // 2  # +1 slot every 2 levels
        tier_bonus = (self.class_tier - 1) * GameConstants.INVENTORY_SLOTS_PER_TIER
        return base + level_bonus + tier_bonus

    def _get_health_per_level(self) -> int:
        """Get health gain per level for this class"""
        config = GameConstants.CLASSES[self.character_class]
        return config['health_per_level']

    def get_class_title(self) -> str:
        """Get the current class title (e.g., 'Berserker' for tier 2 warrior)"""
        return GameConstants.CLASS_NAMES[self.class_tier][self.character_class]

    def can_upgrade_class(self) -> bool:
        """Check if player can upgrade their class tier"""
        if self.class_tier >= 3:
            return False
        next_upgrade_level = GameConstants.CLASS_UPGRADE_LEVELS[self.class_tier - 1]
        return self.level >= next_upgrade_level

    def get_next_class_title(self) -> str:
        """Get the name of the next class tier"""
        if self.class_tier >= 3:
            return "Max Level Reached"
        return GameConstants.CLASS_NAMES[self.class_tier + 1][self.character_class]

    def upgrade_class(self) -> bool:
        """
        Upgrade player's class tier (e.g., Warrior -> Berserker)
        Grants significant bonuses to stats, health, mana, and loot quality
        """
        if not self.can_upgrade_class():
            return False
        
        self.class_tier += 1
        self.rarity_boost += GameConstants.RARITY_BOOST_PER_TIER
        new_title = self.get_class_title()
        
        # Record old values for display
        old_max_health = self.max_health
        old_max_mana = self.max_mana
        
        # Recalculate base values with new tier
        self.max_health = self._get_base_health() + (self.level - 1) * self._get_health_per_level()
        self.max_mana = self._get_base_mana() + (self.level - 1) * GameConstants.MANA_PER_LEVEL
        self.stats = self._get_base_stats()
        self._apply_accumulated_level_bonuses()
        
        # Full heal on upgrade
        self.health = self.max_health
        self.mana = self.max_mana
        
        health_gained = self.max_health - old_max_health
        mana_gained = self.max_mana - old_max_mana
        
        print(f"\n*** CLASS UPGRADE! You are now a {new_title}!")
        print(f"All stats increased by 5!")
        print(f"Health increased by {health_gained} (now {self.max_health})")
        print(f"Mana increased by {mana_gained} (now {self.max_mana})")
        print(f"Rarity spawn boost increased to {self.rarity_boost * 100}%!")
        print("You have been fully healed!")
        return True

    def gain_experience(self, amount: int) -> None:
        """
        Add experience and handle level ups
        Multiple level ups can occur from single experience gain
        """
        self.experience += amount
        print(f"You gained {amount} experience!")
        
        # Handle multiple level ups
        while self.experience >= self.experience_to_next:
            self._level_up()

    def _level_up(self) -> None:
        """
        Handle leveling up the player
        Increases stats, health, mana, and inventory capacity
        """
        self.experience -= self.experience_to_next
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * GameConstants.EXPERIENCE_MULTIPLIER)
        
        old_max_inventory = self.max_inventory
        self.max_inventory = self._calculate_max_inventory()
        
        health_gain = self._get_health_per_level()
        self._apply_single_level_bonuses()
        
        self.max_health += health_gain
        self.max_mana += GameConstants.MANA_PER_LEVEL
        
        # Full heal on level up
        self.health = self.max_health
        self.mana = self.max_mana
        
        print(f"\n*** LEVEL UP! You are now level {self.level}!")
        print(f"Health increased by {health_gain} (now {self.max_health})")
        print(f"Mana increased by {GameConstants.MANA_PER_LEVEL} (now {self.max_mana})")
        if self.max_inventory > old_max_inventory:
            print(f"Inventory capacity increased! ({old_max_inventory} -> {self.max_inventory} slots)")
        print("You have been fully healed!")

    def _apply_single_level_bonuses(self) -> None:
        """Apply stat bonuses for a single level up"""
        if self.character_class == 'warrior':
            self.stats['strength'] += 3
            self.stats['agility'] += 1
            self.stats['intelligence'] += 1
        elif self.character_class == 'mage':
            self.stats['intelligence'] += 3
            self.stats['strength'] += 1
            self.stats['agility'] += 1
        else:  # rogue
            self.stats['agility'] += 3
            self.stats['strength'] += 1
            self.stats['intelligence'] += 1

    def _apply_accumulated_level_bonuses(self) -> None:
        """Apply all accumulated level bonuses (used during class upgrade)"""
        level_bonus = self.level - 1
        if self.character_class == 'warrior':
            self.stats['strength'] += level_bonus * 3
            self.stats['agility'] += level_bonus
            self.stats['intelligence'] += level_bonus
        elif self.character_class == 'mage':
            self.stats['intelligence'] += level_bonus * 3
            self.stats['strength'] += level_bonus
            self.stats['agility'] += level_bonus
        else:  # rogue
            self.stats['agility'] += level_bonus * 3
            self.stats['strength'] += level_bonus
            self.stats['intelligence'] += level_bonus

    def add_item(self, item: str) -> bool:
        """Add item to inventory if space available"""
        if len(self.inventory) >= self.max_inventory:
            print(f"X Your inventory is full! ({self.max_inventory} slots)")
            print("Use 'discard <item>' to make space.")
            return False
        self.inventory.append(item)
        print(f"You picked up: {item}")
        return True

    def add_weapon_to_inventory(self, weapon: Dict) -> bool:
        """Store a weapon in inventory for later use"""
        if len(self.inventory) >= self.max_inventory:
            print(f"X Your inventory is full! ({self.max_inventory} slots)")
            print("Cannot store weapon.")
            return False
        self.inventory_weapons.append(weapon)
        self.inventory.append(f"WEAPON: {weapon['name']}")
        print(f"You stored weapon: {weapon['name']}")
        return True

    def remove_item(self, item: str) -> bool:
        """Remove item from inventory"""
        if item not in self.inventory:
            return False
        
        # Handle weapon removal
        if item.startswith("WEAPON:"):
            weapon_name = item[8:]
            for i, weapon in enumerate(self.inventory_weapons):
                if weapon['name'] == weapon_name:
                    self.inventory_weapons.pop(i)
                    break
        
        self.inventory.remove(item)
        return True

    def can_add_item(self) -> bool:
        """Check if there's space in inventory"""
        return len(self.inventory) < self.max_inventory

    def get_inventory_count(self) -> int:
        """Get current number of items in inventory"""
        return len(self.inventory)

    def discard_item(self, item_name: str) -> bool:
        """Discard an item from inventory"""
        for item in self.inventory:
            if item.lower() == item_name.lower() or item_name.lower() in item.lower():
                self.remove_item(item)
                print(f"You discarded: {item}")
                return True
        print(f"You don't have '{item_name}' in your inventory.")
        return False

    def use_healing_item(self, item_name: Optional[str] = None) -> bool:
        """
        Use a healing item from inventory
        Can target specific item or show menu to choose
        """
        healing_items = GameConstants.HEALING_ITEMS
        
        if item_name:
            # Try to use specific item
            if item_name in self.inventory and item_name in healing_items:
                return self._apply_healing_effect(item_name, healing_items[item_name])
            print(f"You don't have '{item_name}' or it's not a healing item.")
            return False
        
        # Show menu of available healing items
        available = [item for item in self.inventory if item in healing_items]
        if not available:
            print("You don't have any healing items!")
            return False
        
        print("Available healing items:")
        for i, item in enumerate(available, 1):
            effect = healing_items[item]
            heal_text = "full heal" if effect['heal'] == 'full' else f"+{effect['heal']}"
            print(f"{i}. {item} ({heal_text} {effect['type']})")
        
        try:
            choice = int(input("Choose item to use (number): ")) - 1
            if 0 <= choice < len(available):
                chosen = available[choice]
                return self._apply_healing_effect(chosen, healing_items[chosen])
            print("Invalid choice.")
            return False
        except (ValueError, KeyboardInterrupt):
            print("Action cancelled.")
            return False

    def _apply_healing_effect(self, item_name: str, effect: Dict) -> bool:
        """Apply the healing effect of an item"""
        self.inventory.remove(item_name)
        
        if effect['type'] == 'health':
            if effect['heal'] == 'full':
                heal_amount = self.max_health - self.health
                self.health = self.max_health
                print(f"+ You are fully healed! (+{heal_amount} health)")
            else:
                heal_amount = min(effect['heal'], self.max_health - self.health)
                self.health += heal_amount
                print(f"+ You heal for {heal_amount} health!")
        elif effect['type'] == 'mana':
            mana_amount = min(effect['heal'], self.max_mana - self.mana)
            self.mana += mana_amount
            print(f"+ Your mana is restored! (+{mana_amount} mana)")
        
        return True

    def use_exp_item(self, item_name: Optional[str] = None) -> bool:
        """
        Use an experience item from inventory
        Can target specific item or show menu to choose
        """
        exp_items = GameConstants.IMMEDIATE_EFFECT_ITEMS
        
        if item_name:
            # Try to use specific item
            if item_name in self.inventory and item_name in exp_items:
                effect = exp_items[item_name]
                self.gain_experience(effect['amount'])
                self.inventory.remove(item_name)
                return True
            print(f"You don't have '{item_name}' or it's not an experience item.")
            return False
        
        # Show menu of available experience items
        available = [item for item in self.inventory if item in exp_items]
        if not available:
            print("You don't have any experience items!")
            return False
        
        print("Available experience items:")
        for i, item in enumerate(available, 1):
            effect = exp_items[item]
            print(f"{i}. {item} (+{effect['amount']} exp)")
        
        try:
            choice = int(input("Choose item to use (number): ")) - 1
            if 0 <= choice < len(available):
                chosen = available[choice]
                effect = exp_items[chosen]
                self.gain_experience(effect['amount'])
                self.inventory.remove(chosen)
                return True
            print("Invalid choice.")
            return False
        except (ValueError, KeyboardInterrupt):
            print("Action cancelled.")
            return False

    def equip_wearable(self, item: str) -> None:
        """Equip a wearable item for permanent stat boost"""
        if item in GameConstants.WEARABLE_ITEMS:
            effect = GameConstants.WEARABLE_ITEMS[item]
            self.stats[effect['stat']] += effect['bonus']
            self.wearables.append({
                'item': item, 
                'stat': effect['stat'], 
                'bonus': effect['bonus']
            })
            print(f"*** Equipped {item}! +{effect['bonus']} to {effect['stat']}.")
        else:
            print(f"{item} is not wearable.")

    def equip_weapon(self, weapon: Dict) -> None:
        """Equip a weapon"""
        self.weapon = weapon
        print(f"You equipped: {weapon['name']}")

    def switch_weapon(self, weapon_identifier: Optional[str] = None) -> bool:
        """
        Switch to a different weapon from inventory
        Can specify weapon name or show menu to choose
        """
        if not self.inventory_weapons:
            print("You don't have any spare weapons!")
            return False
        
        target_weapon = None
        
        if weapon_identifier:
            # Try to find weapon by name
            for weapon in self.inventory_weapons:
                if weapon_identifier.lower() in weapon['name'].lower() or \
                   weapon_identifier.lower() in weapon.get('base_name', '').lower():
                    target_weapon = weapon
                    break
            
            if not target_weapon:
                print(f"You don't have a weapon matching '{weapon_identifier}'.")
                return False
        else:
            # Show menu of available weapons
            print("Available weapons:")
            for i, weapon in enumerate(self.inventory_weapons, 1):
                print(f"{i}. {weapon['name']} ({weapon['damage']} damage)")
            
            try:
                choice = int(input("Choose weapon to equip (number): ")) - 1
                if 0 <= choice < len(self.inventory_weapons):
                    target_weapon = self.inventory_weapons[choice]
                else:
                    print("Invalid choice.")
                    return False
            except (ValueError, KeyboardInterrupt):
                print("Action cancelled.")
                return False
        
        # Store current weapon and equip new one
        if self.weapon:
            self.inventory_weapons.append(self.weapon)
            self.inventory.append(f"WEAPON: {self.weapon['name']}")
            print(f"You unequip your {self.weapon['name']}")
        
        self.inventory_weapons.remove(target_weapon)
        self.inventory.remove(f"WEAPON: {target_weapon['name']}")
        self.weapon = target_weapon
        print(f"You equip: {target_weapon['name']}")
        print(f"Damage: {target_weapon['damage']} | Rarity: {target_weapon.get('rarity', 'common').title()}")
        return True

    def show_stats(self) -> None:
        """Display full character sheet"""
        weapon_name = self.weapon['name'] if self.weapon else "None"
        weapon_damage = f" ({self.weapon['damage']} damage)" if self.weapon else ""
        class_title = self.get_class_title()
        
        print(f"\n=== {self.name} the {class_title} ===")
        print(f"Class Tier: {self.class_tier}/3")
        print(f"Level: {self.level}")
        print(f"Experience: {self.experience}/{self.experience_to_next}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Mana: {self.mana}/{self.max_mana}")
        print(f"Gold Coins: {self.gold_coins}")
        print(f"Weapon: {weapon_name}{weapon_damage}")
        print(f"Strength: {self.stats['strength']}")
        print(f"Intelligence: {self.stats['intelligence']}")
        print(f"Agility: {self.stats['agility']}")
        print(f"Inventory: {self.get_inventory_count()}/{self.max_inventory} slots")
        print(f"Current Floor: {self.current_floor}/{GameConstants.NUM_FLOORS}")
        print(f"Current Room: {self.current_room}")
        print(f"Bosses Defeated: {len(self.bosses_defeated)}/{GameConstants.NUM_FLOORS}")
        
        if self.wearables:
            print("\nWearables:")
            for w in self.wearables:
                print(f" - {w['item']}: +{w['bonus']} {w['stat']}")
        
        if self.can_upgrade_class():
            print(f"\n*** CLASS UPGRADE AVAILABLE! You can advance to {self.get_next_class_title()}!")
            print("Use 'upgrade' command to upgrade your class.")

    def show_status_summary(self) -> None:
        """Display quick status summary"""
        weapon_name = self.weapon['name'] if self.weapon else "None"
        print(f"\n[Floor {self.current_floor}] Health: {self.health}/{self.max_health} | Mana: {self.mana}/{self.max_mana} | Weapon: {weapon_name}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize player state for saving"""
        return {
            'name': self.name,
            'character_class': self.character_class,
            'class_tier': self.class_tier,
            'level': self.level,
            'experience': self.experience,
            'experience_to_next': self.experience_to_next,
            'stats': self.stats,
            'health': self.health,
            'max_health': self.max_health,
            'mana': self.mana,
            'max_mana': self.max_mana,
            'inventory': self.inventory,
            'inventory_weapons': self.inventory_weapons,
            'weapon': self.weapon,
            'wearables': self.wearables,
            'max_inventory': self.max_inventory,
            'current_floor': self.current_floor,
            'current_room': self.current_room,
            'visited_rooms': list(self.visited_rooms),
            'boss_defeated': self.boss_defeated,
            'bosses_defeated': self.bosses_defeated,
            'rarity_boost': self.rarity_boost,
            'gold_coins': self.gold_coins,
            'secret_room_unlocked': self.secret_room_unlocked
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Deserialize player state from save file"""
        player = cls(data['name'], data['character_class'])
        player.class_tier = data.get('class_tier', 1)
        player.level = data['level']
        player.experience = data['experience']
        player.experience_to_next = data['experience_to_next']
        player.stats = data['stats']
        player.health = data['health']
        player.max_health = data['max_health']
        player.mana = data['mana']
        player.max_mana = data['max_mana']
        player.inventory = data['inventory']
        player.inventory_weapons = data.get('inventory_weapons', [])
        player.weapon = data['weapon']
        player.wearables = data.get('wearables', [])
        player.max_inventory = data.get('max_inventory', player._calculate_max_inventory())
        player.current_floor = data.get('current_floor', 1)
        player.current_room = data['current_room']
        player.visited_rooms = set(data.get('visited_rooms', []))
        player.boss_defeated = data.get('boss_defeated', False)
        player.bosses_defeated = data.get('bosses_defeated', [])
        player.rarity_boost = data.get('rarity_boost', 0.0)
        player.gold_coins = data.get('gold_coins', 0)
        player.secret_room_unlocked = data.get('secret_room_unlocked', False)
        
        # Re-apply wearable bonuses
        for wearable in player.wearables:
            player.stats[wearable['stat']] += wearable['bonus']
        
        return player

#################################################################################
# ROOM CLASS
#################################################################################
class Room:
    """
    Represents a single room in the dungeon
    Contains items, enemies, exits, and descriptions
    """
    def __init__(self, name: str, description: str, floor: int, 
                 items: Optional[List[str]] = None,
                 exits: Optional[Dict[str, str]] = None, 
                 enemies: Optional[List[str]] = None,
                 atmosphere: Optional[str] = None):
        self.name = name
        self.description = description
        self.floor = floor
        self.items = items or []
        self.exits = exits or {}
        self.enemies = enemies or []
        self.visited = False
        self.atmosphere = atmosphere or ""

    def describe(self) -> None:
        """
        Display room description with enhanced atmospheric text
        Shows enemies with their descriptions on first visit
        """
        if not self.visited:
            print(f"\n{self.description}")
            if self.atmosphere:
                print(f"{self.atmosphere}")
            self.visited = True
        else:
            print(f"\nYou are in {self.name}")
        
        # Display enemies with descriptions
        if self.enemies:
            print(f"\n*** ENEMIES PRESENT:")
            for enemy in self.enemies:
                enemy_info = GameConstants.ENEMIES.get(enemy.lower())
                if enemy_info:
                    print(f"  - {enemy}: {enemy_info['desc']}")
                else:
                    print(f"  - {enemy}")
        
        if self.items:
            print(f"\nItems here: {', '.join(self.items)}")
        if self.exits:
            print(f"Exits: {', '.join(self.exits.keys())}")

#################################################################################
# ROOM TEMPLATES
#################################################################################
class RoomTemplates:
    """
    Centralized room template definitions
    Provides themed rooms based on floor progression
    """
    
    @staticmethod
    def get_themed_room_templates(floor: int) -> List[Dict[str, Any]]:
        """
        Returns room templates themed for specific floor
        Each floor has unique atmosphere and enemy types
        """
        templates = []
        
        # Floors 1-2: Dungeon/Prison Theme
        if floor <= 2:
            templates.extend([
                {
                    'name': "Damp Prison Cell",
                    'description': "Rusted bars line the walls of this forgotten cell. Water drips from cracked stone.",
                    'atmosphere': "The air is thick with the stench of decay and despair.",
                    'items': ['rusty key', 'health potion'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Guard Barracks",
                    'description': "Overturned bunks and scattered weapons suggest a hasty retreat.",
                    'atmosphere': "Bloodstains on the floor tell a grim tale.",
                    'items': ['weapon cache', 'armor piece'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Torture Chamber",
                    'description': "Chains hang from the ceiling. Ancient implements of pain line the walls.",
                    'atmosphere': "Echoes of past suffering seem to whisper in the darkness.",
                    'items': ['cursed amulet', 'bone key'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Sewage Tunnel",
                    'description': "Putrid water flows through channels in the floor.",
                    'atmosphere': "The stench is overwhelming. Rats scurry in the shadows.",
                    'items': ['energy drink', 'torch'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                }
            ])
        
        # Floors 3-4: Crypt/Necromancy Theme
        elif floor <= 4:
            templates.extend([
                {
                    'name': "Ancient Crypt",
                    'description': "Stone sarcophagi line the walls, their lids cracked and displaced.",
                    'atmosphere': "An unnatural chill fills the air as the dead stir restlessly.",
                    'items': ['soul crystal', 'weapon cache'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Necromancer's Study",
                    'description': "Forbidden tomes and ritual circles cover every surface.",
                    'atmosphere': "Dark energy crackles around ancient spell books.",
                    'items': ['magic scroll', 'arcane pendant'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Burial Chamber",
                    'description': "Rows of burial niches stretch into the darkness.",
                    'atmosphere': "The dead do not rest peacefully here.",
                    'items': ['health potion', 'wisdom gem'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Ossuary",
                    'description': "Bones are stacked floor to ceiling in intricate patterns.",
                    'atmosphere': "The bones seem to shift and rearrange when you're not looking.",
                    'items': ['bone key', 'cursed amulet'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                }
            ])
        
        # Floors 5-6: Elemental Theme
        elif floor <= 6:
            templates.extend([
                {
                    'name': "Inferno Chamber",
                    'description': "Waves of heat emanate from pools of bubbling lava.",
                    'atmosphere': "The very air shimmers with intense heat.",
                    'items': ['weapon cache', 'elixir of life'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Frozen Cavern",
                    'description': "Icicles the size of spears hang from the ceiling.",
                    'atmosphere': "Your breath freezes instantly in the frigid air.",
                    'items': ['ice crystal', 'frozen artifact'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Storm Hall",
                    'description': "Lightning arcs between metal pillars in this charged chamber.",
                    'atmosphere': "Static electricity makes your hair stand on end.",
                    'items': ['magic scroll', 'power ring'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Elemental Nexus",
                    'description': "All four elements clash in chaotic harmony here.",
                    'atmosphere': "Fire, ice, lightning, and stone war for dominance.",
                    'items': ['weapon cache', 'titan gauntlet'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                }
            ])
        
        # Floors 7-8: Dark Magic Theme
        elif floor <= 8:
            templates.extend([
                {
                    'name': "Ritual Chamber",
                    'description': "Blasphemous symbols cover every inch of floor and wall.",
                    'atmosphere': "Reality seems to warp and twist at the edges of your vision.",
                    'items': ['demon seal', 'weapon cache'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Shadow Realm Gate",
                    'description': "A portal to darkness pulses with malevolent energy.",
                    'atmosphere': "Whispers from beyond beckon you closer.",
                    'items': ['shadow cloak', 'soul crystal'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Corrupted Sanctum",
                    'description': "What was once a holy place now serves darker powers.",
                    'atmosphere': "Desecrated altars radiate profane energy.",
                    'items': ['weapon cache', 'ultimate health potion'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Abyssal Pit",
                    'description': "A bottomless chasm yawns before you, bridged by bone.",
                    'atmosphere': "Screams echo up from unfathomable depths.",
                    'items': ['demon seal', 'arcane pendant'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                }
            ])
        
        # Floors 9-10: Ancient/Cosmic Theme
        else:
            templates.extend([
                {
                    'name': "Primordial Vault",
                    'description': "Ancient stone predating civilization stretches endlessly upward.",
                    'atmosphere': "The weight of eons presses down upon you.",
                    'items': ['primordial rune', 'titan gauntlet'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Cosmic Observatory",
                    'description': "Stars that shouldn't exist shine through impossible windows.",
                    'atmosphere': "Your mind struggles to comprehend the geometry of this place.",
                    'items': ['weapon cache', 'wisdom gem'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Hall of Eternity",
                    'description': "Time flows strangely in this ageless corridor.",
                    'atmosphere': "Past, present, and future seem to overlap here.",
                    'items': ['soul crystal', 'legendary artifact'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                },
                {
                    'name': "Reality Fracture",
                    'description': "The laws of physics break down in this impossible space.",
                    'atmosphere': "You see things that cannot be and yet are.",
                    'items': ['void essence', 'ultimate health potion'],
                    'enemies': RoomTemplates._get_themed_enemies(floor, 2)
                }
            ])
        
        # Common rooms for all floors with special mechanics
        templates.extend([
            {
                'name': "Long Hallway",
                'description': "A long corridor stretches before you, lit by flickering torches.",
                'atmosphere': "Shadows dance menacingly on the walls.",
                'items': ['torch', 'weapon cache'],
                'enemies': RoomTemplates._get_themed_enemies(floor, 2)
            },
            {
                'name': "Treasure Room",
                'description': "Glittering wealth fills this chamber, but it's well guarded.",
                'atmosphere': "Gold and gems reflect torchlight in dazzling patterns.",
                'items': ['golden coin', 'weapon cache', 'experience gem'],
                'enemies': ['treasure guardian'] + RoomTemplates._get_themed_enemies(floor, 1)
            },
            {
                'name': "Hidden Alcove",
                'description': "A dark alcove with a single torch sconce on the wall.",
                'atmosphere': "The sconce looks like it could hold a torch. Something feels hidden here.",
                'items': ['torch'],
                'enemies': RoomTemplates._get_themed_enemies(floor, 1),
                'has_secret': True  # Marker for puzzle interaction
            },
            {
                'name': "Sacred Shrine",
                'description': "An ancient shrine with a stone altar in the center.",
                'atmosphere': "The altar has a circular indentation. Strange energy emanates from it.",
                'items': ['health potion', 'golden coin'],
                'enemies': RoomTemplates._get_themed_enemies(floor, 1),
                'has_altar': True  # Marker for medallion puzzle
            },
            {
                'name': "Locked Vault",
                'description': "A sealed vault with an ornate chest at its center.",
                'atmosphere': "The chest has an old rusty keyhole. It hasn't been opened in centuries.",
                'items': ['weapon cache', 'golden coin'],
                'enemies': ['treasure guardian'] + RoomTemplates._get_themed_enemies(floor, 1),
                'has_locked_chest': True  # Marker for key puzzle
            }
        ])
        
        return templates
    
    @staticmethod
    def get_secret_room_template() -> Dict[str, Any]:
        """
        Returns the template for the secret treasure vault
        Unlocked by using torch in Hidden Alcove
        """
        return {
            'name': "Secret Treasure Vault",
            'description': "A hidden vault glitters with treasures! Ancient magic protected this place.",
            'atmosphere': "Countless riches await those clever enough to find this place.",
            'items': [
                'weapon cache', 'weapon cache', 'ultimate health potion', 
                'experience gem', 'wisdom gem', 'legendary artifact'
            ],
            'enemies': []
        }
    
    @staticmethod
    def _get_themed_enemies(floor: int, count: int) -> List[str]:
        """
        Get unique themed enemies for a floor
        Ensures no duplicate enemies in a single room
        """
        available = GameConstants.FLOOR_THEMES.get(floor, ['goblin'])
        # Ensure we get unique enemies
        selected = []
        available_copy = available.copy()
        random.shuffle(available_copy)
        
        for enemy in available_copy:
            if enemy not in selected:
                selected.append(enemy)
                if len(selected) >= count:
                    break
        
        return selected

    @staticmethod
    def get_boss_room(floor: int) -> Dict[str, Any]:
        """
        Returns boss room template for specified floor
        Each floor has a unique boss with themed arena
        """
        boss_rooms = {
            1: {
                'name': "Gladiator Arena",
                'description': "A massive circular arena with sand-covered floors.",
                'atmosphere': "Ghostly cheers echo from unseen crowds. The Arena Champion awaits!",
                'items': ["champion's prize", 'victory scroll'],
                'enemies': ['Arena Champion']
            },
            2: {
                'name': "Necromancer's Sanctum",
                'description': "Dark energy swirls around an obsidian throne.",
                'atmosphere': "Death itself seems to bow before the Necromancer Lord!",
                'items': ['soul crystal', 'ultimate health potion'],
                'enemies': ['Necromancer Lord']
            },
            3: {
                'name': "Tomb of the Overlord",
                'description': "A vast crypt dominated by a massive stone sarcophagus.",
                'atmosphere': "Ancient power radiates from the awakening Crypt Overlord!",
                'items': ['legendary artifact', 'weapon cache'],
                'enemies': ['Crypt Overlord']
            },
            4: {
                'name': "Shadow Throne Room",
                'description': "Darkness coalesces into a throne of pure shadow.",
                'atmosphere': "The Shadow King emerges from the void itself!",
                'items': ['shadow cloak', 'wisdom gem'],
                'enemies': ['Shadow King']
            },
            5: {
                'name': "Infernal Throne",
                'description': "Rivers of lava flow around a platform of volcanic rock.",
                'atmosphere': "The Flame Lord rises in a pillar of fire!",
                'items': ['weapon cache', 'elixir of life'],
                'enemies': ['Flame Lord']
            },
            6: {
                'name': "Frozen Cavern",
                'description': "A bone-chilling cavern covered in ancient ice.",
                'atmosphere': "The Frost Titan awakens from its eternal slumber!",
                'items': ['ice crystal', 'frozen artifact'],
                'enemies': ['Frost Titan']
            },
            7: {
                'name': "Abyssal Gate",
                'description': "A massive portal to the demonic realm dominates this chamber.",
                'atmosphere': "The Demon Prince steps through from the abyss!",
                'items': ['demon seal', 'ultimate health potion'],
                'enemies': ['Demon Prince']
            },
            8: {
                'name': "Void Nexus",
                'description': "Reality fractures and bends around this impossible space.",
                'atmosphere': "The Void Archon manifests from nothingness!",
                'items': ['void essence', 'soul crystal'],
                'enemies': ['Void Archon']
            },
            9: {
                'name': "Primordial Chamber",
                'description': "Ancient stone predating time itself forms this vast arena.",
                'atmosphere': "The Primordial Beast, older than the world, awakens!",
                'items': ['primordial rune', 'titan gauntlet'],
                'enemies': ['Primordial Beast']
            },
            10: {
                'name': "Reality's Edge",
                'description': "The fabric of existence itself unravels in this final chamber.",
                'atmosphere': "The Reality Breaker threatens to unmake all creation!",
                'items': ['legendary artifact', 'ultimate health potion'],
                'enemies': ['Reality Breaker']
            }
        }
        return boss_rooms.get(floor, boss_rooms[1])

#################################################################################
# WEAPON SYSTEM
#################################################################################
class WeaponSystem:
    """
    Handles weapon generation, rarity calculation, and special weapons
    """
    
    @staticmethod
    def get_rarity_multiplier(rarity: str) -> float:
        """Get damage multiplier for weapon rarity"""
        return GameConstants.WEAPON_RARITIES[rarity]['multiplier']

    @classmethod
    def generate_random_weapon(cls, player: 'Player', force_rarity: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a random weapon appropriate for player's class and level
        Can force a specific rarity for boss drops
        Chance to generate ultra-rare Golden Gun
        """
        # Check for Golden Gun drop (unless rarity is forced)
        if not force_rarity and random.random() < GameConstants.GOLDEN_GUN_DROP_RATE:
            return cls._create_golden_gun()
        
        # Calculate rarity based on level and class tier
        rarity = force_rarity or cls._calculate_rarity_by_level(player.level, player.rarity_boost)
        
        # Get allowed weapon types for player's class
        allowed_types = GameConstants.CLASSES[player.character_class]['weapon_types']
        weapon_type = random.choice(allowed_types)
        
        # Generate weapon name
        material = random.choice(GameConstants.WEAPON_MATERIALS[rarity])
        weapon_name = random.choice(GameConstants.WEAPON_TYPES[weapon_type])
        
        # Calculate damage
        base_damage = random.randint(8, 15) + (player.level * 2)
        rarity_multiplier = cls.get_rarity_multiplier(rarity)
        final_damage = int(base_damage * rarity_multiplier)
        
        full_name = f"{material} {weapon_name}"
        
        return {
            'name': full_name,
            'damage': final_damage,
            'type': weapon_type,
            'rarity': rarity,
            'base_name': full_name
        }

    @classmethod
    def _calculate_rarity_by_level(cls, player_level: int, rarity_boost: float = 0.0) -> str:
        """
        Calculate weapon rarity based on player level and rarity boost
        Higher level = better chance for rare weapons
        """
        boost = int(rarity_boost * 100)
        
        # Rarity chances scale with level
        rarity_chances = {
            'common': max(50 - (player_level * 2) - boost, 10),
            'uncommon': min(25 + player_level, 35),
            'rare': min(15 + (player_level // 2) + (boost // 3), 25),
            'epic': min(8 + (player_level // 3) + (boost // 3), 15),
            'legendary': min(2 + (player_level // 4) + (boost // 3), 8),
            'mythic': min(player_level // 6 + (boost // 3), 2)
        }
        
        # Normalize to 100%
        total = sum(rarity_chances.values())
        if total != 100:
            adjustment = 100 - total
            rarity_chances['common'] += adjustment
        
        # Roll for rarity
        rand = random.randint(1, 100)
        cumulative = 0
        for rarity, chance in rarity_chances.items():
            cumulative += chance
            if rand <= cumulative:
                return rarity
        
        return 'common'

    @classmethod
    def _create_golden_gun(cls) -> Dict[str, Any]:
        """
        Create the ultra-rare Golden Gun
        Instant kill weapon with 6 uses
        """
        chosen_name = random.choice(GameConstants.GOLDEN_GUN_NAMES)
        return {
            'name': f"*** {chosen_name}",
            'damage': 99999,
            'type': 'divine',
            'rarity': 'divine',
            'base_name': chosen_name,
            'uses_remaining': 6,
            'max_uses': 6,
            'special': 'instant_kill'
        }

    @classmethod
    def create_starting_weapons(cls) -> Dict[str, List[Dict[str, Any]]]:
        """Create starting weapon options for each class"""
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
    """
    Handles all combat logic including regular enemies and boss fights
    """
    
    def __init__(self, game: 'Game'):
        self.game = game

    def fight_regular_enemy(self, enemy_name: str, player: Player, room: Room) -> bool:
        """
        Handle combat with a regular enemy
        Returns False if player dies, True if player wins or combat ends
        """
        enemy_stats = GameConstants.ENEMIES.get(enemy_name.lower(), None)
        if not enemy_stats:
            print(f"Unknown enemy: {enemy_name}")
            return True
        
        enemy_health = enemy_stats['health']
        enemy_damage = enemy_stats['damage']
        
        print(f"\n*** You engage the {enemy_name} in combat!")
        print(f"Enemy: {enemy_stats['desc']}")
        
        # Combat loop
        while enemy_health > 0 and player.health > 0:
            # Player attacks
            damage = self._calculate_player_damage(player)
            enemy_health -= damage
            weapon_display = player.weapon.get('base_name', player.weapon['name']) if player.weapon else 'fists'
            print(f"You strike with your {weapon_display} for {damage} damage!")
            
            if enemy_health <= 0:
                print(f"*** You defeated the {enemy_name}!")
                room.enemies.remove(enemy_name)
                player.gain_experience(enemy_stats['exp'])
                self._handle_enemy_drops(enemy_name, room, player)
                return True
            
            # Enemy attacks
            enemy_hit = self._calculate_enemy_damage(enemy_damage, player)
            player.health -= enemy_hit
            print(f"The {enemy_name} hits you for {enemy_hit} damage!")
            
            if player.health <= 0:
                print("*** You have been defeated!")
                print("Game Over! Try loading a saved game or starting over.")
                return False
        
        return True

    def _calculate_player_damage(self, player: Player) -> int:
        """
        Calculate damage dealt by player
        Handles Golden Gun instant kill mechanic
        """
        # Check for Golden Gun
        if player.weapon and player.weapon.get('special') == 'instant_kill' and player.weapon.get('uses_remaining', 0) > 0:
            player.weapon['uses_remaining'] -= 1
            remaining = player.weapon['uses_remaining']
            print(f"*** THE {player.weapon['base_name'].upper()} FIRES!")
            print(f"*** INSTANT OBLITERATION!")
            print(f"Uses remaining: {remaining}/6")
            
            if remaining <= 0:
                print(f"The {player.weapon['base_name']} crumbles to dust after its final shot...")
                player.weapon = None
                print("! You are now unarmed! Find a new weapon!")
            
            return 99999
        
        # No weapon = weak fist attack
        if not player.weapon:
            return random.randint(1, 5)
        
        # Calculate weapon damage with strength bonus
        base_damage = player.weapon['damage']
        strength_bonus = random.randint(1, player.stats['strength'] // 3)
        weapon_rarity = player.weapon.get('rarity', 'common')
        rarity_multiplier = WeaponSystem.get_rarity_multiplier(weapon_rarity)
        
        return int((base_damage + strength_bonus) * rarity_multiplier)

    def _calculate_enemy_damage(self, base_damage: int, player: Player) -> int:
        """
        Calculate damage dealt by enemy
        Agility reduces incoming damage
        """
        agility_defense = random.randint(1, player.stats['agility'] // 3)
        final_damage = base_damage - agility_defense
        return max(GameConstants.MIN_ENEMY_DAMAGE, final_damage)

    def _handle_enemy_drops(self, enemy_name: str, room: Room, player: Player) -> None:
        """
        Handle item drops when enemy is defeated
        Drop rates scale with weapon rarity
        """
        weapon_rarity = player.weapon.get('rarity', 'common') if player.weapon else 'common'
        rarity_multiplier = WeaponSystem.get_rarity_multiplier(weapon_rarity)
        drop_chance = GameConstants.ITEM_DROP_BASE_CHANCE + (rarity_multiplier * 0.1)
        
        # Gold coin drops
        if random.random() < GameConstants.GOLD_DROP_CHANCE:
            coins = random.randint(GameConstants.GOLD_DROP_MIN, GameConstants.GOLD_DROP_MAX)
            player.gold_coins += coins
            print(f"The {enemy_name} dropped {coins} gold coins!")
        
        # Item drops
        if random.random() < drop_chance:
            if random.random() < GameConstants.WEAPON_DROP_CHANCE:
                print(f"+ The {enemy_name} dropped a weapon cache!")
                room.items.append("weapon cache")
            else:
                # Class-specific item drops
                if player.character_class == 'mage':
                    drops = ["health potion", "magic scroll", "ice crystal"]
                else:  # warrior or rogue
                    drops = ["health potion", "energy drink", "vitality tonic", "power ring", "swift boots"]
                dropped_item = random.choice(drops)
                room.items.append(dropped_item)
                print(f"The {enemy_name} dropped: {dropped_item}")

    def fight_boss(self, boss_name: str, player: Player, room: Room) -> bool:
        """
        Handle boss fight encounter
        Returns False if player dies, True if player wins
        """
        print("\n" + "="*60)
        print(f"*** BOSS FIGHT: {boss_name.upper()}!")
        print("="*60)
        
        boss_config = GameConstants.BOSSES[boss_name]
        
        # Check level recommendation
        if player.level < boss_config['min_level']:
            print(f"! WARNING: Recommended level {boss_config['min_level']}+!")
            try:
                choice = input("Fight anyway? (y/n): ").strip().lower()
                if choice not in ['y', 'yes']:
                    return True
            except KeyboardInterrupt:
                return True
        
        success = self._execute_boss_fight(boss_name, boss_config, player)
        
        if success:
            room.enemies.remove(boss_name)
            player.bosses_defeated.append(boss_name)
            self._award_boss_rewards(player, boss_name, boss_config)
        
        return success

    def _execute_boss_fight(self, boss_name: str, boss_config: Dict, player: Player) -> bool:
        """
        Execute the boss fight combat loop
        Bosses have special attacks and health-based mechanics
        """
        # Calculate boss health with scaling
        boss_health = boss_config['base_health'] + (player.level * boss_config['health_scaling'])
        boss_max_health = boss_health
        boss_damage = boss_config['damage']
        
        print(f"\n*** The {boss_name} has {boss_health} health!")
        
        turn = 1
        while boss_health > 0 and player.health > 0:
            print(f"\n--- Turn {turn} ---")
            print(f"Your Health: {player.health}/{player.max_health}")
            print(f"{boss_name} Health: {boss_health}/{boss_max_health}")
            
            # Player turn
            player_damage, defend_mode = self._player_turn(player)
            boss_health -= player_damage
            
            if boss_health <= 0:
                break
            
            # Boss turn
            boss_attack_damage = self._boss_turn(
                boss_name, boss_config, boss_max_health, boss_health, turn, defend_mode, player
            )
            player.health -= boss_attack_damage
            
            if player.health <= 0:
                print(f"\n*** Defeated by the {boss_name}!")
                print("Game Over!")
                return False
            
            turn += 1
        
        return True

    def _player_turn(self, player: Player) -> Tuple[int, bool]:
        """
        Handle player's turn in boss fight
        Returns (damage_dealt, defend_mode)
        """
        print("\n1. Attack | 2. Magic | 3. Defend", end="")
        if any(item in GameConstants.HEALING_ITEMS for item in player.inventory):
            print(" | 4. Heal", end="")
        print()
        
        try:
            action = input("Choice: ").strip()
        except KeyboardInterrupt:
            return 0, False
        
        player_damage = 0
        defend_mode = False
        
        if action == "1":
            player_damage = self._calculate_player_damage(player)
            weapon_display = player.weapon.get('base_name', player.weapon['name']) if player.weapon else 'fists'
            print(f"*** Attack for {player_damage} damage!")
        elif action == "2":
            if player.mana >= GameConstants.MAGIC_MANA_COST:
                player.mana -= GameConstants.MAGIC_MANA_COST
                magic_damage = player.stats['intelligence'] + random.randint(*GameConstants.MAGIC_DAMAGE_RANGE)
                player_damage = magic_damage
                print(f"*** Magic for {player_damage} damage!")
            else:
                print("Not enough mana!")
                player_damage = player.weapon['damage'] if player.weapon else random.randint(1, 5)
        elif action == "3":
            defend_mode = True
            print("*** Defending!")
        elif action == "4":
            player.use_healing_item()
        
        return player_damage, defend_mode

    def _boss_turn(self, boss_name: str, boss_config: Dict, boss_max_health: int, boss_health: int,
                    turn: int, defend_mode: bool, player: Player) -> int:
        """
        Handle boss's turn in combat
        Bosses use special attacks when below health threshold
        """
        boss_damage = boss_config['damage']
        
        # Check if boss should use special attack
        use_special = (boss_health < boss_max_health * GameConstants.BOSS_SPECIAL_HEALTH_THRESHOLD and
                       turn % GameConstants.BOSS_SPECIAL_TURN_FREQUENCY == 0)
        
        if use_special:
            special_damage = boss_damage + boss_config['special_bonus']
            if defend_mode:
                special_damage //= GameConstants.BOSS_DEFEND_REDUCTION
            print(f"*** {boss_config['special_attack']}! {special_damage} damage!")
            return special_damage
        else:
            normal_damage = boss_damage + random.randint(1, 10)
            agility_defense = random.randint(1, player.stats['agility'] // 2)
            final_damage = normal_damage - agility_defense
            if defend_mode:
                final_damage //= GameConstants.BOSS_DEFEND_REDUCTION
            final_damage = max(GameConstants.MIN_BOSS_DAMAGE, final_damage)
            print(f"*** Boss attacks for {final_damage} damage!")
            return final_damage

    def _award_boss_rewards(self, player: Player, boss_name: str, boss_config: Dict) -> None:
        """
        Award rewards for defeating a boss
        Includes legendary weapon, experience, stats, and full heal
        """
        print("\n" + "="*60)
        print("*** VICTORY!")
        print("="*60)
        
        player.gain_experience(boss_config['exp_reward'])
        
        # Award boss-specific legendary weapon
        boss_weapon = self._get_boss_weapon(boss_name, player.character_class)
        print(f"\n*** Legendary Reward: {boss_weapon['name']}!")
        print(f"Damage: {boss_weapon['damage']} | Rarity: {boss_weapon['rarity'].title()}")
        player.equip_weapon(boss_weapon)
        
        # Full heal
        player.health = player.max_health
        player.mana = player.max_mana
        
        # Permanent stat boost
        stat_bonus = boss_config['stat_bonus']
        for stat in player.stats:
            player.stats[stat] += stat_bonus
        
        print(f"\n*** All stats increased by {stat_bonus}!")
        print("*** Fully healed!")

    def _get_boss_weapon(self, boss_name: str, char_class: str) -> Dict:
        """
        Get the legendary weapon for defeating a specific boss
        Each boss has unique weapons for each class
        """
        # Complete boss weapon definitions for all 10 bosses and 3 classes
        weapons = {
            'Arena Champion': {
                'warrior': {'name': 'Gladius of Victory', 'damage': 32},
                'mage': {'name': "Champion's Scepter", 'damage': 28},
                'rogue': {'name': 'Twin Blades of Honor', 'damage': 30}
            },
            'Necromancer Lord': {
                'warrior': {'name': 'Soul Reaper', 'damage': 35},
                'mage': {'name': 'Death Staff', 'damage': 32},
                'rogue': {'name': 'Shadow Fang', 'damage': 33}
            },
            'Crypt Overlord': {
                'warrior': {'name': 'Bone Crusher', 'damage': 38},
                'mage': {'name': 'Crypt Scepter', 'damage': 35},
                'rogue': {'name': 'Grave Shiv', 'damage': 36}
            },
            'Shadow King': {
                'warrior': {'name': 'Shadowbane', 'damage': 41},
                'mage': {'name': 'Dark Orb', 'damage': 38},
                'rogue': {'name': 'Night Piercer', 'damage': 39}
            },
            'Flame Lord': {
                'warrior': {'name': 'Flamebringer', 'damage': 44},
                'mage': {'name': 'Inferno Staff', 'damage': 41},
                'rogue': {'name': 'Cinder Bow', 'damage': 42}
            },
            'Frost Titan': {
                'warrior': {'name': 'Frostbane Greatsword', 'damage': 47},
                'mage': {'name': 'Staff of Eternal Winter', 'damage': 44},
                'rogue': {'name': 'Icicle Piercer', 'damage': 45}
            },
            'Demon Prince': {
                'warrior': {'name': "Demon's Edge", 'damage': 50},
                'mage': {'name': 'Abyssal Staff', 'damage': 47},
                'rogue': {'name': 'Soul Piercer', 'damage': 48}
            },
            'Void Archon': {
                'warrior': {'name': 'Voidreaver', 'damage': 53},
                'mage': {'name': 'Reality Staff', 'damage': 50},
                'rogue': {'name': 'Oblivion Blade', 'damage': 51}
            },
            'Primordial Beast': {
                'warrior': {'name': 'Titan Slayer', 'damage': 56},
                'mage': {'name': 'Primordial Staff', 'damage': 53},
                'rogue': {'name': 'Beast Fang', 'damage': 54}
            },
            'Reality Breaker': {
                'warrior': {'name': 'Worldender', 'damage': 60},
                'mage': {'name': 'Cosmos Staff', 'damage': 57},
                'rogue': {'name': 'Reality Ripper', 'damage': 58}
            }
        }
        
        weapon_data = weapons.get(boss_name, {}).get(char_class, {'name': 'Legendary Blade', 'damage': 35})
        weapon_type = GameConstants.CLASSES[char_class]['weapon_types'][0]
        
        return {
            'name': weapon_data['name'],
            'damage': weapon_data['damage'],
            'type': weapon_type,
            'rarity': 'legendary',
            'base_name': weapon_data['name']
        }

#################################################################################
# COMMAND HANDLER
#################################################################################
class CommandHandler:
    """
    Handles command parsing and execution with fuzzy matching
    """
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.commands = {
            'help': self.game.show_help,
            'look': self.game.look_around,
            'go': self.game.move,
            'north': lambda: self.game.move('north'),
            'south': lambda: self.game.move('south'),
            'east': lambda: self.game.move('east'),
            'west': lambda: self.game.move('west'),
            'up': lambda: self.game.move('up'),
            'down': lambda: self.game.move('down'),
            'take': self.game.take_item,
            'get': self.game.take_item,
            'takeall': self.game.take_all_items,
            'inventory': self.game.show_inventory,
            'inv': self.game.show_inventory,
            'stats': self.game.show_stats,
            'status': self.game.show_stats,
            'fight': self.game.fight_enemy,
            'attack': self.game.fight_enemy,
            'upgrade': self.game.upgrade_class_command,
            'heal': self.game.use_healing,
            'experience': self.game.use_experience,
            'exp': self.game.use_experience,
            'equip': self.game.equip_wearable_command,
            'wear': self.game.equip_wearable_command,
            'switch': self.game.switch_weapon,
            'discard': self.game.discard_item,
            'drop': self.game.discard_item,
            'use': self.game.use_item,
            'shop': self.game.open_shop,
            'map': self.game.show_map,
            'save': self.game.save_game,
            'load': self.game.load_game,
            'quit': self.game.quit_game,
            'exit': self.game.quit_game
        }

    def process(self, user_input: str) -> None:
        """
        Process user command with fuzzy matching for typos
        Suggests corrections for misspelled commands
        """
        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Try fuzzy matching if command not found
        if command not in self.commands:
            matches = get_close_matches(command, self.commands.keys(), n=1, cutoff=0.6)
            if matches:
                print(f"Did you mean '{matches[0]}'?")
                command = matches[0]
            else:
                print("Unknown command. Type 'help' for commands.")
                return
        
        try:
            if args:
                self.commands[command](*args)
            else:
                self.commands[command]()
        except Exception as e:
            logging.error(f"Command error: {str(e)}")
            print(f"Error: {e}")

#################################################################################
# GAME CLASS
#################################################################################
class Game:
    """
    Main game controller
    Handles world generation, game loop, and high-level game logic
    """
    
    def __init__(self):
        self.player: Optional[Player] = None
        self.floors: Optional[Dict[int, Dict[str, Room]]] = None
        self.running = True
        self.weapons = WeaponSystem.create_starting_weapons()
        self.combat = CombatSystem(self)
        self.save_file = GameConstants.SAVE_FILE
        self.command_handler = CommandHandler(self)

    def start_game(self) -> None:
        """Initialize and start the game"""
        print("=" * 50)
        print(" TEXT ADVENTURE RPG - 10 FLOOR EDITION")
        print(f" Version {GameConstants.VERSION}")
        print("=" * 50)
        print("\n1. New Game | 2. Load Game")
        
        while True:
            try:
                choice = input("Choice: ").strip()
                if choice == '1':
                    self.create_new_character()
                    break
                elif choice == '2':
                    if self.load_game():
                        break
                    print("No save found. Starting new game...")
                    self.create_new_character()
                    break
            except KeyboardInterrupt:
                print("\nInterrupted.")
        
        print("\nType 'help' for commands.")
        self.look_around()
        self.game_loop()

    def game_loop(self) -> None:
        """Main game loop - processes commands until game ends"""
        while self.running:
            try:
                user_input = input("\n> ").strip().lower()
                if not user_input:
                    continue
                self.command_handler.process(user_input)
                if self.player:
                    self.player.show_status_summary()
            except KeyboardInterrupt:
                print("\n\nInterrupted. Save before quitting!")
                break
            except Exception as e:
                logging.error(str(e))
                print(f"Error: {e}")

    def create_new_character(self) -> None:
        """Create a new player character"""
        try:
            name = input("Character name: ").strip()
            if not name:
                name = "Adventurer"
            
            character_class = self._choose_character_class()
            self.player = Player(name, character_class)
            
            starting_weapon = self._choose_starting_weapon()
            self.player.equip_weapon(starting_weapon)
            
            self.floors = self._create_multi_floor_dungeon()
            
            print(f"\nWelcome, {self.player.name} the {character_class.title()}!")
            print(f"Weapon: {starting_weapon['base_name']}")
            print(f"{GameConstants.NUM_FLOORS} floors await. Good luck!")
        except Exception as e:
            logging.error(f"Creation error: {str(e)}")
            self.player = Player("Adventurer", "warrior")
            self.floors = self._create_multi_floor_dungeon()

    def _choose_character_class(self) -> str:
        """Let player choose their class"""
        print("\n=== Choose Class ===")
        print("1. Warrior - High HP, strength-based")
        print("2. Mage - High mana, intelligence-based")
        print("3. Rogue - Balanced, agility-based")
        
        while True:
            try:
                choice = input("Choice (1-3): ").strip()
                class_map = {'1': 'warrior', '2': 'mage', '3': 'rogue'}
                if choice in class_map:
                    return class_map[choice]
                print("Invalid choice. Enter 1, 2, or 3.")
            except KeyboardInterrupt:
                print("\nDefaulting to Warrior...")
                return 'warrior'

    def _choose_starting_weapon(self) -> Dict[str, Any]:
        """Let player choose starting weapon"""
        print("\n=== Choose Weapon ===")
        class_weapons = self.weapons[self.player.character_class]
        
        for i, weapon in enumerate(class_weapons, 1):
            print(f"{i}. {weapon['name']} - {weapon['damage']} dmg")
        
        while True:
            try:
                choice = input("Choice (1-3): ").strip()
                if choice in ['1', '2', '3']:
                    return class_weapons[int(choice) - 1].copy()
                print("Invalid choice. Enter 1, 2, or 3.")
            except (ValueError, KeyboardInterrupt):
                print("\nDefaulting to first weapon...")
                return class_weapons[0].copy()

    def _create_multi_floor_dungeon(self) -> Dict[int, Dict[str, Room]]:
        """
        Generate the complete 10-floor dungeon
        Each floor has themed rooms and enemies
        """
        print("\n*** Generating 10-floor dungeon...")
        floors = {}
        
        for floor_num in range(1, GameConstants.NUM_FLOORS + 1):
            print(f"Floor {floor_num}...", end=" ")
            num_rooms = random.randint(GameConstants.MIN_ROOMS_PER_FLOOR, GameConstants.MAX_ROOMS_PER_FLOOR)
            floor_rooms = {}
            
            # Create start room
            if floor_num == 1:
                start_room_id = 'start'
                floor_rooms[start_room_id] = Room(
                    "Entrance Hall",
                    "You stand at the entrance of a vast dungeon.",
                    floor_num,
                    items=['rusty key', 'health potion'],
                    enemies=[],
                    atmosphere="Adventure awaits in the depths below."
                )
            else:
                start_room_id = f"floor{floor_num}_start"
                floor_rooms[start_room_id] = Room(
                    f"Floor {floor_num} Entrance",
                    f"You arrive at floor {floor_num}. The atmosphere grows darker.",
                    floor_num,
                    items=['health potion'],
                    enemies=[]
                )
            
            # Add themed rooms
            templates = RoomTemplates.get_themed_room_templates(floor_num)
            selected = random.sample(templates, min(num_rooms - 2, len(templates)))
            
            for i, template in enumerate(selected):
                room_id = f"floor{floor_num}_room{i+1}"
                floor_rooms[room_id] = Room(
                    template['name'],
                    template['description'],
                    floor_num,
                    items=self._filter_items_by_class(template['items'].copy()),
                    enemies=template.get('enemies', []).copy(),
                    atmosphere=template.get('atmosphere', '')
                )
            
            # Add boss room
            boss_template = RoomTemplates.get_boss_room(floor_num)
            boss_room_id = f"floor{floor_num}_boss"
            floor_rooms[boss_room_id] = Room(
                boss_template['name'],
                boss_template['description'],
                floor_num,
                items=self._filter_items_by_class(boss_template['items'].copy()),
                enemies=boss_template['enemies'].copy(),
                atmosphere=boss_template.get('atmosphere', '')
            )
            
            # Add stairs (except last floor)
            if floor_num < GameConstants.NUM_FLOORS:
                stairs_id = f"floor{floor_num}_stairs"
                floor_rooms[stairs_id] = Room(
                    "Ancient Stairway",
                    "Stone stairs descend deeper.",
                    floor_num,
                    items=[],
                    enemies=[]
                )
            
            # Connect all rooms
            self._connect_rooms_properly(floor_rooms, start_room_id)
            
            floors[floor_num] = floor_rooms
            print(f"{len(floor_rooms)} rooms")
        
        # Connect stairs between floors
        for floor_num in range(1, GameConstants.NUM_FLOORS):
            stairs_id = f"floor{floor_num}_stairs"
            next_start = f"floor{floor_num+1}_start"
            
            if stairs_id in floors[floor_num] and next_start in floors.get(floor_num + 1, {}):
                floors[floor_num][stairs_id].exits['down'] = next_start
                floors[floor_num + 1][next_start].exits['up'] = stairs_id
        
        print("*** Dungeon complete!")
        return floors
    
    def _filter_items_by_class(self, items: List[str]) -> List[str]:
        """
        Replace mana items with class-appropriate alternatives for non-mages
        Mages keep magic scrolls and ice crystals, others get health items
        """
        if self.player.character_class == 'mage':
            return items
        
        # For warriors and rogues, replace mana items
        mana_items = ['magic scroll', 'ice crystal', 'mana flower']
        replacements = {
            'magic scroll': random.choice(['energy drink', 'vitality tonic']),
            'ice crystal': random.choice(['power ring', 'swift boots']),
            'mana flower': random.choice(['leather bracer', 'armor piece'])
        }
        
        return [replacements.get(item, item) for item in items]
    
    def _connect_rooms_properly(self, rooms: Dict[str, Room], start_id: str) -> None:
        """
        Connect all rooms in a floor ensuring all are reachable
        Creates a connected graph with some loops for non-linear exploration
        """
        directions = ['north', 'south', 'east', 'west']
        reverse = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        
        room_ids = list(rooms.keys())
        connected = {start_id}
        unconnected = set(room_ids) - connected
        
        # Connect all rooms to the graph
        while unconnected:
            current = random.choice(list(connected))
            target = random.choice(list(unconnected))
            
            # Find available direction
            available_dirs = [d for d in directions if d not in rooms[current].exits]
            if not available_dirs:
                continue
            
            direction = random.choice(available_dirs)
            
            # Create bidirectional connection
            rooms[current].exits[direction] = target
            rooms[target].exits[reverse[direction]] = current
            
            connected.add(target)
            unconnected.remove(target)
        
        # Add extra connections for loops (about 33% more connections)
        extra_connections = len(room_ids) // 3
        for _ in range(extra_connections):
            room1, room2 = random.sample(room_ids, 2)
            
            # Skip if already connected
            if room2 in rooms[room1].exits.values():
                continue
            
            # Find available directions
            available_dirs = [d for d in directions if d not in rooms[room1].exits]
            if available_dirs:
                direction = random.choice(available_dirs)
                
                # Only connect if room2 also has space
                if reverse[direction] not in rooms[room2].exits:
                    rooms[room1].exits[direction] = room2
                    rooms[room2].exits[reverse[direction]] = room1

    def get_current_room(self) -> Room:
        """Get the room the player is currently in"""
        return self.floors[self.player.current_floor][self.player.current_room]

    def show_help(self) -> None:
        """
        Display context-aware help showing only relevant commands
        Adapts to current situation (combat, items, etc.)
        """
        room = self.get_current_room()
        
        print("\n" + "="*40)
        print("COMMANDS")
        print("="*40)
        
        # Always show basic commands
        print("look - Examine room")
        print("go <dir> - Move (north/south/east/west/up/down)")
        print("  shortcuts: n, s, e, w, up, down")
        
        # Combat commands if enemies present
        if room.enemies:
            print("fight/attack <enemy> - Combat")
        
        # Item commands if items present or in inventory
        if room.items or self.player.inventory:
            print("take <item> - Pick up item")
            if room.items and len(room.items) > 1:
                print("takeall - Pick up all")
        
        # Inventory commands
        print("inventory/inv - Show items")
        print("stats/status - Show character")
        
        # Conditional commands based on inventory
        if any(item in GameConstants.HEALING_ITEMS for item in self.player.inventory):
            print("heal - Use healing item")
        if any(item in GameConstants.IMMEDIATE_EFFECT_ITEMS for item in self.player.inventory):
            print("exp - Use experience item")
        if any(item in GameConstants.WEARABLE_ITEMS for item in self.player.inventory):
            print("equip/wear - Equip item")
        if any(item in GameConstants.ACTIONABLE_ITEMS for item in self.player.inventory):
            print("use <item> - Use special items (torch, keys, etc.)")
        if self.player.inventory_weapons:
            print("switch [weapon] - Change weapon")
        if self.player.inventory:
            print("discard <item> - Drop item")
        
        # Gold/shop only if player has gold
        if self.player.gold_coins > 0:
            print("shop - Merchant (spend gold)")
        
        # Upgrade only if available
        if self.player.can_upgrade_class():
            print("upgrade - Advance class")
        
        # System commands
        print("map - View dungeon")
        print("save/load - Save/Load")
        print("quit/exit - Quit game")
        print("="*40)

    def look_around(self) -> None:
        """Examine current room and mark as visited"""
        current_room = self.get_current_room()
        current_room.describe()
        self.player.visited_rooms.add(self.player.current_room)

    def move(self, direction: str) -> None:
        """
        Move player in specified direction
        Handles floor transitions and boss blocking
        """
        current_room = self.get_current_room()
        
        if direction not in current_room.exits:
            print("Can't go that way!")
            return
        
        next_room_id = current_room.exits[direction]
        
        # Check if trying to descend without defeating boss
        if direction == 'down':
            boss_for_floor = self._get_boss_for_floor(self.player.current_floor)
            if boss_for_floor and boss_for_floor not in self.player.bosses_defeated:
                print(f"! Blocked! Defeat {boss_for_floor} first!")
                return
        
        # Handle floor transitions
        if direction in ['down', 'up'] and 'floor' in next_room_id:
            next_floor = int(next_room_id.split('_')[0].replace('floor', ''))
            if next_floor != self.player.current_floor:
                self.player.current_floor = next_floor
                print(f"→ Floor {self.player.current_floor}")
        
        # Move to new room
        self.player.current_room = next_room_id
        self.player.visited_rooms.add(next_room_id)
        print(f"You go {direction}.")
        self.look_around()
    
    def _get_boss_for_floor(self, floor: int) -> Optional[str]:
        """Get the boss name for specified floor"""
        for boss_name, boss_config in GameConstants.BOSSES.items():
            if boss_config['floor'] == floor:
                return boss_name
        return None

    def show_map(self) -> None:
        """Display dungeon map showing visited rooms"""
        print("\n" + "="*40)
        print("DUNGEON MAP")
        print("="*40)
        print(f"Floor {self.player.current_floor}/{GameConstants.NUM_FLOORS}")
        
        for floor_num in range(1, GameConstants.NUM_FLOORS + 1):
            floor_rooms = self.floors[floor_num]
            visited_on_floor = [r for r in self.player.visited_rooms if r in floor_rooms]
            
            print(f"\n--- Floor {floor_num} ---")
            print(f"Discovered: {len(visited_on_floor)}/{len(floor_rooms)}")
            
            if visited_on_floor:
                # Show first 5 rooms
                for room_id in sorted(visited_on_floor)[:5]:
                    room = floor_rooms[room_id]
                    marker = ">>>" if (floor_num == self.player.current_floor and 
                                      room_id == self.player.current_room) else "---"
                    print(f" {marker} {room.name}")
                
                if len(visited_on_floor) > 5:
                    print(f" ... and {len(visited_on_floor) - 5} more rooms")
        
        total_visited = len(self.player.visited_rooms)
        total_rooms = sum(len(floor_rooms) for floor_rooms in self.floors.values())
        print(f"\nTotal: {total_visited}/{total_rooms} rooms")
        print("="*40)

    def show_inventory(self) -> None:
        """Display organized inventory"""
        print(f"\n=== INVENTORY ({self.player.get_inventory_count()}/{self.player.max_inventory}) ===")
        
        if self.player.weapon:
            print(f"Equipped: {self.player.weapon['name']} ({self.player.weapon['damage']} dmg)")
        
        if not self.player.inventory:
            print("Empty")
            return
        
        # Organize items by category
        healing = [i for i in self.player.inventory if i in GameConstants.HEALING_ITEMS]
        exp = [i for i in self.player.inventory if i in GameConstants.IMMEDIATE_EFFECT_ITEMS]
        wearables = [i for i in self.player.inventory if i in GameConstants.WEARABLE_ITEMS]
        actionable = [i for i in self.player.inventory if i in GameConstants.ACTIONABLE_ITEMS]
        weapons = [i for i in self.player.inventory if i.startswith("WEAPON:")]
        other = [i for i in self.player.inventory if i not in healing and i not in exp and 
                i not in wearables and i not in actionable and not i.startswith("WEAPON:")]
        
        if healing:
            print("\nHealing:")
            for item in healing:
                print(f"  - {item}")
        
        if exp:
            print("\nExperience:")
            for item in exp:
                print(f"  - {item}")
        
        if wearables:
            print("\nWearables:")
            for item in wearables:
                print(f"  - {item}")
        
        if actionable:
            print("\nSpecial Items:")
            for item in actionable:
                print(f"  - {item}")
        
        if weapons:
            print("\nWeapons:")
            for w in weapons:
                print(f"  - {w[8:]}")
        
        if other:
            print("\nOther:")
            for item in other:
                print(f"  - {item}")

    def show_stats(self) -> None:
        """Display full character stats"""
        self.player.show_stats()

    def use_healing(self, *args) -> None:
        """Use a healing item"""
        item_name = ' '.join(args) if args else None
        self.player.use_healing_item(item_name)

    def use_experience(self, *args) -> None:
        """Use an experience item"""
        item_name = ' '.join(args) if args else None
        self.player.use_exp_item(item_name)

    def equip_wearable_command(self, *args) -> None:
        """Equip a wearable item"""
        if not args:
            wearables = [i for i in self.player.inventory if i in GameConstants.WEARABLE_ITEMS]
            if not wearables:
                print("No wearable items!")
                return
            
            print("Available wearables:")
            for i, item in enumerate(wearables, 1):
                effect = GameConstants.WEARABLE_ITEMS[item]
                print(f"{i}. {item} (+{effect['bonus']} {effect['stat']})")
            
            try:
                choice = int(input("Choose (1-{}): ".format(len(wearables)))) - 1
                if 0 <= choice < len(wearables):
                    item = wearables[choice]
                    self.player.inventory.remove(item)
                    self.player.equip_wearable(item)
                else:
                    print("Invalid choice.")
            except (ValueError, KeyboardInterrupt):
                print("Cancelled.")
        else:
            item_name = ' '.join(args)
            if item_name in self.player.inventory:
                self.player.inventory.remove(item_name)
                self.player.equip_wearable(item_name)
            else:
                print(f"You don't have '{item_name}'.")

    def switch_weapon(self, *args) -> None:
        """Switch equipped weapon"""
        weapon_identifier = ' '.join(args) if args else None
        self.player.switch_weapon(weapon_identifier)

    def discard_item(self, *args) -> None:
        """Discard an item from inventory"""
        if not args:
            print("Discard what? Usage: discard <item name>")
            return
        item_name = ' '.join(args)
        self.player.discard_item(item_name)

    def take_item(self, *args) -> None:
        """Pick up an item from the room"""
        if not args:
            print("Take what? Usage: take <item name>")
            return
        
        current_room = self.get_current_room()
        
        # Check if enemies present - items locked during combat
        if current_room.enemies:
            print("! Defeat enemies first!")
            print(f"Enemies: {', '.join(current_room.enemies)}")
            return
        
        item = ' '.join(args)
        
        if item not in current_room.items:
            print(f"No '{item}' here.")
            if current_room.items:
                print(f"Available: {', '.join(current_room.items)}")
            return
        
        # Check inventory space (except for wearables which auto-equip)
        if not self.player.can_add_item() and item not in GameConstants.WEARABLE_ITEMS:
            print(f"Inventory full! ({self.player.max_inventory} slots)")
            print("Use 'discard <item>' to make space.")
            return
        
        current_room.items.remove(item)
        
        # Handle special item types
        if item == "weapon cache":
            self._handle_weapon_cache()
        elif item == "champion's prize":
            self._handle_champions_prize()
        else:
            self._handle_regular_item(item)

    def take_all_items(self) -> None:
        """Pick up all items in the room"""
        current_room = self.get_current_room()
        
        if current_room.enemies:
            print("! Defeat enemies first!")
            return
        
        if not current_room.items:
            print("No items here.")
            return
        
        items_taken = 0
        items_left = []
        
        for item in current_room.items[:]:
            if item in GameConstants.WEARABLE_ITEMS or self.player.can_add_item():
                current_room.items.remove(item)
                if item == "weapon cache":
                    self._handle_weapon_cache()
                elif item == "champion's prize":
                    self._handle_champions_prize()
                else:
                    self._handle_regular_item(item)
                items_taken += 1
            else:
                items_left.append(item)
        
        if items_taken:
            print(f"\n+ Picked up {items_taken} item(s)")
        if items_left:
            print(f"X Inventory full! Left behind: {', '.join(items_left)}")

    def _handle_weapon_cache(self) -> None:
        """Handle opening a weapon cache"""
        new_weapon = WeaponSystem.generate_random_weapon(self.player)
        
        print(f"+ Weapon: {new_weapon['name']}")
        print(f"  {new_weapon['damage']} dmg | {new_weapon['rarity'].title()}")
        
        # Check if it's the Golden Gun
        if new_weapon.get('special') == 'instant_kill':
            print("\n*** LEGENDARY GOLDEN GUN FOUND! ***")
            print("*** 6 INSTANT KILLS! ***")
        
        # Offer to equip if better than current
        if not self.player.weapon or new_weapon['damage'] > self.player.weapon['damage']:
            try:
                choice = input("Equip? (y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    if self.player.weapon:
                        print(f"Replaced {self.player.weapon['name']}")
                    self.player.equip_weapon(new_weapon)
                else:
                    self.player.add_weapon_to_inventory(new_weapon)
            except KeyboardInterrupt:
                self.player.add_weapon_to_inventory(new_weapon)
        else:
            try:
                choice = input("Weaker weapon. Take anyway? (y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    self.player.add_weapon_to_inventory(new_weapon)
                else:
                    print("Left weapon behind.")
            except KeyboardInterrupt:
                print("Left weapon behind.")

    def _handle_champions_prize(self) -> None:
        """Handle opening champion's prize (guaranteed epic/legendary)"""
        prize = WeaponSystem.generate_random_weapon(
            self.player, random.choice(['epic', 'legendary'])
        )
        
        print(f"*** Champion's Prize: {prize['name']}")
        print(f"  {prize['damage']} dmg | {prize['rarity'].title()}")
        
        try:
            choice = input("Equip? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                if self.player.weapon:
                    print(f"Replaced {self.player.weapon['name']}")
                self.player.equip_weapon(prize)
            else:
                self.player.add_weapon_to_inventory(prize)
        except KeyboardInterrupt:
            self.player.add_weapon_to_inventory(prize)

    def _handle_regular_item(self, item: str) -> None:
        """Handle picking up a regular item"""
        # Immediate effect items (experience)
        if item in GameConstants.IMMEDIATE_EFFECT_ITEMS:
            effect = GameConstants.IMMEDIATE_EFFECT_ITEMS[item]
            if effect['type'] == 'exp':
                self.player.gain_experience(effect['amount'])
            return
        
        # Gold coins
        if item == 'golden coin':
            coins = random.randint(3, 10)
            self.player.gold_coins += coins
            print(f"Collected {coins} gold coins!")
            return
        
        # Wearable items
        if item in GameConstants.WEARABLE_ITEMS:
            self.player.inventory.append(item)
            print(f"Picked up: {item} (wearable)")
            return
        
        # All other items
        self.player.add_item(item)

    def use_item(self, *args) -> None:
        """
        Use special interactive items (torch, keys, medallion)
        These items have puzzle-like interactions with specific rooms
        """
        if not args:
            print("Use what? Usage: use <item name>")
            return
        
        item_name = ' '.join(args)
        
        if item_name not in self.player.inventory:
            print(f"You don't have '{item_name}'.")
            return
        
        if item_name not in GameConstants.ACTIONABLE_ITEMS:
            print(f"You can't use '{item_name}' like that.")
            print("Try: 'heal', 'exp', or 'equip' for other items.")
            return
        
        action_type = GameConstants.ACTIONABLE_ITEMS[item_name]
        current_room = self.get_current_room()
        
        # TORCH - Opens secret room in Hidden Alcove
        if action_type == 'light' and item_name == 'torch':
            if 'Hidden Alcove' in current_room.name and not self.player.secret_room_unlocked:
                print("\n*** You place the torch in the wall sconce...")
                print("The flame flares brightly with an otherworldly glow!")
                print("You hear a grinding sound as a hidden door slides open!")
                
                self.player.secret_room_unlocked = True
                self.player.inventory.remove('torch')
                
                # Add secret room
                secret_room_id = f"floor{self.player.current_floor}_secret"
                current_room.exits['secret'] = secret_room_id
                
                # Create secret room if it doesn't exist
                if secret_room_id not in self.floors[self.player.current_floor]:
                    secret_template = RoomTemplates.get_secret_room_template()
                    self.floors[self.player.current_floor][secret_room_id] = Room(
                        secret_template['name'],
                        secret_template['description'],
                        self.player.current_floor,
                        items=secret_template['items'],
                        enemies=secret_template['enemies'],
                        atmosphere=secret_template.get('atmosphere', '')
                    )
                    # Add return exit
                    self.floors[self.player.current_floor][secret_room_id].exits['out'] = self.player.current_room
                
                print("\nA SECRET exit has appeared! Use 'go secret' to enter!")
            else:
                print("You hold up the torch, illuminating the area.")
                print("Nothing unusual here. Perhaps somewhere with a torch sconce?")
        
        # RUSTY KEY - Opens Locked Vault chest
        elif action_type == 'key' and item_name == 'rusty key':
            if 'Locked Vault' in current_room.name or 'Vault' in current_room.name:
                print("\n*** You approach the ornate chest with the rusty key...")
                print("The key fits perfectly!")
                print("With a satisfying *CLICK*, the chest opens!")
                print("\n>>> The vault's treasures are revealed! <<<")
                
                self.player.inventory.remove('rusty key')
                
                # Add treasure to room
                vault_rewards = [
                    'weapon cache', 'weapon cache', 'legendary artifact', 
                    'ultimate health potion', 'experience gem', 'power ring'
                ]
                for reward in vault_rewards:
                    if reward not in current_room.items:
                        current_room.items.append(reward)
                
                print(f"\nTreasures added: {', '.join(vault_rewards)}")
                print("Use 'takeall' to collect everything!")
                print("\nThe rusty key crumbles to dust...")
            else:
                print("You examine the rusty key.")
                print("It looks like it would fit a large, ornate lock...")
        
        # BONE KEY - Flavor item
        elif action_type == 'key' and item_name == 'bone key':
            print(f"You hold the {item_name}. It's cold to the touch.")
            print("This might unlock something in the crypts...")
        
        # OLD MAP - Shows dungeon map
        elif action_type == 'map':
            print("You study the old map carefully...")
            self.show_map()
        
        # ANCIENT MEDALLION - Sacred Shrine offering for permanent stats
        elif action_type == 'offering' and item_name == 'ancient medallion':
            if 'Sacred Shrine' in current_room.name or 'Shrine' in current_room.name:
                print("\n*** You approach the ancient altar...")
                print("The medallion glows as you hold it near!")
                print("You place the ancient medallion on the altar.")
                print("\n>>> The altar erupts with brilliant light! <<<")
                print("Ancient power flows through you!")
                
                self.player.inventory.remove('ancient medallion')
                
                # Class-specific permanent stat boosts
                if self.player.character_class == 'warrior':
                    self.player.stats['strength'] += 8
                    self.player.stats['agility'] += 3
                    print(f"*** Strength +8!")
                    print(f"*** Agility +3!")
                elif self.player.character_class == 'mage':
                    self.player.stats['intelligence'] += 8
                    self.player.stats['strength'] += 3
                    print(f"*** Intelligence +8!")
                    print(f"*** Strength +3!")
                else:  # rogue
                    self.player.stats['agility'] += 8
                    self.player.stats['intelligence'] += 3
                    print(f"*** Agility +8!")
                    print(f"*** Intelligence +3!")
                
                # Bonus health and mana
                self.player.max_health += 20
                self.player.health = self.player.max_health
                self.player.max_mana += 15
                self.player.mana = self.player.max_mana
                
                print(f"*** Max health +20! (now {self.player.max_health})")
                print(f"*** Max mana +15! (now {self.player.max_mana})")
                print("*** Fully healed!")
                print("\nThe altar's power fades, but your strength remains...")
            else:
                print("You hold the ancient medallion, studying its design.")
                print("It should be placed somewhere specific...")
                print("Perhaps on an altar or shrine?")

    def open_shop(self, *args) -> None:
        """Open merchant shop to buy items with gold coins"""
        print("\n" + "="*40)
        print("*** MERCHANT ***")
        print("="*40)
        print(f"Your gold: {self.player.gold_coins}")
        
        # Filter shop items based on class
        shop_items = []
        for item, price in GameConstants.SHOP_ITEMS.items():
            # Only mages can buy magic scrolls
            if item == 'magic scroll' and self.player.character_class != 'mage':
                continue
            shop_items.append((item, price))
        
        print("\n=== SHOP ===")
        for i, (item, price) in enumerate(shop_items, 1):
            print(f"{i}. {item} - {price}g")
        print(f"{len(shop_items) + 1}. Leave")
        
        try:
            choice = input("\nBuy item (number): ").strip()
            choice_num = int(choice)
            
            if choice_num == len(shop_items) + 1:
                print("The merchant nods farewell...")
                return
            
            if 1 <= choice_num <= len(shop_items):
                item, price = shop_items[choice_num - 1]
                
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
                        print("Inventory full! Discard items first.")
                else:
                    print(f"Not enough gold! Need {price}g, have {self.player.gold_coins}g")
            else:
                print("Invalid choice.")
        except (ValueError, KeyboardInterrupt):
            print("Transaction cancelled.")
    
    def fight_enemy(self, *args) -> None:
        """Initiate combat with an enemy"""
        if not args:
            print("Fight what? Usage: fight <enemy name>")
            return
        
        input_enemy_name = ' '.join(args)
        current_room = self.get_current_room()
        
        # Find matching enemy (case-insensitive)
        matching_enemy = None
        for e in current_room.enemies:
            if e.lower() == input_enemy_name.lower():
                matching_enemy = e
                break
        
        if not matching_enemy:
            print(f"No '{input_enemy_name}' here to fight!")
            if current_room.enemies:
                print(f"Enemies present: {', '.join(current_room.enemies)}")
            return
        
        # Warn if no weapon
        if not self.player.weapon:
            print("! No weapon! Fight with fists?")
            try:
                choice = input("Continue? (y/n): ").strip().lower()
                if choice not in ['y', 'yes']:
                    return
            except KeyboardInterrupt:
                return
        
        # Check if boss fight
        boss_names = list(GameConstants.BOSSES.keys())
        if matching_enemy in boss_names:
            success = self.combat.fight_boss(matching_enemy, self.player, current_room)
        else:
            success = self.combat.fight_regular_enemy(matching_enemy, self.player, current_room)
        
        if not success:
            self.running = False

    def upgrade_class_command(self) -> None:
        """Upgrade player's class tier"""
        if not self.player.can_upgrade_class():
            if self.player.class_tier >= 3:
                print("Already at max tier!")
            else:
                next_level = GameConstants.CLASS_UPGRADE_LEVELS[self.player.class_tier - 1]
                print(f"Need level {next_level} to upgrade. (Currently level {self.player.level})")
            return
        
        current_title = self.player.get_class_title()
        next_title = self.player.get_next_class_title()
        
        print(f"\n*** CLASS UPGRADE AVAILABLE! ***")
        print(f"Current: {current_title} (Tier {self.player.class_tier})")
        print(f"Upgrade to: {next_title} (Tier {self.player.class_tier + 1})")
        print("\nBenefits:")
        print("• +5 all stats")
        print("• +30 max health")
        print("• +25 max mana")
        print("• Full heal & mana restore")
        print("• +5% better loot drops")
        
        try:
            choice = input(f"\nUpgrade to {next_title}? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                if self.player.upgrade_class():
                    print("\nClass upgrade successful!")
            else:
                print("Upgrade cancelled.")
        except KeyboardInterrupt:
            print("\nUpgrade cancelled.")

    def save_game(self) -> None:
        """Save complete game state to file"""
        try:
            save_data = {
                'version': GameConstants.VERSION,
                'player': self.player.to_dict(),
                'floors': {}
            }
            
            # Save all floor data
            for floor_num, floor_rooms in self.floors.items():
                save_data['floors'][str(floor_num)] = {
                    room_id: {
                        'items': room.items,
                        'enemies': room.enemies,
                        'visited': room.visited,
                        'exits': room.exits
                    } for room_id, room in floor_rooms.items()
                }
            
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"✓ Game saved successfully!")
        except Exception as e:
            logging.error(f"Save error: {str(e)}")
            print(f"✗ Save failed: {e}")

    def load_game(self) -> bool:
        """Load game state from save file"""
        try:
            if not os.path.exists(self.save_file):
                return False
            
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            # Version check
            if save_data.get('version') != GameConstants.VERSION:
                print(f"! Save version mismatch. Starting new game.")
                return False
            
            # Load player
            self.player = Player.from_dict(save_data['player'])
            
            # Check Golden Gun status
            if self.player.weapon and self.player.weapon.get('special') == 'instant_kill':
                if self.player.weapon.get('uses_remaining', 0) <= 0:
                    print("! Your Golden Gun has depleted...")
                    self.player.weapon = None
            
            # Reconstruct floors
            self.floors = {}
            for floor_str, floor_data in save_data['floors'].items():
                floor_num = int(floor_str)
                self.floors[floor_num] = {}
                
                for room_id, room_data in floor_data.items():
                    # Determine room type and get appropriate template
                    if room_id == 'start':
                        room_name = "Entrance Hall"
                        room_desc = "The dungeon entrance."
                        atmosphere = "Adventure awaits."
                    elif 'boss' in room_id:
                        boss_template = RoomTemplates.get_boss_room(floor_num)
                        room_name = boss_template['name']
                        room_desc = boss_template['description']
                        atmosphere = boss_template.get('atmosphere', '')
                    elif 'stairs' in room_id:
                        room_name = "Ancient Stairway"
                        room_desc = "Stone stairs descend deeper."
                        atmosphere = ""
                    elif 'secret' in room_id:
                        secret_template = RoomTemplates.get_secret_room_template()
                        room_name = secret_template['name']
                        room_desc = secret_template['description']
                        atmosphere = secret_template.get('atmosphere', '')
                    else:
                        # Use themed template
                        templates = RoomTemplates.get_themed_room_templates(floor_num)
                        if templates:
                            template = random.choice(templates)
                            room_name = template['name']
                            room_desc = template['description']
                            atmosphere = template.get('atmosphere', '')
                        else:
                            room_name = "Mysterious Room"
                            room_desc = "A dark room."
                            atmosphere = ""
                    
                    # Create room with saved data
                    self.floors[floor_num][room_id] = Room(
                        room_name,
                        room_desc,
                        floor_num,
                        items=room_data['items'],
                        exits=room_data['exits'],
                        enemies=room_data['enemies'],
                        atmosphere=atmosphere
                    )
                    self.floors[floor_num][room_id].visited = room_data['visited']
            
            print(f"✓ Welcome back, {self.player.name} the {self.player.get_class_title()}!")
            return True
            
        except Exception as e:
            logging.error(f"Load error: {str(e)}")
            print(f"✗ Load failed: {e}")
            print("Save file may be corrupted.")
            return False

    def quit_game(self) -> None:
        """Exit the game with optional save"""
        try:
            save_choice = input("\nSave before quitting? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
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
    """Main entry point for the game"""
    try:
        game = Game()
        game.start_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        print(f"\n\nFatal error: {e}")
        print("Please report this bug!")

if __name__ == "__main__":
    main()