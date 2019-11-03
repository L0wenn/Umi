import aiosqlite

database = None


async def connect():
    global database
    database = await aiosqlite.connect("umi.db")
    

async def insert(table, values):
    """Creates a new item in database"""
    await database.execute(f"INSERT INTO {table} VALUES ({values})")
    return await database.commit()
    

async def get(predicate, table, field):
    """Returns an item"""
    cursor = await database.execute(f"SELECT {predicate} FROM {table} WHERE {field}")
    row = await cursor.fetchone()
    return row[0]


async def getmany(predicate, table, field = None):
    """Returns a list of items"""
    if field:
        fmt = f"SELECT {predicate} FROM {table} WHERE {field}"
    else:
        fmt = f"SELECT {predicate} FROM {table}"

    cursor = await database.execute(fmt)
    rows = await cursor.fetchall()
    return rows


async def update(table, predicate, field):
    """Updates an item"""
    await database.execute(f"UPDATE {table} SET {predicate} WHERE {field}")
    return await database.commit()


async def delete(table, predicate):
    """Deletes an item"""
    await database.execute(f"DELETE FROM {table} WHERE {predicate}")
    return await database.commit()
    