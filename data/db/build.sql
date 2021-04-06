CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY KEY,
	Prefix text DEFAULT "+"
);

CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY,
	UserName text,
	HP integer DEFAULT 100,
	MP integer DEFAULT 50,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP,
	Luck integer DEFAULT 50,
	StatusPoint integer DEFAULT 0,
	Strength integer DEFAULT 0,
	Intelligence integer DEFAULT 0,
	Dexerity integer DEFAULT 0,
	Yen integer DEFAULT 500,
	Nadecoin integer DEFAULT 0,
	Items text  '{}',
	Charas text  '{}'
);

CREATE TABLE IF NOT EXISTS mutes (
	UserID integer PRIMARY KEY,
	RoleIDs text,
	EndTime text
);

CREATE TABLE IF NOT EXISTS starboard (
	RootMessageID integer PRIMARY KEY,
	StarMessageID integer,
	Stars integer DEFAULT 1
);