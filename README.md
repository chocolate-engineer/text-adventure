# text-adventure


## COMPLETE FEATURE LIST

### MULTI-FLOOR DUNGEON SYSTEM:
- Ten unique floors with procedurally generated layouts (expanded from 3)
- Each floor contains 10-15 randomly connected rooms (expanded from 8-10)
- Floors connected via ancient stairways (use 'up'/'down' commands)
- One unique boss per floor with escalating difficulty
- Floor progression: Dungeon → Crypt → Elemental → Dark Magic → Cosmic
- Each playthrough has completely different room layouts

### CHARACTER CLASSES & PROGRESSION:
- Three playable classes: Warrior, Mage, Rogue
- Each class has unique stats, health, mana, and weapon types
- Three-tier class progression system (upgrades at levels 5, 10, 15)
  - Tier 1: Warrior/Mage/Rogue
  - Tier 2: Berserker/Sorcerer/Assassin
  - Tier 3: Paladin/Archmage/Shadow Master
- Class upgrades grant: +5 all stats, +30 health, +25 mana, +5% rare drops
- Different inventory capacities and growth rates per class

### WEAPON SYSTEM:
- Three starting weapons per class (game randomly shows 3 to choose from)
  - Warrior weapons: 18-22 base damage (melee type)
  - Mage weapons: 13-16 base damage (magic type)
  - Rogue weapons: 14-18 base damage (stealth type)
- Six rarity tiers with damage multipliers:
  - Common (1.0x), Uncommon (1.3x), Rare (1.6x)
  - Epic (2.0x), Legendary (2.5x), Mythic (3.0x)
- Ultra-rare Golden Gun (0.02% drop chance):
  - Instant kill on any enemy
  - 6 uses before it crumbles to dust
  - Divine rarity (999x multiplier)
- Weapons scale with player level and rarity boosts
- Class-specific weapon spawns (warriors get melee, mages get magic, etc.)

### COMBAT & LEVELING:
- Turn-based combat system with strategic choices
- Player actions: Attack, Magic (costs mana), Defend, Use Potion
- Enemy count balanced for proper level progression per floor
- Each floor has 15-25 enemies before boss encounter (scaled up)
- Experience required increases per level (base 100, 1.4x multiplier)
- Boss fights feature special attacks and health-based mechanics
- Bosses reward legendary weapons, stat bonuses, and full heal

### ENHANCED ENEMY SYSTEM (NEW):
- 20+ unique enemy types (expanded from 7)
- Enemies organized by floor themes:
  - Floors 1-2: Dungeon/Prison (Rats, Goblins, Skeletons, Guards)
  - Floors 3-4: Crypt/Necromancy (Wraiths, Ghouls, Dark Mages)
  - Floors 5-6: Elemental (Fire, Ice, Lightning, Stone)
  - Floors 7-8: Dark Magic (Demons, Cultists, Void Spawn)
  - Floors 9-10: Cosmic/Ancient (Guardians, Horrors, Titans)
- NO DUPLICATE enemies per room (unique spawning system)
- Each enemy has descriptive text that appears in combat

### ATMOSPHERIC DESCRIPTIONS (NEW):
- Every room has two-part descriptions:
  - Main description of the physical space
  - Atmospheric text that sets the mood
- Enhanced enemy introductions with flavor text
- Thematic consistency per floor

### TEN BOSS FIGHTS (EXPANDED):
- Floor 1: Arena Champion (gladiator theme)
- Floor 2: Necromancer Lord (death magic)
- Floor 3: Crypt Overlord (undead king)
- Floor 4: Shadow King (darkness incarnate)
- Floor 5: Flame Lord (fire elemental)
- Floor 6: Frost Titan (ice giant)
- Floor 7: Demon Prince (abyssal power)
- Floor 8: Void Archon (reality warper)
- Floor 9: Primordial Beast (ancient titan)
- Floor 10: Reality Breaker (cosmic horror)
- Each boss has unique legendary weapons for all 3 classes

