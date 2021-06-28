import aiosqlite

path = "data/umi.db"

# TODO: Move from sqlite to Postgresql

async def create_table(name: str, rows: str):
    async with aiosqlite.connect(path) as db:
        await db.execute(f'''CREATE TABLE IF NOT EXISTS "{name}"({rows})''')


async def create_database_base():
    await create_table("global", 'uID INTEGER, reputation INTEGER, description INTEGER, repTimeout TEXT, UNIQUE(uID)')
    await create_table("levels", 'uID INTEGER, gID INTEGER, level INTEGER, exp INTEGER, nextLvlExp INTEGER')
    await create_table("settings", "gID INTEGER, prefix TEXT, UNIQUE(gID)")


async def insert(table, values):
    """Creates a new item in database"""
    async with aiosqlite.connect(path) as db:
        await db.execute(f"INSERT OR IGNORE INTO {table} VALUES ({values})")
        await db.commit()
    

async def get(item, table, field):
    """Returns an item"""
    async with aiosqlite.connect(path) as db:
        cursor = await db.execute(f"SELECT {item} FROM {table} WHERE {field}")
        row = await cursor.fetchone()

    try:
        return row[0]
    except TypeError:
        return None


async def getmany(item, table, field = None):
    """Returns a list of items"""
    if field:
        fmt = f"SELECT {item} FROM {table} WHERE {field}"
    else:
        fmt = f"SELECT {item} FROM {table}"

    async with aiosqlite.connect(path) as db:
        cursor = await db.execute(fmt)
        rows = await cursor.fetchall()

    return rows if len(rows) != 0 else None


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


async def check_existence(item, table, field):
    if await get(item, table, field):
        return True
    return False
    