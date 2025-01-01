import sqlite3

class USDBScraperDB:
    def __init__(self, db_path):
        """
        Initialisiert die Datenbankverbindung.
        :param db_path: Pfad zur SQLite-Datenbankdatei
        """
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row  # Damit wir Ergebnisse als Dictionary erhalten
        self.cursor = self.connection.cursor()

    def insert_song_query(self, USDB_SONG_ID, SONG_TITLE, SONG_INTERPRET, SONG_COVER_URL):
        query = """
        INSERT INTO QUERY_LIST (
            USDB_SONG_ID,
            SONG_TITLE,
            SONG_INTERPRET,
            SONG_COVER_URL,
            STATUS) 
            VALUES (?, ?, ?, ?, -2);
        """

        try:
            self.cursor.execute(query, (USDB_SONG_ID, SONG_TITLE, SONG_INTERPRET, SONG_COVER_URL))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError as e:
            return False


    def insert_song(self, song_title, song_interpret, song_genre, song_ultra_star_lyrics, song_yt_video_link, song_mp3_filename, song_mp4_filename, status):
        """
        Fügt einen Song in die Tabelle QUERY_LIST ein.
        :param song_name: Name des Songs
        :param song_interpret: Interpret des Songs
        :param song_genre: Genre des Songs
        :param song_ultra_star_lyrics: Lyrics im UltraStar-Format (als BLOB)
        :param song_yt_video_link: YouTube-Link des Videos
        :param song_mp3_filename: Dateiname der MP3
        :param song_mp4_filename: Dateiname der MP4
        :param status: Status des Eintrags (z. B. 0 = inaktiv, 1 = aktiv)
        """
        query = """
        INSERT INTO QUERY_LIST (
            SONG_TITLE, SONG_INTERPRET, SONG_GENRE, SONG_ULTRA_STAR_LYRICS,
            SONG_YT_VIDEO_LINK, SONG_MP3_FILENAME, SONG_MP4_FILENAME, STATUS
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (song_title, song_interpret, song_genre, song_ultra_star_lyrics,
                                    song_yt_video_link, song_mp3_filename, song_mp4_filename, status))
        self.connection.commit()

    def upate_song_by_id(self, song_id, song_yt_video_link, song_ultra_star_lyrics, status):
        """
        Songinformationen updaten
        """
        query = """
        UPDATE QUERY_LIST
            SET SONG_YT_VIDEO_LINK = ?,
            SONG_ULTRA_STAR_LYRICS = ?,
            STATUS = ?
        WHERE USDB_SONG_ID = ?
        """
        self.cursor.execute(query, (song_yt_video_link, song_ultra_star_lyrics, status, song_id))
        self.connection.commit()

    def update_song_status(self, song_id, status):
        """
        Update Song Status By Song ID
        """
        query = """
        UPDATE QUERY_LIST
            SET STATUS = ?
        WHERE USDB_SONG_ID = ?        
        """
        self.cursor.execute(query, (status, song_id))
        self.connection.commit()

    def delete_song_by_id(self, song_id):
        """
        Löscht einen Song aus der Tabelle QUERY_LIST.
        :param song_id: ID des Songs
        """
        query = "DELETE FROM QUERY_LIST WHERE USDB_SONG_ID = ?"
        self.cursor.execute(query, (song_id,))
        self.connection.commit()

    def fetch_all_songs(self):
        """
        Liest alle Songs aus der Tabelle QUERY_LIST aus.
        :return: Liste von Songs als Dictionaries
        """
        query = "SELECT * FROM QUERY_LIST WHERE STATUS < 4 and STATUS <> -3"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]  # Wandelt Row-Objekte in Dictionaries um

    def get_downloaded_songs(self):
        """
        Liest alle Songs aus der Tabelle QUERY_LIST aus.
        :return: Liste von Songs als Dictionaries
        """
        query = "SELECT * FROM QUERY_LIST WHERE STATUS = 4 ORDER BY QUERY_LIST_ID desc"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]  # Wandelt Row-Objekte in Dictionaries um

    def get_song_by_id(self, song_id):
        query = "SELECT * FROM QUERY_LIST WHERE USDB_SONG_ID = ?"
        self.cursor.execute(query, (song_id,))
        row = self.cursor.fetchone()
        
        # Prüfen, ob ein Song gefunden wurde
        if row:
            return {
                "SONG_ID": row[1],
                "SONG_TITEL": row[2],
                "SONG_INTERPRET": row[3],                
                "SONG_COVER_URL": row[4],
                "SONG_ULTRA_STAR_LYRICS": row[6],
                "SONG_YT_VIDEO_LINK": row[8],
                "STATUS": row[11],
            }
        else:
            return None

    def close(self):
        """
        Schließt die Datenbankverbindung.
        """
        self.connection.close()