### PUZZLE & EXPLORATION SYSTEM (ORIGINAL FEATURES):
- Interactive special items with 'use' command:
  - Torch: Place in Hidden Alcove sconce to unlock secret vault
  - Rusty Key: Opens Locked Vault chest for treasure cache
  - Ancient Medallion: Offer at Sacred Shrine for permanent stat boosts
  - Old Map: View dungeon layout
  - Bone Key: Quest item for crypt areas
- Secret room system with legendary loot
- Special room types: Hidden Alcove, Locked Vault, Sacred Shrine
- Context-sensitive interactions (items work in specific rooms)

### ITEM MANAGEMENT - SEPARATE COMMANDS:
- `heal` - Use healing items (health potions restore HP, magic scrolls restore mana)
- `exp` or `experience` - Use experience items (gems give instant XP)
- `equip` or `wear` - Equip wearable stat-boosting items
- `use <item>` - Use special interactive items (torch, keys, medallion)
- Items LOCKED until all enemies in room are defeated
- Cannot pick up loot while enemies present (strategic gameplay)
- Inventory capacity increases with level and class tier

### ENHANCED DROP RATES:
- 40% chance for weapon cache drops from defeated enemies
- 35% base item drop chance (scales with weapon rarity)
- Multiple weapon caches per room (2-3 in armories/warrior halls)
- Approximately 10-15 weapon opportunities per floor
- Golden Gun can drop from any weapon cache (0.02% chance)
- 60% gold coin drop rate from enemies

### CONTEXT-AWARE HELP SYSTEM (NEW):
- Help command shows only relevant actions
- Combat commands appear only when enemies present
- Item commands adjust based on inventory contents
- Shop command only shows when you have gold coins
- Special item usage hints when you have interactive items
- No menu clutter - clean, situational interface

### FUZZY COMMAND MATCHING:
- Typo-tolerant command system using similarity matching
- "inventroy" → suggests "inventory"
- "atack goblin" → suggests "attack"
- Shortcuts available: 'inv', 'n/s/e/w', 'get', 'drop', etc.
- Direction commands work standalone: 'north', 'south', 'east', 'west'
- Cutoff threshold: 60% similarity for matches

### GOLD COIN ECONOMY:
- Enemies drop 2-10 gold coins (60% drop rate)
- Merchant shop available throughout dungeon
- Purchase healing items, stat boosters, experience gems
- Prices scale from 5g (health potion) to 40g (soul crystal)
- Shop inventory adjusts by class (mages can buy magic scrolls)

### SAVE/LOAD SYSTEM:
- Complete game state persistence to JSON file
- Saves: player stats, inventory, floor layouts, room states
- Version checking prevents corrupted saves from old versions
- Auto-saves progress including visited rooms and defeated enemies
- Golden Gun uses tracked and restored properly
- Secret room unlock states preserved

### INTERACTIVE MAP:
- View entire dungeon with 'map' command
- Shows all ten floors separately
- Tracks visited rooms with >>> current location marker
- Displays available exits for each discovered room
- Progress counter: visited/total rooms per floor
- Undiscovered room hints

## ROOM TYPES (30+ Templates, Thematically Organized)

### FLOORS 1-2: DUNGEON/PRISON THEME
- Damp Prison Cell - Rusted bars and decay
- Guard Barracks - Abandoned military quarters
- Torture Chamber - Implements of pain
- Long Hallway - Common corridor

### FLOORS 3-4: CRYPT/NECROMANCY THEME
- Ancient Crypt - Stone sarcophagi
- Necromancer's Study - Forbidden tomes
- Burial Chamber - Rows of burial niches
- Tomb passages

### FLOORS 5-6: ELEMENTAL THEME
- Inferno Chamber - Lava pools and heat
- Frozen Cavern - Ice and cold
- Storm Hall - Lightning and electricity
- Elemental nexus points

