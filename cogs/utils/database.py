import aiosqlite

path = "data/umi.db"

async def create_database():
    async with aiosqlite.connect(path) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS "levelsGlobal"(
        "uID"	INTEGER,
        "level"	INTEGER,
        "exp"	INTEGER,
        "nextLvlExp"	INTEGER,
        "reputation"	INTEGER,
        "description"	INTEGER,
        "repTimeout"	TEXT)''')

        await db.execute('''CREATE TABLE IF NOT EXISTS "levelsGuilds"(
        "uID"	INTEGER,
        "gID"   INTEGER,
        "level"	INTEGER,
        "exp"	INTEGER,
        "nextLvlExp"	INTEGER)''')

        await db.execute('''CREATE TABLE IF NOT EXISTS "levelsRewards"(
        "gID"	INTEGER,
        "rID"   INTEGER,
        "level"	INTEGER''')


async def insert(table, values):
    """Creates a new item in database"""
    async with aiosqlite.connect(path) as db:
        await db.execute(f"INSERT INTO {table} VALUES ({values})")
        await db.commit()
    

async def get(item, table, field):
    """Returns an item"""
    async with aiosqlite.connect(path) as db:
        cursor = await db.execute(f"SELECT {item} FROM {table} WHERE {field}")
        row = await cursor.fetchone()

    return row[0]


async def getmany(item, table, field = None):
    """Returns a list of items"""
    if field:
        fmt = f"SELECT {item} FROM {table} WHERE {field}"
    else:
        fmt = f"SELECT {item} FROM {table}"

    async with aiosqlite.connect(path) as db:
        cursor = await db.execute(fmt)
        rows = await cursor.fetchall()

    return rows


async def update(table, item, field):
    """Updates an item"""
    async with aiosqlite.connect(path) as db:
        await db.execute(f"UPDATE {table} SET {item} WHERE {field}")
        await db.commit()


async def delete(table, item):
    """Deletes an item"""
    async with aiosqlite.connect(path) as db:
        await db.execute(f"DELETE FROM {table} WHERE {item}")
        await db.commit()
    