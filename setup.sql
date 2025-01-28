CREATE TABLE Archetype (
    arch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    arch_name TEXT NOT NULL,
    arch_type TEXT NOT NULL
)
CREATE TABLE Card (
	card_id	INTEGER,
	card_cost	INTEGER NOT NULL,
	card_name	TEXT NOT NULL,
	card_rarity	BLOB NOT NULL CHECK(card_rarity IN ('Common', 'Rare', 'Epic', 'Legendary', 'Champion')),
	card_type	BLOB NOT NULL CHECK(card_type IN ('Building', 'Spell', 'Troop')),
	card_is_win_condition	REAL NOT NULL,
	PRIMARY KEY(card_id AUTOINCREMENT)
)

CREATE TABLE CardItem (
    carditem_id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    carditem_level INTEGER NOT NULL CHECK (carditem_level BETWEEN 1 AND 15),
    carditem_count INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    FOREIGN KEY (card_id) REFERENCES Card(card_id),
    FOREIGN KEY (player_id) REFERENCES Player(player_id)
)

CREATE TABLE Deck (
    deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    arch_id INTEGER NOT NULL,
    FOREIGN KEY (arch_id) REFERENCES Archetype(arch_id)
)

CREATE TABLE DeckCard (
    deck_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    deckcard_slot INTEGER NOT NULL CHECK (deckcard_slot BETWEEN 1 AND 8),
    PRIMARY KEY (deck_id, card_id),
    FOREIGN KEY (deck_id) REFERENCES Deck(deck_id),
    FOREIGN KEY (card_id) REFERENCES Card(card_id)
)

CREATE TABLE Player (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL
)

CREATE TABLE PlayerDeck (
    player_id INTEGER NOT NULL,
    deck_id INTEGER NOT NULL,
    playerdeck_slot INTEGER NOT NULL CHECK (playerdeck_slot BETWEEN 1 AND 8),
    PRIMARY KEY (player_id, deck_id),
    FOREIGN KEY (player_id) REFERENCES Player(player_id),
    FOREIGN KEY (deck_id) REFERENCES Deck(deck_id)
)