### FLOORS 7-8: DARK MAGIC THEME
- Ritual Chamber - Blasphemous symbols
- Shadow Realm Gate - Portal to darkness
- Corrupted Sanctum - Desecrated holy sites
- Cultist hideouts

### FLOORS 9-10: COSMIC/ANCIENT THEME
- Primordial Vault - Prehistoric architecture
- Cosmic Observatory - Reality-bending spaces
- Hall of Eternity - Time anomalies
- Ancient monuments

### SPECIAL ROOMS (ALL FLOORS):
- Treasure Room - Guarded wealth
- Hidden Alcove - Secret room trigger (torch puzzle)
- Locked Vault - Key puzzle room
- Sacred Shrine - Medallion offering puzzle
- Ancient Armory - Weapon caches
- Boss Chambers - Ten unique arenas


## COMPLETE ENEMY ROSTER (20+ TYPES)

### FLOORS 1-2 ENEMIES:
- Sewer Rat: 15 HP, 5 damage, 15 XP - Disease-ridden vermin
- Goblin: 25 HP, 8 damage, 25 XP - Small green creatures
- Skeleton: 30 HP, 10 damage, 30 XP - Animated bones
- Prison Guard: 40 HP, 12 damage, 35 XP - Corrupted guards

### FLOORS 3-4 ENEMIES:
- Armored Skeleton: 45 HP, 14 damage, 45 XP - Warrior undead
- Shadow Wraith: 50 HP, 18 damage, 55 XP - Spectral beings
- Corrupted Mage: 40 HP, 20 damage, 60 XP - Fallen spellcasters
- Ghoul: 55 HP, 16 damage, 50 XP - Flesh-eating undead

### FLOORS 5-6 ENEMIES:
- Fire Elemental: 60 HP, 22 damage, 70 XP - Living flame
- Ice Elemental: 58 HP, 20 damage, 68 XP - Crystalline cold
- Lightning Wisp: 50 HP, 25 damage, 75 XP - Crackling energy
- Stone Golem: 80 HP, 18 damage, 65 XP - Animated stone

### FLOORS 7-8 ENEMIES:
- Lesser Demon: 70 HP, 26 damage, 85 XP - Abyssal horrors
- Dark Cultist: 65 HP, 24 damage, 80 XP - Dark fanatics
- Shadow Beast: 75 HP, 28 damage, 90 XP - Monstrous predators
- Void Spawn: 80 HP, 30 damage, 95 XP - Reality aberrations

### FLOORS 9-10 ENEMIES:
- Ancient Guardian: 90 HP, 32 damage, 110 XP - Eternal sentinels
- Cosmic Horror: 85 HP, 35 damage, 120 XP - Incomprehensible beings
- Titan Spawn: 100 HP, 30 damage, 105 XP - Primordial offspring
- Celestial Knight: 95 HP, 34 damage, 115 XP - Fallen heavenly warriors

### SPECIAL ENEMY:
- Treasure Guardian: 60 HP, 20 damage, 65 XP - Magical construct


## TEN BOSS ENCOUNTERS (DETAILED)

### Floor 1 - Arena Champion:
- Health: 120 + (level × 8)
- Special: CHAMPION'S FURY
- Rewards: Gladius of Victory / Champion's Scepter / Twin Blades
- Minimum Level: 2

### Floor 2 - Necromancer Lord:
- Health: 140 + (level × 9)
- Special: DEATH CURSE
- Rewards: Soul Reaper / Death Staff / Shadow Fang
- Minimum Level: 4

### Floor 3 - Crypt Overlord:
- Health: 160 + (level × 10)
- Special: SOUL DRAIN
- Rewards: Bone Crusher / Crypt Scepter / Grave Shiv
- Minimum Level: 6

### Floor 4 - Shadow King:
- Health: 180 + (level × 11)
- Special: SHADOW STRIKE
- Rewards: Shadowbane / Dark Orb / Night Piercer
- Minimum Level: 8

