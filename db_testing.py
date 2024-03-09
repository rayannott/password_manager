import sqlite3


def run_db():
    conn = sqlite3.connect('lite.db')
    cur = conn.cursor()
    # cur.execute(
    #     """
    #     CREATE TABLE folders (
    #         id INTEGER PRIMARY KEY,
    #         name TEXT,
    #         unlocked BOOLEAN,
    #         key_hash TEXT
    #     )
    #     """
    # )

    # cur.execute(
    #     """
    #     INSERT INTO folders VALUES
    #         (1, 'folder1'),
    #         (2, 'folder2'),
    #         (3, 'folder3')
    #     """
    # )
    # res = cur.execute(
    #     """
    #     SELECT * FROM folders
    #     """
    # ); print(res.fetchall())
    
    # remove a row:
    # cur.execute("DELETE FROM folders WHERE folder_id = 2")
    conn.commit()
    conn.close()


def setup_create():
    with sqlite3.connect('lite.db') as conn:
        cur = conn.cursor()
        # cur.execute(
        #     """
        #     CREATE TABLE folders (
        #         id INTEGER PRIMARY KEY,
        #         name TEXT,
        #         unlocked BOOLEAN,
        #         key_hash TEXT
        #     )
        #     """
        # )
        # cur.execute(
        #     """
        #     CREATE TABLE entries (
        #         id INTEGER PRIMARY KEY,
        #         folder_id INTEGER,
        #         name TEXT,
        #         login TEXT,
        #         password TEXT,
        #         notes TEXT
        #     )
        #     """
        # )
        # cur.execute(
        #     """
        #     CREATE TABLE logs (
        #         id INTEGER PRIMARY KEY,
        #         folder_id INTEGER,
        #         date DECIMAL,
        #         action TEXT
        #     )
        #     """
        # )


def setup_insert():
    with sqlite3.connect('lite.db') as conn:
        cur = conn.cursor()
        # cur.execute(
        #     """
        #     INSERT INTO folders VALUES
        #         (1, 'cards', 1, ''),
        #         (2, 'emails', 1, ''),
        #         (3, 'social', 1, ''),
        #         (4, 'studies', 1, ''),
        #         (5, 'streaming', 1, '')
        #     """
        # )
        # cur.execute(
        #     """
        #     INSERT INTO entries VALUES
        #         (1, 1, 'visa-main', '4987-7911-7844-1147', 'pin=4498', 'cvv=195 valid_until=11/28'),
        #         (2, 1, 'visa-secondary', '1432-6345-8236-2564', 'pin=1423', 'cvv=123 valid_until=05/25')
        #     """
        # )
        # cur.execute(
        #     """
        #     INSERT INTO entries VALUES
        #         (3, 2, 'yahoo', 'sample@yahoo.com', 'mypAss1&*', ''),
        #         (4, 2, 'gmail', 'mail_here@gmail.com', 'qkittenQ13', 'some notes')
        #     """
        # )
        cur.execute(
            """
            INSERT INTO entries VALUES
                (5, 3, 'facebook', 'user123', 'pass123', '')
            """
        )


if __name__ == '__main__':
    # setup_create()
    setup_insert()
