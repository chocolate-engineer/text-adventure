"""
================================================================================
TEXT ADVENTURE RPG GAME
================================================================================
Version: 2.1.0
Author: AI Assistant
Python: 3.8+
FEATURES:
• Three character classes with 3-tier progression
• Procedurally generated dungeons (unique each playthrough)
• Six weapon rarity tiers with damage scaling
• Ultra-rare Golden Gun (0.02% drop, instant kill, 6 uses)
• Three boss encounters with strategic combat
• Level-based inventory management
• Hidden chest system unlocked by boss defeat
• Complete save/load functionality with version checking
• Interactive dungeon map
• Turn-based combat system
• Wearable items (e.g., armor piece) that boost stats without inventory cost
• Class-specific weapon spawns
• Increased rare item spawn rates on class upgrades
• Improved crash handling with logging
• New 'consume' command for healing/experience items
CLASSES:
GameConstants - Configuration and game balance values
Player - Character state and progression
Room - Dungeon locations
RoomTemplates - Centralized room definitions
WeaponSystem - Weapon generation and rarity
CombatSystem - All combat mechanics
CommandHandler - Command processing
Game - Main controller and game loop
================================================================================
"""
import random
import json
import os
import logging
from typing import Dict, List, Optional, Set, Tuple, Any

# Setup logging for crash handling
logging.basicConfig(
    filename='game.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

#################################################################################
# CONFIGURATION & CONSTANTS
#################################################################################
class GameConstants:
    """Centralized game configuration and balance values. All tunable parameters are defined here for easy adjustment."""
    # ==================== VERSION INFO ====================
    VERSION = "2.1.0"
    SAVE_FILE = "savegame.json"
    # ==================== CHARACTER CLASSES ====================
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
    # ==================== CLASS PROGRESSION ====================
    CLASS_NAMES = {
        1: {'warrior': 'Warrior', 'mage': 'Mage', 'rogue': 'Rogue'},
        2: {'warrior': 'Berserker', 'mage': 'Sorcerer', 'rogue': 'Assassin'},
        3: {'warrior': 'Paladin', 'mage': 'Archmage', 'rogue': 'Shadow Master'}
    }
    RARITY_BOOST_PER_TIER = 0.05  # 5% increase per class tier upgrade
    # ==================== WEAPON RARITY SYSTEM ====================
    WEAPON_RARITIES = {
        'common': {'multiplier': 1.0, 'color': '⚪'},
        'uncommon': {'multiplier': 1.3, 'color': '🟢'},
        'rare': {'multiplier': 1.6, 'color': '🔵'},
        'epic': {'multiplier': 2.0, 'color': '🟣'},
        'legendary': {'multiplier': 2.5, 'color': '🟡'},
        'mythic': {'multiplier': 3.0, 'color': '🔴'},
        'divine': {'multiplier': 999.0, 'color': '🌟'}  # Golden Gun only
    }
    WEAPON_TYPES = {
        'melee': ['Sword', 'Axe', 'Hammer', 'Spear', 'Blade'],
        'magic': ['Staff', 'Wand', 'Orb', 'Tome', 'Crystal'],
        'stealth': ['Dagger', 'Bow', 'Claws', 'Shiv', 'Needle']
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
    GOLDEN_GUN_DROP_RATE = 0.0002  # 0.02% chance
    # ==================== ENEMIES ====================
    ENEMIES = {
        'goblin': {'health': 25, 'damage': 8, 'exp': 25},
        'treasure guardian': {'health': 45, 'damage': 15, 'exp': 50},
        'armored skeleton': {'health': 35, 'damage': 12, 'exp': 40},
        'shadow wraith': {'health': 40, 'damage': 18, 'exp': 55},
        'corrupted mage': {'health': 30, 'damage': 20, 'exp': 60}
    }
    # ==================== BOSSES ====================
    BOSSES = {
        'Dark Lord': {
            'base_health': 150, 'health_scaling': 10, 'damage': 25, 'exp_reward': 200,
            'special_attack': 'DARK ENERGY', 'special_bonus': 15, 'stat_bonus': 3, 'min_level': 3
        },
        'Arena Champion': {
            'base_health': 120, 'health_scaling': 8, 'damage': 22, 'exp_reward': 150,
            'special_attack': "CHAMPION'S FURY", 'special_bonus': 12, 'stat_bonus': 2, 'min_level': 4
        },
        'Frost Titan': {
            'base_health': 180, 'health_scaling': 12, 'damage': 28, 'exp_reward': 250,
            'special_attack': 'GLACIAL STORM', 'special_bonus': 18, 'stat_bonus': 3, 'min_level': 5
        }
    }
    # ==================== ITEMS ====================
    HEALING_ITEMS = {
        'health potion': {'heal': 30, 'type': 'health'},
        'ultimate health potion': {'heal': 'full', 'type': 'health'},
        'magic scroll': {'heal': 25, 'type': 'mana'},
        'ice crystal': {'heal': 50, 'type': 'mana'}
    }
    IMMEDIATE_EFFECT_ITEMS = {
        'experience gem': {'type': 'exp', 'amount': 50},
        'victory scroll': {'type': 'exp', 'amount': 75},
        'wisdom gem': {'type': 'exp', 'amount': 100},
        'frozen artifact': {'type': 'exp', 'amount': 100}
    }
    WEARABLE_ITEMS = {
        'armor piece': {'stat': 'strength', 'bonus': 5},
        'cursed amulet': {'stat': 'intelligence', 'bonus': 3},
        "nature's blessing": {'stat': 'agility', 'bonus': 4},
        'healing herb': {'stat': 'agility', 'bonus': 2},  # Assuming some are wearable
        'mana flower': {'stat': 'intelligence', 'bonus': 4}
    }
    QUEST_ITEMS = [
        'rusty key', 'old map', 'legendary artifact', 'bone key', 'rope'
    ]
    # ==================== DROP RATES ====================
    WEAPON_DROP_CHANCE = 0.3  # 30% from enemies
    ITEM_DROP_BASE_CHANCE = 0.3  # 30% base drop rate
    # ==================== PROGRESSION ====================
    BASE_EXPERIENCE_NEEDED = 100
    EXPERIENCE_MULTIPLIER = 1.5
    MANA_PER_LEVEL = 10
    INVENTORY_SLOTS_PER_2_LEVELS = 1
    INVENTORY_SLOTS_PER_TIER = 2
    # ==================== COMBAT ====================
    BOSS_DEFEND_REDUCTION = 2  # Divide damage by this when defending
    BOSS_SPECIAL_TURN_FREQUENCY = 3  # Special attack every 3rd turn
    BOSS_SPECIAL_HEALTH_THRESHOLD = 0.5  # Special attacks below 50% health
    MIN_ENEMY_DAMAGE = 1
    MIN_BOSS_DAMAGE = 5
    MAGIC_MANA_COST = 15
    MAGIC_DAMAGE_RANGE = (10, 25)

#################################################################################
# PLAYER CLASS
#################################################################################
class Player:
    """Manages player character state, progression, and inventory."""
    def __init__(self, name: str, character_class: str = "warrior"):
        # ===== BASIC INFO =====
        self.name = name
        self.character_class = character_class
        self.class_tier = 1
        # ===== PROGRESSION =====
        self.level = 1
        self.experience = 0
        self.experience_to_next = GameConstants.BASE_EXPERIENCE_NEEDED
        self.stats = self._get_base_stats()
        self.rarity_boost = 0.0
        # ===== RESOURCES =====
        self.health = self._get_base_health()
        self.max_health = self.health
        self.mana = self._get_base_mana()
        self.max_mana = self.mana
        # ===== EQUIPMENT & INVENTORY =====
        self.inventory: List[str] = []
        self.inventory_weapons: List[Dict] = []
        self.weapon: Optional[Dict] = None
        self.wearables: List[Dict] = []
        self.max_inventory = self._calculate_max_inventory()
        # ===== GAME STATE =====
        self.current_room = "start"
        self.visited_rooms: Set[str] = set()
        self.boss_defeated = False
        self.first_boss_defeated = False
        self.has_rusty_key = False

    # ========== STAT CALCULATIONS ==========
    def _get_base_health(self) -> int:
        config = GameConstants.CLASSES[self.character_class]
        base = config['base_health']
        tier_bonus = (self.class_tier - 1) * 30
        return base + tier_bonus

    def _get_base_mana(self) -> int:
        config = GameConstants.CLASSES[self.character_class]
        base = config['base_mana']
        tier_bonus = (self.class_tier - 1) * 25
        return base + tier_bonus

    def _get_base_stats(self) -> Dict[str, int]:
        config = GameConstants.CLASSES[self.character_class]
        stats = config['base_stats'].copy()
        tier_bonus = (self.class_tier - 1) * 5
        for stat in stats:
            stats[stat] += tier_bonus
        return stats

    def _calculate_max_inventory(self) -> int:
        config = GameConstants.CLASSES[self.character_class]
        base = config['inventory_slots']
        level_bonus = (self.level - 1) // 2
        tier_bonus = (self.class_tier - 1) * GameConstants.INVENTORY_SLOTS_PER_TIER
        return base + level_bonus + tier_bonus

    def _get_health_per_level(self) -> int:
        config = GameConstants.CLASSES[self.character_class]
        return config['health_per_level']

    # ========== CLASS PROGRESSION ==========
    def get_class_title(self) -> str:
        return GameConstants.CLASS_NAMES[self.class_tier][self.character_class]

    def can_upgrade_class(self) -> bool:
        return self.level >= 5 and self.class_tier < 3

    def get_next_class_title(self) -> str:
        if self.class_tier >= 3:
            return "Max Level Reached"
        return GameConstants.CLASS_NAMES[self.class_tier + 1][self.character_class]

    def upgrade_class(self) -> bool:
        if not self.can_upgrade_class():
            return False
        old_title = self.get_class_title()
        self.class_tier += 1
        self.rarity_boost += GameConstants.RARITY_BOOST_PER_TIER
        new_title = self.get_class_title()
        # Recalculate all stats
        old_max_health = self.max_health
        old_max_mana = self.max_mana
        self.max_health = self._get_base_health() + (self.level - 1) * self._get_health_per_level()
        self.max_mana = self._get_base_mana() + (self.level - 1) * GameConstants.MANA_PER_LEVEL
        self.stats = self._get_base_stats()
        self._apply_accumulated_level_bonuses()
        # Full heal
        self.health = self.max_health
        self.mana = self.max_mana
        # Display results
        health_gained = self.max_health - old_max_health
        mana_gained = self.max_mana - old_max_mana
        print(f"\n🌟 CLASS UPGRADE! You are now a {new_title}!")
        print(f"Previous class: {old_title}")
        print(f"All stats increased by 5!")
        print(f"Health increased by {health_gained} (now {self.max_health})")
        print(f"Mana increased by {mana_gained} (now {self.max_mana})")
        print(f"Rarity spawn boost increased to {self.rarity_boost * 100}%!")
        print("You have been fully healed!")
        return True

    # ========== EXPERIENCE & LEVELING ==========
    def gain_experience(self, amount: int) -> None:
        self.experience += amount
        print(f"You gained {amount} experience!")
        while self.experience >= self.experience_to_next:
            self._level_up()

    def _level_up(self) -> None:
        self.experience -= self.experience_to_next
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * GameConstants.EXPERIENCE_MULTIPLIER)
        # Update inventory capacity
        old_max_inventory = self.max_inventory
        self.max_inventory = self._calculate_max_inventory()
        # Stat increases
        health_gain = self._get_health_per_level()
        self._apply_single_level_bonuses()
        self.max_health += health_gain
        self.max_mana += GameConstants.MANA_PER_LEVEL
        self.health = self.max_health
        self.mana = self.max_mana
        # Display results
        print(f"\n🎉 LEVEL UP! You are now level {self.level}!")
        print(f"Health increased by {health_gain} (now {self.max_health})")
        print(f"Mana increased by {GameConstants.MANA_PER_LEVEL} (now {self.max_mana})")
        if self.max_inventory > old_max_inventory:
            print(f"Inventory capacity increased! ({old_max_inventory} → {self.max_inventory} slots)")
        print("You have been fully healed!")

    def _apply_single_level_bonuses(self) -> None:
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

    # ========== INVENTORY MANAGEMENT ==========
    def add_item(self, item: str) -> bool:
        if len(self.inventory) >= self.max_inventory:
            print(f"❌ Your inventory is full! ({self.max_inventory} slots)")
            print("Use 'discard <item>' to make space.")
            return False
        self.inventory.append(item)
        print(f"You picked up: {item}")
        return True

    def add_weapon_to_inventory(self, weapon: Dict) -> bool:
        if len(self.inventory) >= self.max_inventory:
            print(f"❌ Your inventory is full! ({self.max_inventory} slots)")
            print("Cannot store weapon.")
            return False
        self.inventory_weapons.append(weapon)
        self.inventory.append(f"WEAPON: {weapon['name']}")
        print(f"You stored weapon: {weapon['name']}")
        return True

    def remove_item(self, item: str) -> bool:
        if item not in self.inventory:
            return False
        if item.startswith("WEAPON:"):
            weapon_name = item[8:]
            for i, weapon in enumerate(self.inventory_weapons):
                if weapon['name'] == weapon_name:
                    self.inventory_weapons.pop(i)
                    break
        self.inventory.remove(item)
        return True

    def can_add_item(self) -> bool:
        return len(self.inventory) < self.max_inventory

    def get_inventory_count(self) -> int:
        return len(self.inventory)

    def discard_item(self, item_name: str) -> bool:
        for item in self.inventory:
            if item.lower() == item_name.lower():
                self.remove_item(item)
                print(f"You discarded: {item}")
                return True
            if item_name.lower() in item.lower():
                self.remove_item(item)
                print(f"You discarded: {item}")
                return True
        print(f"You don't have '{item_name}' in your inventory.")
        return False

    # ========== ITEM USAGE ==========
    def consume_item(self) -> None:
        healing = [item for item in self.inventory if item in GameConstants.HEALING_ITEMS]
        exp_items = [item for item in self.inventory if item in GameConstants.IMMEDIATE_EFFECT_ITEMS]
        if not healing and not exp_items:
            print("You have no consumable items!")
            return
        print("\nChoose type:")
        print("1. Healing item")
        print("2. Experience item")
        try:
            choice = input("Enter 1 or 2: ").strip()
            if choice == '1':
                self.use_healing_item()
            elif choice == '2':
                self.use_exp_item()
            else:
                print("Invalid choice!")
        except KeyboardInterrupt:
            print("\nAction interrupted.")

    def use_healing_item(self, item_name: Optional[str] = None) -> bool:
        healing_items = GameConstants.HEALING_ITEMS
        if item_name:
            if item_name in self.inventory and item_name in healing_items:
                return self._apply_healing_effect(item_name, healing_items[item_name])
            print(f"You don't have '{item_name}' or it's not a healing item.")
            return False
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
        except ValueError:
            print("Please enter a number.")
            return False
        except KeyboardInterrupt:
            print("\nAction interrupted.")
            return False

    def _apply_healing_effect(self, item_name: str, effect: Dict) -> bool:
        self.inventory.remove(item_name)
        if effect['type'] == 'health':
            if effect['heal'] == 'full':
                heal_amount = self.max_health - self.health
                self.health = self.max_health
                print(f"💚 You are fully healed! (+{heal_amount} health)")
            else:
                heal_amount = min(effect['heal'], self.max_health - self.health)
                self.health += heal_amount
                print(f"💚 You heal for {heal_amount} health!")
        elif effect['type'] == 'mana':
            mana_amount = min(effect['heal'], self.max_mana - self.mana)
            self.mana += mana_amount
            print(f"💙 Your mana is restored! (+{mana_amount} mana)")
        return True

    def use_exp_item(self, item_name: Optional[str] = None) -> bool:
        exp_items = GameConstants.IMMEDIATE_EFFECT_ITEMS
        if item_name:
            if item_name in self.inventory and item_name in exp_items:
                effect = exp_items[item_name]
                self.gain_experience(effect['amount'])
                self.inventory.remove(item_name)
                return True
            print(f"You don't have '{item_name}' or it's not an experience item.")
            return False
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
        except ValueError:
            print("Please enter a number.")
            return False
        except KeyboardInterrupt:
            print("\nAction interrupted.")
            return False

    # ========== WEARABLES ==========
    def equip_wearable(self, item: str) -> None:
        if item in GameConstants.WEARABLE_ITEMS:
            effect = GameConstants.WEARABLE_ITEMS[item]
            self.stats[effect['stat']] += effect['bonus']
            self.wearables.append({'item': item, 'stat': effect['stat'], 'bonus': effect['bonus']})
            print(f"🌟 Equipped {item}! +{effect['bonus']} to {effect['stat']}.")
        else:
            print(f"{item} is not wearable.")

    # ========== WEAPON MANAGEMENT ==========
    def equip_weapon(self, weapon: Dict) -> None:
        self.weapon = weapon
        print(f"You equipped: {weapon['name']}")

    def switch_weapon(self, weapon_identifier: Optional[str] = None) -> bool:
        if not self.inventory_weapons:
            print("You don't have any spare weapons!")
            return False
        target_weapon = None
        if weapon_identifier:
            for weapon in self.inventory_weapons:
                if weapon_identifier.lower() in weapon['name'].lower() or weapon_identifier.lower() in weapon.get('base_name', '').lower():
                    target_weapon = weapon
                    break
            if not target_weapon:
                print(f"You don't have a weapon matching '{weapon_identifier}'.")
                return False
        else:
            print("Available weapons:")
            for i, weapon in enumerate(self.inventory_weapons, 1):
                rarity_data = GameConstants.WEAPON_RARITIES[weapon.get('rarity', 'common')]
                print(f"{i}. {weapon['name']} ({weapon['damage']} damage) {rarity_data['color']}")
            try:
                choice = int(input("Choose weapon to equip (number): ")) - 1
                if 0 <= choice < len(self.inventory_weapons):
                    target_weapon = self.inventory_weapons[choice]
                else:
                    print("Invalid choice.")
                    return False
            except ValueError:
                print("Please enter a number.")
                return False
            except KeyboardInterrupt:
                print("\nAction interrupted.")
                return False
        # Perform switch
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

    # ========== DISPLAY ==========
    def show_stats(self) -> None:
        weapon_name = self.weapon['name'] if self.weapon else "None"
        weapon_damage = f" ({self.weapon['damage']} damage)" if self.weapon else ""
        weapon_rarity = ""
        if self.weapon and 'rarity' in self.weapon:
            rarity_data = GameConstants.WEAPON_RARITIES[self.weapon['rarity']]
            weapon_rarity = f" {rarity_data['color']} {self.weapon['rarity'].title()}"
        class_title = self.get_class_title()
        print(f"\n=== {self.name} the {class_title} ===")
        print(f"Class Tier: {self.class_tier}/3")
        print(f"Level: {self.level}")
        print(f"Experience: {self.experience}/{self.experience_to_next}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Mana: {self.mana}/{self.max_mana}")
        print(f"Weapon: {weapon_name}{weapon_damage}{weapon_rarity}")
        print(f"Strength: {self.stats['strength']}")
        print(f"Intelligence: {self.stats['intelligence']}")
        print(f"Agility: {self.stats['agility']}")
        print(f"Inventory: {self.get_inventory_count()}/{self.max_inventory} slots")
        print(f"Current Room: {self.current_room}")
        print(f"Boss Defeated: {'Yes' if self.boss_defeated else 'No'}")
        if self.wearables:
            print("\nWearables:")
            for w in self.wearables:
                print(f" - {w['item']}: +{w['bonus']} {w['stat']}")
        if self.can_upgrade_class():
            print(f"\n🌟 CLASS UPGRADE AVAILABLE! You can advance to {self.get_next_class_title()}!")
            print("Use 'upgrade' command to upgrade your class.")

    def show_status_summary(self) -> None:
        weapon_name = self.weapon['name'] if self.weapon else "None"
        print(f"\n[Status] Health: {self.health}/{self.max_health} | Mana: {self.mana}/{self.max_mana} | Weapon: {weapon_name}")

    # ========== SERIALIZATION ==========
    def to_dict(self) -> Dict[str, Any]:
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
            'current_room': self.current_room,
            'visited_rooms': list(self.visited_rooms),
            'boss_defeated': self.boss_defeated,
            'first_boss_defeated': self.first_boss_defeated,
            'has_rusty_key': self.has_rusty_key,
            'rarity_boost': self.rarity_boost
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
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
        player.current_room = data['current_room']
        player.visited_rooms = set(data.get('visited_rooms', []))
        player.boss_defeated = data.get('boss_defeated', False)
        player.first_boss_defeated = data.get('first_boss_defeated', False)
        player.has_rusty_key = data.get('has_rusty_key', False)
        player.rarity_boost = data.get('rarity_boost', 0.0)
        # Re-apply wearable bonuses
        for wearable in player.wearables:
            player.stats[wearable['stat']] += wearable['bonus']
        return player

#################################################################################
# ROOM CLASS
#################################################################################
class Room:
    """Represents a dungeon location with description, items, exits, and enemies."""
    def __init__(self, name: str, description: str, items: Optional[List[str]] = None,
                 exits: Optional[Dict[str, str]] = None, enemies: Optional[List[str]] = None,
                 hidden_items: Optional[Dict[str, List[str]]] = None):
        self.name = name
        self.description = description
        self.items = items or []
        self.exits = exits or {}
        self.enemies = enemies or []
        self.hidden_items = hidden_items or {}
        self.visited = False

    def describe(self) -> None:
        if not self.visited:
            print(f"\n{self.description}")
            self.visited = True
        else:
            print(f"\nYou are in {self.name}")
        if self.enemies:
            print(f"⚔️ Enemies here: {', '.join(self.enemies)}")
        if self.items:
            print(f"Items here: {', '.join(self.items)}")
        if self.exits:
            print(f"Exits: {', '.join(self.exits.keys())}")

    def reveal_hidden_items(self, condition: str) -> List[str]:
        if condition in self.hidden_items:
            new_items = self.hidden_items[condition]
            self.items.extend(new_items)
            del self.hidden_items[condition]
            return new_items
        return []

#################################################################################
# ROOM TEMPLATES
#################################################################################
class RoomTemplates:
    """Centralized room template definitions to avoid duplication."""
    @staticmethod
    def get_all_templates() -> Dict[str, Dict[str, Any]]:
        return {
            'start': {
                'name': "Starting Room",
                'description': "You find yourself in a dimly lit room. This appears to be the beginning of your adventure.",
                'items': ['rusty key', 'old map'],
                'enemies': [],
                'type': 'start'
            },
            'hallway': {
                'name': "Long Hallway",
                'description': "A long, narrow hallway stretches before you. Torches line the walls.",
                'items': ['torch'],
                'enemies': ['goblin'],
                'type': 'normal'
            },
            'storage': {
                'name': "Storage Room",
                'description': "A cluttered storage room filled with old boxes and forgotten items.",
                'items': ['health potion', 'rope', 'magic scroll'],
                'enemies': [],
                'type': 'normal'
            },
            'armory': {
                'name': "Ancient Armory",
                'description': "An old armory filled with weapon racks. Some weapons still gleam in the torchlight.",
                'items': ['weapon cache', 'armor piece'],
                'enemies': ['armored skeleton'],
                'type': 'normal',
                'hidden_items': {'first_boss_defeated': ['ancient chest']}
            },
            'arena': {
                'name': "Gladiator Arena",
                'description': "A massive circular arena with sand-covered floors. The crowd's ghostly cheers echo.",
                'items': ["champion's prize", 'victory scroll'],
                'enemies': ['Arena Champion'],
                'type': 'boss'
            },
            'treasure_room': {
                'name': "Treasure Room",
                'description': "A magnificent room with golden walls. A treasure chest sits in the center!",
                'items': ['golden coin', 'magic sword', 'experience gem'],
                'enemies': ['treasure guardian'],
                'type': 'normal'
            },
            'frozen_cavern': {
                'name': "Frozen Cavern",
                'description': "A bone-chilling cavern covered in ancient ice. Frozen breath escapes your lips.",
                'items': ['ice crystal', 'frozen artifact'],
                'enemies': ['Frost Titan'],
                'type': 'boss'
            },
            'boss_chamber': {
                'name': "Dark Boss Chamber",
                'description': "A massive, ominous chamber. Ancient runes glow on the walls. The Dark Lord awaits!",
                'items': ['legendary artifact', 'ultimate health potion'],
                'enemies': ['Dark Lord'],
                'type': 'boss'
            },
            'crypt': {
                'name': "Ancient Crypt",
                'description': "A damp, dark crypt filled with ancient tombs. The air is thick with decay.",
                'items': ['cursed amulet', 'health potion', 'bone key'],
                'enemies': ['shadow wraith', 'armored skeleton'],
                'type': 'normal'
            },
            'library': {
                'name': "Forgotten Library",
                'description': "A vast library with towering bookshelves. Dust covers ancient tomes.",
                'items': ['spell book', 'magic scroll', 'wisdom gem'],
                'enemies': ['corrupted mage'],
                'type': 'normal'
            },
            'garden': {
                'name': "Overgrown Garden",
                'description': "An enchanted garden overgrown with magical vines. Strange plants glow in darkness.",
                'items': ['healing herb', 'mana flower', "nature's blessing"],
                'enemies': ['shadow wraith'],
                'type': 'normal'
            }
        }

#################################################################################
# WEAPON SYSTEM
#################################################################################
class WeaponSystem:
    """Manages weapon generation, rarity calculations, and the Golden Gun."""
    @staticmethod
    def get_rarity_multiplier(rarity: str) -> float:
        return GameConstants.WEAPON_RARITIES[rarity]['multiplier']

    @staticmethod
    def get_rarity_color(rarity: str) -> str:
        return GameConstants.WEAPON_RARITIES[rarity]['color']

    @classmethod
    def generate_random_weapon(cls, player: 'Player', force_rarity: Optional[str] = None) -> Dict[str, Any]:
        # Check for Golden Gun (0.02% chance)
        if not force_rarity and random.random() < GameConstants.GOLDEN_GUN_DROP_RATE:
            return cls._create_golden_gun()
        # Determine rarity
        rarity = force_rarity or cls._calculate_rarity_by_level(player.level, player.rarity_boost)
        # Class-specific weapon type
        allowed_types = GameConstants.CLASSES[player.character_class]['weapon_types']
        weapon_type = random.choice(allowed_types)
        # Generate weapon components
        material = random.choice(GameConstants.WEAPON_MATERIALS[rarity])
        weapon_name = random.choice(GameConstants.WEAPON_TYPES[weapon_type])
        # Calculate damage
        base_damage = random.randint(8, 15) + (player.level * 2)
        rarity_multiplier = cls.get_rarity_multiplier(rarity)
        final_damage = int(base_damage * rarity_multiplier)
        # Create weapon dict
        full_name = f"{material} {weapon_name}"
        rarity_symbol = cls.get_rarity_color(rarity)
        return {
            'name': f"{rarity_symbol} {full_name}",
            'damage': final_damage,
            'type': weapon_type,
            'rarity': rarity,
            'base_name': full_name
        }

    @classmethod
    def _calculate_rarity_by_level(cls, player_level: int, rarity_boost: float = 0.0) -> str:
        boost = int(rarity_boost * 100)
        rarity_chances = {
            'common': max(50 - (player_level * 3) - boost, 10),
            'uncommon': min(25 + (player_level * 2), 35),
            'rare': min(15 + player_level + (boost // 3), 25),
            'epic': min(8 + (player_level // 2) + (boost // 3), 15),
            'legendary': min(2 + (player_level // 3) + (boost // 3), 8),
            'mythic': min(player_level // 5 + (boost // 3), 2)
        }
        # Normalize if sum != 100
        total = sum(rarity_chances.values())
        if total != 100:
            adjustment = 100 - total
            rarity_chances['common'] += adjustment
        rand = random.randint(1, 100)
        cumulative = 0
        for rarity, chance in rarity_chances.items():
            cumulative += chance
            if rand <= cumulative:
                return rarity
        return 'common'

    @classmethod
    def _create_golden_gun(cls) -> Dict[str, Any]:
        chosen_name = random.choice(GameConstants.GOLDEN_GUN_NAMES)
        return {
            'name': f"🌟 {chosen_name}",
            'damage': 99999,
            'type': 'divine',
            'rarity': 'divine',
            'base_name': chosen_name,
            'uses_remaining': 6,
            'max_uses': 6,
            'special': 'instant_kill'
        }

    @classmethod
    def create_starting_weapons(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'sword': {
                'name': '⚪ Iron Sword',
                'damage': 15,
                'type': 'melee',
                'rarity': 'common',
                'base_name': 'Iron Sword'
            },
            'staff': {
                'name': '⚪ Wooden Staff',
                'damage': 10,
                'type': 'magic',
                'rarity': 'common',
                'base_name': 'Wooden Staff'
            },
            'dagger': {
                'name': '⚪ Steel Dagger',
                'damage': 12,
                'type': 'stealth',
                'rarity': 'common',
                'base_name': 'Steel Dagger'
            }
        }

#################################################################################
# COMBAT SYSTEM
#################################################################################
class CombatSystem:
    """Manages all combat mechanics including regular fights and boss encounters."""
    def __init__(self, game: 'Game'):
        self.game = game

    # ========== REGULAR COMBAT ==========
    def fight_regular_enemy(self, enemy_name: str, player: Player, room: Room) -> bool:
        enemy_stats = GameConstants.ENEMIES.get(enemy_name.lower(), None)
        if not enemy_stats:
            print(f"Unknown enemy: {enemy_name}")
            return True
        enemy_health = enemy_stats['health']
        enemy_damage = enemy_stats['damage']
        print(f"\n⚔️ You engage the {enemy_name} in combat!")
        # Combat loop
        while enemy_health > 0 and player.health > 0:
            # Player attacks
            damage = self._calculate_player_damage(player)
            enemy_health -= damage
            weapon_rarity = player.weapon.get('rarity', 'common') if player.weapon else 'common'
            rarity_symbol = WeaponSystem.get_rarity_color(weapon_rarity)
            weapon_display = player.weapon.get('base_name', player.weapon['name']) if player.weapon else 'fists'
            if player.weapon:
                print(f"You strike with your {rarity_symbol} {weapon_display} for {damage} damage!")
            else:
                print(f"You punch with your bare fists for {damage} damage!")
            if enemy_health <= 0:
                print(f"💀 You defeated the {enemy_name}!")
                room.enemies.remove(enemy_name)
                player.gain_experience(enemy_stats['exp'])
                self._handle_enemy_drops(enemy_name, room, player)
                return True
            # Enemy attacks
            enemy_hit = self._calculate_enemy_damage(enemy_damage, player)
            player.health -= enemy_hit
            print(f"The {enemy_name} hits you for {enemy_hit} damage!")
            if player.health <= 0:
                print("💀 You have been defeated!")
                print("Game Over! Try loading a saved game or starting over.")
                return False
        return True

    def _calculate_player_damage(self, player: Player) -> int:
        # Check for Golden Gun special case
        if player.weapon and player.weapon.get('special') == 'instant_kill' and player.weapon.get('uses_remaining', 0) > 0:
            player.weapon['uses_remaining'] -= 1
            remaining = player.weapon['uses_remaining']
            print(f"🌟 THE {player.weapon['base_name'].upper()} FIRES! 🌟")
            print(f"⚡ INSTANT OBLITERATION! ⚡")
            print(f"Uses remaining: {remaining}/6")
            if remaining <= 0:
                print(f"💨 The {player.weapon['base_name']} crumbles to dust after its final shot...")
                player.weapon = None
                print("⚠️ You are now unarmed! Find a new weapon!")
            return 99999  # Instant kill
        # Check if player has no weapon
        if not player.weapon:
            return random.randint(1, 5)  # Bare fists
        # Regular damage calculation
        base_damage = player.weapon['damage']
        strength_bonus = random.randint(1, player.stats['strength'] // 3)
        weapon_rarity = player.weapon.get('rarity', 'common')
        rarity_multiplier = WeaponSystem.get_rarity_multiplier(weapon_rarity)
        return int((base_damage + strength_bonus) * rarity_multiplier)

    def _calculate_enemy_damage(self, base_damage: int, player: Player) -> int:
        agility_defense = random.randint(1, player.stats['agility'] // 3)
        final_damage = base_damage - agility_defense
        return max(GameConstants.MIN_ENEMY_DAMAGE, final_damage)

    def _handle_enemy_drops(self, enemy_name: str, room: Room, player: Player) -> None:
        weapon_rarity = player.weapon.get('rarity', 'common') if player.weapon else 'common'
        rarity_multiplier = WeaponSystem.get_rarity_multiplier(weapon_rarity)
        drop_chance = GameConstants.ITEM_DROP_BASE_CHANCE + (rarity_multiplier * 0.1)
        if random.random() < drop_chance:
            if random.random() < GameConstants.WEAPON_DROP_CHANCE:
                print(f"💎 The {enemy_name} dropped a weapon cache!")
                room.items.append("weapon cache")
            else:
                drops = ["health potion", "golden coin", "magic scroll"]
                dropped_item = random.choice(drops)
                room.items.append(dropped_item)
                print(f"The {enemy_name} dropped: {dropped_item}")

    # ========== BOSS FIGHTS ==========
    def fight_boss(self, boss_name: str, player: Player, room: Room) -> bool:
        boss_methods = {
            'Dark Lord': self._fight_dark_lord,
            'Arena Champion': self._fight_arena_champion,
            'Frost Titan': self._fight_frost_titan
        }
        if boss_name in boss_methods:
            return boss_methods[boss_name](player, room)
        print(f"Unknown boss: {boss_name}")
        return True

    def _fight_dark_lord(self, player: Player, room: Room) -> bool:
        print("\n" + "="*60)
        print("💀 THE DARK LORD EMERGES FROM THE SHADOWS! 💀")
        print("This is the ultimate challenge!")
        print("="*60)
        boss_config = GameConstants.BOSSES['Dark Lord']
        if player.level < boss_config['min_level']:
            if not self._confirm_boss_fight('Dark Lord', 'underpowered'):
                return True
        success = self._execute_boss_fight('Dark Lord', boss_config, player)
        if success:
            player.boss_defeated = True
            room.enemies.remove('Dark Lord')
            self._award_boss_rewards(player, 'Dark Lord', boss_config)
            print(f"\n🏆 Congratulations, {player.name} the {player.get_class_title()}!")
            print("You are now a legendary hero!")
        return success

    def _fight_arena_champion(self, player: Player, room: Room) -> bool:
        print("\n" + "="*60)
        print("🏛️ THE ARENA CHAMPION STEPS FORWARD! 🏛️")
        print("A legendary gladiator who has never known defeat!")
        print("="*60)
        boss_config = GameConstants.BOSSES['Arena Champion']
        if player.level < boss_config['min_level']:
            if not self._confirm_boss_fight('Arena Champion', 'strong'):
                return True
        success = self._execute_boss_fight('Arena Champion', boss_config, player)
        if success:
            room.enemies.remove('Arena Champion')
            self._award_boss_rewards(player, 'Arena Champion', boss_config)
            print("You are the new arena champion!")
            # Unlock hidden chest
            if not player.first_boss_defeated:
                player.first_boss_defeated = True
                print("\n🔓 A mysterious force stirs in the world...")
                print("Something has been unlocked...")
                self.game.reveal_hidden_chest()
        return success

    def _fight_frost_titan(self, player: Player, room: Room) -> bool:
        print("\n" + "="*60)
        print("❄️ THE FROST TITAN AWAKENS FROM ETERNAL SLUMBER! ❄️")
        print("Ancient ice magic radiates from its massive form!")
        print("="*60)
        boss_config = GameConstants.BOSSES['Frost Titan']
        if player.level < boss_config['min_level']:
            if not self._confirm_boss_fight('Frost Titan', 'overwhelming'):
                return True
        success = self._execute_boss_fight('Frost Titan', boss_config, player)
        if success:
            room.enemies.remove('Frost Titan')
            self._award_boss_rewards(player, 'Frost Titan', boss_config)
            # Special Frost Titan bonus reward
            mythic_weapon = WeaponSystem.generate_random_weapon(player, "mythic")
            room.items.append("weapon cache")
            print(f"\n❄️ The Titan's icy power crystallizes into: {mythic_weapon['name']}!") 
            print("Check the room for additional legendary loot!")
            print("The ancient ice magic is yours to command!")
        return success

    def _confirm_boss_fight(self, boss_name: str, difficulty: str) -> bool:
        warnings = {
            'underpowered': "⚠️ WARNING: You seem underpowered for this fight!",
            'strong': f"⚠️ WARNING: The {boss_name} looks incredibly strong!",
            'overwhelming': f"⚠️ WARNING: The {boss_name}'s aura is overwhelming!"
        }
        print(warnings[difficulty])
        print(f"Consider leveling up more before facing the {boss_name}.")
        try:
            choice = input("Do you want to fight anyway? (y/n): ").strip().lower()
            return choice in ['y', 'yes']
        except KeyboardInterrupt:
            print("\nAction interrupted.")
            return False

    def _execute_boss_fight(self, boss_name: str, boss_config: Dict, player: Player) -> bool:
        boss_health = boss_config['base_health'] + (player.level * boss_config['health_scaling'])
        boss_max_health = boss_health
        boss_damage = boss_config['damage']
        print(f"\n🔥 The {boss_name} has {boss_health} health!")
        print("The battle begins!")
        turn = 1
        while boss_health > 0 and player.health > 0:
            print(f"\n--- Turn {turn} ---")
            print(f"Your Health: {player.health}/{player.max_health}")
            print(f"{boss_name} Health: {boss_health}/{boss_max_health}")
            # Player's turn
            player_damage, defend_mode = self._player_turn(player)
            boss_health -= player_damage
            if boss_health <= 0:
                break
            # Boss's turn
            boss_attack_damage = self._boss_turn(
                boss_name, boss_config, boss_max_health, boss_health, turn, defend_mode, player
            )
            player.health -= boss_attack_damage
            if player.health <= 0:
                print(f"\n💀 You have been defeated by the {boss_name}!")
                print("The battle is lost... Game Over!")
                print("Try loading a saved game or starting over.")
                return False
            turn += 1
        return True

    def _player_turn(self, player: Player) -> Tuple[int, bool]:
        print("\nChoose your action:")
        print("1. Attack with weapon")
        print("2. Use magic (costs mana)")
        print("3. Defend (reduce incoming damage)")
        if any(item in GameConstants.HEALING_ITEMS for item in player.inventory):
            print("4. Use health potion")
        try:
            action = input("Enter your choice (1-4): ").strip()
        except KeyboardInterrupt:
            print("\nAction interrupted.")
            return 0, False
        player_damage = 0
        defend_mode = False
        if action == "1":
            # Weapon attack
            if not player.weapon:
                print("⚠️ You have no weapon! Using bare fists...")
                player_damage = random.randint(1, 5)
            else:
                player_damage = self._calculate_player_damage(player)
            if player.weapon:  # Check again in case Golden Gun depleted
                weapon_rarity = player.weapon.get('rarity', 'common')
                rarity_symbol = WeaponSystem.get_rarity_color(weapon_rarity)
                weapon_display = player.weapon.get('base_name', player.weapon['name'])
                print(f"⚔️ You strike with your {rarity_symbol} {weapon_display} for {player_damage} damage!")
            else:
                print(f"⚔️ You strike with your bare fists for {player_damage} damage!")
        elif action == "2":
            # Magic attack
            if player.mana >= GameConstants.MAGIC_MANA_COST:
                player.mana -= GameConstants.MAGIC_MANA_COST
                magic_damage = player.stats['intelligence'] + random.randint(*GameConstants.MAGIC_DAMAGE_RANGE)
                player_damage = magic_damage
                print(f"🔮 You cast a powerful spell for {player_damage} damage!")
            else:
                print("❌ Not enough mana! You resort to a basic attack.")
                player_damage = player.weapon['damage'] if player.weapon else random.randint(1, 5)
        elif action == "3":
            # Defend
            defend_mode = True
            print("🛡️ You raise your guard and prepare to defend!")
        elif action == "4" and any(item in GameConstants.HEALING_ITEMS for item in player.inventory):
            # Heal
            player.use_healing_item()
        else:
            print("Invalid action! You hesitate and lose your turn.")
        return player_damage, defend_mode

    def _boss_turn(self, boss_name: str, boss_config: Dict, boss_max_health: int, boss_health: int,
                    turn: int, defend_mode: bool, player: Player) -> int:
        boss_damage = boss_config['damage']
        special_attack = boss_config['special_attack']
        special_bonus = boss_config['special_bonus']
        # Determine if boss uses special attack
        use_special = (boss_health < boss_max_health * GameConstants.BOSS_SPECIAL_HEALTH_THRESHOLD and
                       turn % GameConstants.BOSS_SPECIAL_TURN_FREQUENCY == 0)
        if use_special:
            # Special attack
            special_damage = boss_damage + special_bonus
            if defend_mode:
                special_damage //= GameConstants.BOSS_DEFEND_REDUCTION
            print(f"🔥 The {boss_name} unleashes {special_attack}! You block some damage and take {special_damage} damage!")
            return special_damage
        else:
            # Normal attack
            normal_damage = boss_damage + random.randint(1, 10)
            agility_defense = random.randint(1, player.stats['agility'] // 2)
            final_damage = normal_damage - agility_defense
            if defend_mode:
                final_damage //= GameConstants.BOSS_DEFEND_REDUCTION
                print(f"⚔️ The {boss_name} attacks! You defend and take only {final_damage} damage!")
            else:
                final_damage = max(GameConstants.MIN_BOSS_DAMAGE, final_damage)
                print(f"⚔️ The {boss_name} strikes you for {final_damage} damage!")
            return final_damage

    def _award_boss_rewards(self, player: Player, boss_name: str, boss_config: Dict) -> None:
        print("\n" + "="*60)
        print("🎉 VICTORY! 🎉")
        print("="*60)
        # Experience reward
        player.gain_experience(boss_config['exp_reward'])
        # Boss weapon reward based on player class
        boss_weapons = {
            'Dark Lord': {
                'warrior': {'name': '🟡 Excalibur', 'damage': 35, 'type': 'melee', 'rarity': 'legendary', 'base_name': 'Excalibur'},
                'mage': {'name': '🟡 Staff of Arcane Power', 'damage': 30, 'type': 'magic', 'rarity': 'legendary', 'base_name': 'Staff of Arcane Power'},
                'rogue': {'name': '🟡 Shadow Fang', 'damage': 32, 'type': 'stealth', 'rarity': 'legendary', 'base_name': 'Shadow Fang'}
            },
            'Arena Champion': {
                'warrior': {'name': '🟣 Gladius of Victory', 'damage': 32, 'type': 'melee', 'rarity': 'epic', 'base_name': 'Gladius of Victory'},
                'mage': {'name': '🟣 Champion\'s Scepter', 'damage': 28, 'type': 'magic', 'rarity': 'epic', 'base_name': 'Champion\'s Scepter'},
                'rogue': {'name': '🟣 Twin Blades of Honor', 'damage': 30, 'type': 'stealth', 'rarity': 'epic', 'base_name': 'Twin Blades of Honor'}
            },
            'Frost Titan': {
                'warrior': {'name': '🔴 Frostbane Greatsword', 'damage': 38, 'type': 'melee', 'rarity': 'mythic', 'base_name': 'Frostbane Greatsword'},
                'mage': {'name': '🔴 Staff of Eternal Winter', 'damage': 35, 'type': 'magic', 'rarity': 'mythic', 'base_name': 'Staff of Eternal Winter'},
                'rogue': {'name': '🔴 Icicle Piercer', 'damage': 36, 'type': 'stealth', 'rarity': 'mythic', 'base_name': 'Icicle Piercer'}
            }
        }
        boss_weapon = boss_weapons[boss_name][player.character_class]
        print(f"\n🗡️ You receive: {boss_weapon['name']}!")
        print(f"Damage: {boss_weapon['damage']} | Rarity: {boss_weapon['rarity'].title()}")
        print("This legendary weapon is now yours!")
        player.equip_weapon(boss_weapon)
        # Full heal and stat bonuses
        player.health = player.max_health
        player.mana = player.max_mana
        stat_bonus = boss_config['stat_bonus']
        for stat in player.stats:
            player.stats[stat] += stat_bonus
        print(f"\n🌟 You feel permanently stronger from this epic battle!")
        print(f"All stats increased by {stat_bonus}!")
        print("You have been fully healed!")

#################################################################################
# COMMAND HANDLER
#################################################################################
class CommandHandler:
    """Handles command processing for the game."""
    def __init__(self, game: 'Game'):
        self.game = game
        self.commands = {
            'help': self.game.show_help,
            'look': self.game.look_around,
            'go': self.game.move,
            'take': self.game.take_item,
            'takeall': self.game.take_all_items,
            'inventory': self.game.show_inventory,
            'stats': self.game.show_stats,
            'fight': self.game.fight_enemy,
            'upgrade': self.game.upgrade_class_command,
            'consume': self.game.consume_item,
            'switch': self.game.switch_weapon,
            'discard': self.game.discard_item,
            'map': self.game.show_map,
            'save': self.game.save_game,
            'load': self.game.load_game,
            'quit': self.game.quit_game,
            'exit': self.game.quit_game
        }

    def process(self, user_input: str) -> None:
        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        if command in self.commands:
            try:
                if args:
                    self.commands[command](*args)
                else:
                    self.commands[command]()
            except Exception as e:
                logging.error(f"Command error in {command}: {str(e)}")
                print(f"Error executing command: {e}")
        else:
            print("I don't understand that command. Type 'help' for available commands.")

#################################################################################
# GAME CLASS
#################################################################################
class Game:
    """Main game controller managing world state, commands, and game flow."""
    def __init__(self):
        self.player: Optional[Player] = None
        self.rooms: Optional[Dict[str, Room]] = None
        self.room_layout: Optional[Dict[str, Dict[str, str]]] = None
        self.running = True
        self.weapons = WeaponSystem.create_starting_weapons()
        self.combat = CombatSystem(self)
        self.save_file = GameConstants.SAVE_FILE
        self.command_handler = CommandHandler(self)

    # ========== GAME FLOW CONTROL ==========
    def start_game(self) -> None:
        print("=" * 50)
        print(" TEXT ADVENTURE RPG")
        print(f" Version {GameConstants.VERSION}")
        print("=" * 50)
        print("\nWould you like to:")
        print("1. Start a new game")
        print("2. Load a saved game")
        while True:
            try:
                choice = input("\nEnter your choice (1-2): ").strip()
                if choice == '1':
                    self.create_new_character()
                    break
                elif choice == '2':
                    if self.load_game():
                        break
                    print("No save file found. Starting new game...")
                    self.create_new_character()
                    break
                else:
                    print("Invalid choice! Please enter 1 or 2.")
            except KeyboardInterrupt:
                print("\nInput interrupted. Please choose an option.")

        print("\nType 'help' for a list of commands.")
        self.look_around()
        self.game_loop()

    def game_loop(self) -> None:
        while self.running:
            try:
                user_input = input("\n> ").strip().lower()
                if not user_input:
                    continue
                self.command_handler.process(user_input)
                if self.player:
                    self.player.show_status_summary()
            except KeyboardInterrupt:
                print("\n\nGame interrupted. Don't forget to save! Goodbye!")
                break
            except Exception as e:
                logging.error(str(e))
                print(f"An error occurred: {e}")
                print("Please report this bug!")

    # ========== CHARACTER CREATION ==========
    def create_new_character(self) -> None:
        try:
            name = input("Enter your character's name: ").strip()
            if not name:
                name = "Adventurer"
            character_class = self._choose_character_class()
            self.player = Player(name, character_class)
            starting_weapon = self._choose_starting_weapon()
            self.player.equip_weapon(starting_weapon)
            self.rooms = self._create_procedural_world()
            print(f"\nWelcome, {self.player.name} the {character_class.title()}!")
            print(f"You begin your adventure with a {starting_weapon['base_name']}.")
        except Exception as e:
            logging.error(f"Character creation error: {str(e)}")
            print("Error creating character. Starting with default.")
            self.player = Player("Adventurer", "warrior")
            self.rooms = self._create_procedural_world()

    def _choose_character_class(self) -> str:
        print("\n=== Choose Your Character Class ===")
        print("1. Warrior - High health and strength, tanky melee fighter")
        print("2. Mage - High mana and intelligence, masters of magic")
        print("3. Rogue - Balanced with high agility, quick and stealthy")
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                class_map = {'1': 'warrior', '2': 'mage', '3': 'rogue'}
                if choice in class_map:
                    return class_map[choice]
                print("Invalid choice! Please enter 1, 2, or 3.")
            except KeyboardInterrupt:
                print("\nInput interrupted. Please choose a class.")

    def _choose_starting_weapon(self) -> Dict[str, Any]:
        print("\n=== Choose Your Starting Weapon ===")
        print("1. Iron Sword - 15 damage, reliable melee weapon")
        print("2. Wooden Staff - 10 damage, channels magical energy")
        print("3. Steel Dagger - 12 damage, quick and precise")
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                weapon_map = {'1': 'sword', '2': 'staff', '3': 'dagger'}
                if choice in weapon_map:
                    return self.weapons[weapon_map[choice]].copy()
                print("Invalid choice! Please enter 1, 2, or 3.")
            except KeyboardInterrupt:
                print("\nInput interrupted. Please choose a weapon.")

    # ========== PROCEDURAL WORLD GENERATION ==========
    def _create_procedural_world(self) -> Dict[str, Room]:
        print("\n🗺️ Generating procedural dungeon layout...")
        room_templates = RoomTemplates.get_all_templates()
        self.room_layout = self._generate_random_layout(room_templates)
        rooms = {}
        for room_id, template in room_templates.items():
            exits = self.room_layout.get(room_id, {})
            hidden = template.get('hidden_items', {})
            rooms[room_id] = Room(
                template['name'],
                template['description'],
                items=template['items'].copy(),
                exits=exits,
                enemies=template['enemies'].copy(),
                hidden_items=hidden.copy()
            )
        print("✅ Dungeon generated! Each playthrough has a unique layout.")
        return rooms

    def _generate_random_layout(self, room_templates: Dict) -> Dict[str, Dict[str, str]]:
        layout = {room: {} for room in room_templates}
        rooms = list(room_templates.keys())
        random.shuffle(rooms)
        connected = {'start'}
        to_connect = set(rooms) - connected
        directions = ['north', 'south', 'east', 'west']
        reverse = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        while to_connect:
            room = to_connect.pop()
            parent = random.choice(list(connected))
            available_dirs = [d for d in directions if d not in layout[parent]]
            if available_dirs:
                direction = random.choice(available_dirs)
                layout[parent][direction] = room
                layout[room][reverse[direction]] = parent
                connected.add(room)
            else:
                # If no available, add back and try later
                to_connect.add(room)
        return layout

    def reveal_hidden_chest(self) -> None:
        for room_id, room in self.rooms.items():
            revealed = room.reveal_hidden_items('first_boss_defeated')
            if revealed:
                print(f"✨ A hidden chest has appeared in the {room.name}!")
                print(f"It contains: {', '.join(revealed)}")

    # ========== COMMAND IMPLEMENTATIONS ==========
    def show_help(self) -> None:
        print("\n" + "="*50)
        print("AVAILABLE COMMANDS")
        print("="*50)
        print("help - Show this help message")
        print("look - Look around the current room")
        print("go <dir> - Move (north, south, east, west)")
        print("take <item> - Pick up an item")
        print("takeall - Pick up all items in room")
        print("inventory - Show your inventory")
        print("stats - Show character stats")
        print("fight <enemy> - Fight an enemy")
        print("consume - Use a healing or experience item")
        print("switch [weapon] - Switch weapons")
        print("discard <item> - Discard an item")
        print("map - View the dungeon map")
        print("upgrade - Upgrade class (level 5+)")
        print("save - Save your game")
        print("load - Load saved game")
        print("quit/exit - Quit the game")
        print("="*50)

    def look_around(self) -> None:
        current_room = self.rooms[self.player.current_room]
        current_room.describe()
        self.player.visited_rooms.add(self.player.current_room)

    def move(self, direction: str) -> None:
        current_room = self.rooms[self.player.current_room]
        if direction in current_room.exits:
            self.player.current_room = current_room.exits[direction]
            self.player.visited_rooms.add(self.player.current_room)
            print(f"You go {direction}.")
            self.look_around()
        else:
            print("You can't go that way!")

    def show_map(self) -> None:
        print("\n" + "="*50)
        print("DUNGEON MAP")
        print("="*50)
        current = self.player.current_room
        visited = self.player.visited_rooms
        print(f"\nCurrent Location: {self.rooms[current].name}")
        print(f"Rooms Discovered: {len(visited)}/{len(self.rooms)}\n")
        print("Visited Rooms:")
        for room_id in sorted(visited):
            room = self.rooms[room_id]
            marker = "📍" if room_id == current else "✓"
            exits_str = ", ".join(room.exits.keys()) if room.exits else "none"
            print(f" {marker} {room.name}")
            print(f"   Exits: {exits_str}")
        undiscovered = len(self.rooms) - len(visited)
        if undiscovered > 0:
            print(f"\n🔒 {undiscovered} undiscovered room(s) remain...")
        else:
            print("\n🎉 All rooms discovered!")
        print("="*50)

    def show_inventory(self) -> None:
        print(f"\n=== INVENTORY ({self.player.get_inventory_count()}/{self.player.max_inventory} slots) ===")
        if self.player.weapon:
            print(f"Equipped Weapon: {self.player.weapon['name']}")
        if not self.player.inventory:
            print("Your inventory is empty.")
            return
        weapons = [item for item in self.player.inventory if item.startswith("WEAPON:")]
        healing = [item for item in self.player.inventory if item in GameConstants.HEALING_ITEMS]
        exp = [item for item in self.player.inventory if item in GameConstants.IMMEDIATE_EFFECT_ITEMS]
        other = [item for item in self.player.inventory if not item.startswith("WEAPON:") and item not in healing and item not in exp]
        if healing:
            print("\n💚 Healing Items:")
            for item in healing:
                print(f" • {item}")
        if exp:
            print("\n📜 Experience Items:")
            for item in exp:
                print(f" • {item}")
        if weapons:
            print("\n⚔️ Stored Weapons:")
            for item in weapons:
                print(f" • {item[8:]}")
        if other:
            print("\n📦 Other Items:")
            for item in other:
                print(f" • {item}")
        print(f"\nUse 'consume' to use healing or experience items")
        print(f"Use 'switch' to change weapons")
        print(f"Use 'discard <item>' to remove items")

    def show_stats(self) -> None:
        self.player.show_stats()

    def consume_item(self, *args) -> None:
        if args:
            item_name = ' '.join(args)
            if item_name in GameConstants.HEALING_ITEMS:
                self.player.use_healing_item(item_name)
            elif item_name in GameConstants.IMMEDIATE_EFFECT_ITEMS:
                self.player.use_exp_item(item_name)
            else:
                print(f"Invalid item: {item_name}")
        else:
            self.player.consume_item()

    def switch_weapon(self, *args) -> None:
        weapon_identifier = ' '.join(args) if args else None
        self.player.switch_weapon(weapon_identifier)

    def discard_item(self, *args) -> None:
        if not args:
            print("Discard what?")
            print("Usage: discard <item name>")
            return
        item_name = ' '.join(args)
        self.player.discard_item(item_name)

    # ========== ITEM MANAGEMENT ==========
    def take_item(self, *args) -> None:
        if not args:
            print("Take what?")
            return
        item = ' '.join(args)
        current_room = self.rooms[self.player.current_room]
        if item not in current_room.items:
            print(f"There's no '{item}' here.")
            if current_room.items:
                print(f"Available items: {', '.join(current_room.items)}")
            return
        if not self.player.can_add_item() and item not in GameConstants.WEARABLE_ITEMS:
            print(f"❌ Your inventory is full! ({self.player.max_inventory} slots)")
            print("Use 'discard <item>' to make space.")
            return
        current_room.items.remove(item)
        if item == "weapon cache":
            self._handle_weapon_cache()
        elif item == "champion's prize":
            self._handle_champions_prize()
        elif item == "ancient chest":
            self._handle_ancient_chest()
        else:
            self._handle_regular_item(item)

    def take_all_items(self) -> None:
        current_room = self.rooms[self.player.current_room]
        if not current_room.items:
            print("There are no items here to take.")
            return
        items_taken = []
        items_left = []
        for item in current_room.items[:]:
            if item in GameConstants.WEARABLE_ITEMS or self.player.can_add_item():
                current_room.items.remove(item)
                if item == "weapon cache":
                    self._handle_weapon_cache()
                    items_taken.append(item)
                elif item == "champion's prize":
                    self._handle_champions_prize()
                    items_taken.append(item)
                elif item == "ancient chest":
                    self._handle_ancient_chest()
                    items_taken.append(item)
                else:
                    self._handle_regular_item(item)
                    items_taken.append(item)
            else:
                items_left.append(item)
        if items_taken:
            print(f"\n✅ Picked up {len(items_taken)} item(s)")
        if items_left:
            print(f"❌ Inventory full! Left behind: {', '.join(items_left)}")

    def _handle_weapon_cache(self) -> None:
        new_weapon = WeaponSystem.generate_random_weapon(self.player)
        print(f"🎁 You found a weapon cache!")
        print(f"Inside: {new_weapon['name']}")
        print(f"Damage: {new_weapon['damage']} | Type: {new_weapon['type']} | Rarity: {new_weapon['rarity'].title()}")
        if not self.player.weapon or new_weapon['damage'] > self.player.weapon['damage']:
            choice = input("Equip this weapon? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                if self.player.weapon:
                    print(f"You replace your {self.player.weapon['name']}")
                self.player.equip_weapon(new_weapon)
            else:
                self.player.add_weapon_to_inventory(new_weapon)
        else:
            choice = input("This weapon seems weaker. Take it anyway? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                self.player.add_weapon_to_inventory(new_weapon)
            else:
                print("You leave the weapon behind.")

    def _handle_champions_prize(self) -> None:
        prize_weapon = WeaponSystem.generate_random_weapon(
            self.player, random.choice(['epic', 'legendary'])
        )
        print(f"🏆 The Champion's Prize contains: {prize_weapon['name']}")
        print(f"Damage: {prize_weapon['damage']} | Rarity: {prize_weapon['rarity'].title()}")
        choice = input("Equip this champion weapon? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            if self.player.weapon:
                print(f"You replace your {self.player.weapon['name']}")
            self.player.equip_weapon(prize_weapon)
        else:
            self.player.add_weapon_to_inventory(prize_weapon)

    def _handle_ancient_chest(self) -> None:
        if not self.player.first_boss_defeated:
            print("🔒 The ancient chest is sealed by powerful magic...")
            return
        if "rusty key" not in self.player.inventory:
            print("🔒 The ancient chest is locked. You need a rusty key!")
            self.player.add_item("ancient chest")
            return
        print("\n" + "="*60)
        print("🔑 You use the rusty key on the ancient chest!")
        print("The lock clicks open...")
        print("="*60)
        self.player.inventory.remove("rusty key")
        self.player.has_rusty_key = True
        print("\n✨ The chest bursts open with incredible treasures!")
        legendary_weapon = WeaponSystem.generate_random_weapon(
            self.player, random.choice(['legendary', 'mythic'])
        )
        print(f"\n🗡️ {legendary_weapon['name']} (Damage: {legendary_weapon['damage']})")
        choice = input("Equip this weapon now? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            if self.player.weapon:
                self.player.add_weapon_to_inventory(self.player.weapon)
            self.player.equip_weapon(legendary_weapon)
        else:
            self.player.add_weapon_to_inventory(legendary_weapon)
        healing_rewards = ['ultimate health potion', 'ultimate health potion', 'magic scroll', 'ice crystal']
        print(f"\n💎 Additional rewards:")
        for reward in healing_rewards:
            if self.player.can_add_item():
                self.player.add_item(reward)
        self.player.gain_experience(150)
        print(f"\n🎉 The ancient chest has been opened!")
        print("The rusty key crumbles to dust, its purpose fulfilled...")

    def _handle_regular_item(self, item: str) -> None:
        if item in GameConstants.IMMEDIATE_EFFECT_ITEMS:
            effect = GameConstants.IMMEDIATE_EFFECT_ITEMS[item]
            if effect['type'] == 'exp':
                self.player.gain_experience(effect['amount'])
                if item == 'victory scroll':
                    print("The scroll contains ancient combat knowledge!")
                elif item == 'wisdom gem':
                    print("The gem fills you with ancient wisdom!")
                elif item == 'frozen artifact':
                    print("The ancient artifact fills you with knowledge!")
            return
        if item in GameConstants.WEARABLE_ITEMS:
            self.player.equip_wearable(item)
            return
        if item in GameConstants.QUEST_ITEMS or item in GameConstants.HEALING_ITEMS:
            self.player.add_item(item)
        elif item == "legendary artifact":
            self.player.add_item(item)
            print("🌟 A legendary artifact! Useful for class upgrades!")
            if self.player.can_upgrade_class():
                print("You can now upgrade your class with 'upgrade' command!")
        else:
            self.player.add_item(item)

    # ========== COMBAT ==========
    def fight_enemy(self, *args) -> None:
        if not args:
            print("Fight what?")
            return
        input_enemy_name = ' '.join(args)
        current_room = self.rooms[self.player.current_room]
        # Find matching enemy ignoring case
        matching_enemy = None
        for e in current_room.enemies:
            if e.lower() == input_enemy_name.lower():
                matching_enemy = e
                break
        if not matching_enemy:
            print(f"There's no {input_enemy_name} here to fight!")
            return
        enemy_name = matching_enemy  # Use original case
        if not self.player.weapon:
            print("⚠️ You have no weapon! You'll have to fight with your bare fists.")
            try:
                choice = input("Continue anyway? (y/n): ").strip().lower()
                if choice not in ['y', 'yes']:
                    print("You back away from the fight.")
                    return
            except KeyboardInterrupt:
                print("\nAction interrupted.")
                return
        boss_names = ['Dark Lord', 'Arena Champion', 'Frost Titan']
        if enemy_name in boss_names:
            success = self.combat.fight_boss(enemy_name, self.player, current_room)
        else:
            success = self.combat.fight_regular_enemy(enemy_name, self.player, current_room)
        if not success:
            self.running = False

    def upgrade_class_command(self) -> None:
        if not self.player.can_upgrade_class():
            if self.player.level < 5:
                print(f"You need level 5 to upgrade. (Currently level {self.player.level})")
            elif self.player.class_tier >= 3:
                print("You've reached maximum class tier!")
            return
        current_title = self.player.get_class_title()
        next_title = self.player.get_next_class_title()
        print(f"\n🌟 CLASS UPGRADE AVAILABLE!")
        print(f"Current: {current_title} (Tier {self.player.class_tier})")
        print(f"Upgrade to: {next_title} (Tier {self.player.class_tier + 1})")
        print("\nBenefits:")
        print("• +5 to all stats")
        print("• +30 maximum health")
        print("• +25 maximum mana")
        print("• Full heal and mana restore")
        print("• +5% higher rarity weapon spawn chance")
        try:
            choice = input(f"\nUpgrade to {next_title}? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                if self.player.upgrade_class():
                    print("Class upgrade successful!")
                else:
                    print("Upgrade failed.")
            else:
                print("You decide to wait.")
        except KeyboardInterrupt:
            print("\nAction interrupted.")

    # ========== SAVE/LOAD SYSTEM ==========
    def save_game(self) -> None:
        try:
            save_data = {
                'version': GameConstants.VERSION,
                'player': self.player.to_dict(),
                'rooms': {
                    room_name: {
                        'items': room.items,
                        'enemies': room.enemies,
                        'visited': room.visited,
                        'hidden_items': room.hidden_items
                    } for room_name, room in self.rooms.items()
                },
                'room_layout': self.room_layout
            }
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"✅ Game saved successfully to {self.save_file}!")
        except Exception as e:
            logging.error(f"Save error: {str(e)}")
            print(f"❌ Error saving game: {e}")

    def load_game(self) -> bool:
        try:
            if not os.path.exists(self.save_file):
                return False
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            if save_data.get('version') != GameConstants.VERSION:
                print(f"⚠️ Save file version {save_data.get('version')} does not match game version {GameConstants.VERSION}.")
                print("Starting new game instead.")
                return False
            self.player = Player.from_dict(save_data['player'])
            if self.player.weapon and self.player.weapon.get('special') == 'instant_kill':
                if self.player.weapon.get('uses_remaining', 0) <= 0:
                    print("⚠️ Your Golden Gun has depleted. It crumbles to dust...")
                    self.player.weapon = None
            self.room_layout = save_data.get('room_layout', {})
            if self.room_layout:
                room_templates = RoomTemplates.get_all_templates()
                self.rooms = {}
                for room_id, template in room_templates.items():
                    exits = self.room_layout.get(room_id, {})
                    hidden = template.get('hidden_items', {})
                    self.rooms[room_id] = Room(
                        template['name'],
                        template['description'],
                        items=template['items'].copy(),
                        exits=exits,
                        enemies=template['enemies'].copy(),
                        hidden_items=hidden.copy()
                    )
            else:
                print("⚠️ Old save file detected. Generating new dungeon layout...")
                self.rooms = self._create_procedural_world()
            for room_name, room_data in save_data['rooms'].items():
                if room_name in self.rooms:
                    self.rooms[room_name].items = room_data['items']
                    self.rooms[room_name].enemies = room_data['enemies']
                    self.rooms[room_name].visited = room_data['visited']
                    self.rooms[room_name].hidden_items = room_data.get('hidden_items', {})
            print(f"✅ Game loaded! Welcome back, {self.player.name}!")
            return True
        except Exception as e:
            logging.error(f"Load error: {str(e)}")
            print(f"❌ Error loading game: {e}")
            print("Save file may be corrupted. Try starting a new game.")
            return False

    def quit_game(self) -> None:
        try:
            save_choice = input("\nSave before quitting? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                self.save_game()
        except KeyboardInterrupt:
            print("\nInput interrupted. Quitting without saving.")
        print(f"\nThanks for playing, {self.player.name if self.player else 'Adventurer'}!")
        print("See you next time!")
        self.running = False

#################################################################################
# MAIN ENTRY POINT
#################################################################################
def main():
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