### Floor 5 - Flame Lord:
- Health: 200 + (level × 12)
- Special: INFERNO
- Rewards: Flamebringer / Inferno Staff / Cinder Bow
- Minimum Level: 10

### Floor 6 - Frost Titan:
- Health: 220 + (level × 13)
- Special: GLACIAL STORM
- Rewards: Frostbane Greatsword / Staff of Eternal Winter / Icicle Piercer
- Minimum Level: 12

### Floor 7 - Demon Prince:
- Health: 240 + (level × 14)
- Special: HELLFIRE
- Rewards: Demon's Edge / Abyssal Staff / Soul Piercer
- Minimum Level: 14

### Floor 8 - Void Archon:
- Health: 260 + (level × 15)
- Special: VOID RIFT
- Rewards: Voidreaver / Reality Staff / Oblivion Blade
- Minimum Level: 16

### Floor 9 - Primordial Beast:
- Health: 280 + (level × 16)
- Special: ANCIENT WRATH
- Rewards: Titan Slayer / Primordial Staff / Beast Fang
- Minimum Level: 18

### Floor 10 - Reality Breaker:
- Health: 300 + (level × 18)
- Special: COSMIC ANNIHILATION
- Rewards: Worldender / Cosmos Staff / Reality Ripper
- Minimum Level: 20

## EXPERIENCE REQUIREMENTS (PROGRESSIVE):
- Level 1→2: 100 XP
- Level 2→3: 140 XP (1.4x multiplier)
- Level 3→4: 196 XP
- Level 4→5: 274 XP
- Level 5→6: 384 XP
- Level 6→7: 538 XP
- Level 7→8: 753 XP
- Each floor provides ~1200-1800 XP (ensures 2-3 levels per floor)


## COMMANDS REFERENCE (CONTEXT-AWARE)

### ALWAYS AVAILABLE:
- `help` - Show relevant commands for current situation
- `look` - Examine current room
- `go <direction>` - Move (north/south/east/west/up/down)
- `inventory` or `inv` - Show items
- `stats` or `status` - Show character sheet
- `map` - View dungeon layout
- `save` or `load` - Save or load game
- `quit` or `exit` - Exit game

### COMBAT (when enemies present):
- `fight <enemy>` or `attack <enemy>` - Engage in combat

### ITEMS (context-dependent):
- `take <item>` - Pick up item (after combat)
- `takeall` - Pick up all items
- `heal` - Use healing items
- `exp`/`experience` - Use experience items
- `equip`/`wear` - Equip wearable items
- `use <item>` - Use special interactive items (torch, keys, etc.)
- `switch <weapon>` - Change equipped weapon
- `discard/drop <item>` - Remove item

SHOP (when you have gold):
- `shop/buy` - Open merchant interface

PROGRESSION (when available):
- `upgrade` - Advance class tier


## TECHNICAL CLASSES & ARCHITECTURE

- GameConstants - All configuration values, enemy data, boss data, item definitions
- Player - Character state, progression, inventory, stats management
- Room - Dungeon location with items, enemies, exits, description, atmosphere
- RoomTemplates - Centralized themed room definitions for procedural generation
- WeaponSystem - Weapon generation, rarity calculation, Golden Gun mechanics
- CombatSystem - Turn-based combat, damage calculation, boss fights with all 10 bosses
- CommandHandler - Command processing with fuzzy matching
- Game - Main controller, world generation, game loop, save/load, puzzle systems


## BALANCE NOTES

- Starting weapons balanced against early enemies (goblins: 25 HP)
- ~15-25 enemies per floor ensures 2-3 level gains minimum
- Boss minimum levels: 2, 4, 6, 8, 10, 12, 14, 16, 18, 20
- Weapon rarity chances increase with level and class tier
- Magic costs 15 mana, deals 10-25 + intelligence damage
- Defending reduces boss damage by 50%
- Agility reduces incoming damage by random(1, agility/3)
- Boss health scales: base + (player_level × scaling_factor)
- Experience multiplier reduced to 1.4x (from 1.5x) for better pacing
