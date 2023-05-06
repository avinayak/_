import sqlite3

def open_connection():
    """ Open a connection to the database """
    return sqlite3.connect("images.db")

def maybe_create_table():
    """ Create a table in the database """
    conn = open_connection()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS images (fhash TEXT PRIMARY KEY, path TEXT, phash TEXT)")
    conn.commit()
    conn.close()


def fetch_all_images():
    """ Fetch all images from the database """
    conn = open_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM images")
    all_images = c.fetchall()
    conn.close()
    return all_images


def insert_image(image):
    (fhash, path, phash) = image
    """ Insert an image into the database """
    conn = open_connection()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO images VALUES (?, ?, ?)",
              (str(fhash), str(path), str(phash)))
    conn.commit()
    conn.close()


def does_image_exist(path):
    """ Check if an image exists in the database """
    conn = open_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM images WHERE path = ?", [str(path)])
    exists = c.fetchone() is not None
    conn.close()
    return exists
