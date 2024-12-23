from flask import Flask, jsonify, render_template, request
from classes.USDBScraper import USDBScraper
from classes.USDBScraperDB import USDBScraperDB
from classes.USDBUtility import USDBUtility
import os
import json
import asyncio
import threading

# Load Config-File
usdbUtilityObj = USDBUtility()
config = usdbUtilityObj.load_config('config.json')

app = Flask(__name__)

async def background_task():    
    """
    Eine asynchrone Funktion, die in einem Zyklus läuft und alle 60 Sekunden eine Aufgabe ausführt.
    """

    usdbUtilityObj = USDBUtility()
    databaseObj = USDBScraperDB("usdb_scrapper.db")    

    while True:
        print("Hintergrundaufgabe wird ausgeführt...")

        # Create Database Object        
        query_song_list = databaseObj.fetch_all_songs()
        
        # Loop all songs that STATUS = 0
        for song in query_song_list:
            usdb_song_id = song.get("USDB_SONG_ID")

            # STATUS 0  ->  Scrapping
            if song.get("STATUS") == 0:                
                print("Get Song Informationen from Database")
                
                # Update Song Status -> 1 (Scraping)
                databaseObj.update_song_status(usdb_song_id, 1)

                # USDB Config
                usdb_config = config["USDBScraper"]                    

                # 1. Anhand der USDB-ID die Song Informationen scrapen und in die Datenbank speichern                                                
                usdbScraperObject = USDBScraper("./chromedriver-win64/chromedriver.exe", usdb_config.get("USERNAME", ""), usdb_config.get("PASSWORD", "")) 
                song_infos = usdbScraperObject.srape_song(usdb_song_id)  
                databaseObj.upate_song_by_id(usdb_song_id, song_infos.get("YOUTUBE_URL", ""), song_infos.get("SONG_TEXT", ""), 2)

            # STATUS 2  -> Scraping Completed
            if song.get("STATUS") == 2:
                print("Download Youtube Video / Download mp3 / Create Folder")

                # Update Song Status -> 3 (Downloading / Create Folder)
                databaseObj.update_song_status(usdb_song_id, 3)

                # 1. Ordner erstellen                
                song_folder_name = song.get("SONG_INTERPRET") + "-" + song.get("SONG_TITLE")  
                output_path  = usdbUtilityObj.create_song_folder(song_folder_name)
                media_file_path = output_path + "/" + song_folder_name

                # 2. Lyrics in eine Textdatei speichern (Dateiname: SONG_INTERPRET - SONG_TITLE.txt)    
                song_text = song.get('SONG_ULTRA_STAR_LYRICS')
                # Datei speichern
                output_file = media_file_path + ".txt"
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(song_text)
                
                # 5. Anhand YOUTUBE_LINK das Video und die MP3 herunterladen und wie oben beschrieben benennen    
                usdbUtilityObj.youtube_to_mp3(song.get('SONG_YT_VIDEO_LINK'), media_file_path)    
                usdbUtilityObj.youtube_to_mp4(song.get('SONG_YT_VIDEO_LINK'), media_file_path)
                
                # 6. COVER herunterladen und umbenennen    
                image_path = output_path + "/" + song_folder_name + ".jpg"
                usdbUtilityObj.download_image(song.get('SONG_COVER_URL'), image_path)    

                # Update Song Status -> 3 (Downloading / Create Folder)
                databaseObj.update_song_status(usdb_song_id, 4)

                # prepare Song for UltraStar
                usdbUtilityObj.prepare_song_ultra_star(output_path)

        
        await asyncio.sleep(20)  # 60 Sekunden warten

def start_background_task():
    """
    Startet die asynchrone Hintergrundaufgabe in einem separaten Thread.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(background_task())

# Serverseitige Liste, um die Song-IDs zu speichern
download_list = []

# PAGES
@app.route('/', methods=['GET'])
def page_home():
    """Gibt die Songliste als JSON zurück."""

    # SONGS = usdbScraperObject.search_song("Willst du")

    # return jsonify(SONGS)
    # return render_template('songs.html', songs=SONGS)
    return render_template('home.html')

@app.route('/search-song', methods=['GET'])
def page_search_song():
    """Gibt die Songliste als JSON zurück."""

    # SONGS = usdbScraperObject.search_song("Willst du")

    # return jsonify(SONGS)
    # return render_template('songs.html', songs=SONGS)
    return render_template('songs.html')

@app.route('/query-list', methods=['GET'])
def page_query_list():

    # Databse Object
    databaseObj = USDBScraperDB("usdb_scrapper.db")
    query_song_list = databaseObj.fetch_all_songs()  
    
    return render_template('query_list.html', songs=query_song_list)

@app.route('/downloads', methods=['GET'])
def page_downloads():

    # Databse Object
    databaseObj = USDBScraperDB("usdb_scrapper.db")    
    downloaded_songs = databaseObj.get_downloaded_songs() 

    return render_template('downloads.html', downloaded_songs=downloaded_songs)

# FUNCTIONS
@app.route('/search', methods=['GET'])
def search():
    """Führt die Suche durch und gibt die Ergebnisse als JSON zurück."""
    query = request.args.get('query', '').lower()
    filter_by = request.args.get('filter', 'SONG_TITEL')        

    # USDB Config
    usdb_config = config["USDBScraper"]    
    
    usdbScraperObject = USDBScraper("./chromedriver-win64/chromedriver.exe", usdb_config.get("USERNAME", ""), usdb_config.get("PASSWORD", "")) 
    SONGS = usdbScraperObject.search_song(query)

    return jsonify(SONGS)

@app.route('/query_list_action', methods=['POST'])
def function_query_list_action():
    usdb_song_id = request.json.get('USDB_SONG_ID')
    status = request.json.get('STATUS')

    databaseObj = USDBScraperDB("usdb_scrapper.db")
    databaseObj.update_song_status(usdb_song_id, status)

    return jsonify({"USDB_SONG_ID": f"{usdb_song_id}", "STATUS": f"{status}"})

@app.route('/add_to_download', methods=['POST'])
def add_to_download():
    """Fügt einen Song mit allen Details zur Download-Liste hinzu."""
    song_id = request.json.get('SONG_ID')
    song_interpret = request.json.get('SONG_INTERPRET')
    song_title = request.json.get('SONG_TITEL')

    song_cover_url = "https://usdb.animux.de/data/cover/" + song_id + ".jpg"

    # Song in die Datenbank speichern
    databaseObj = USDBScraperDB("usdb_scrapper.db")
    databaseObj.insert_song_query(song_id, song_title, song_interpret, song_cover_url)

    # Validiere die Daten
    if not (song_id and song_interpret and song_title):
        return jsonify({"status": "error", "message": "Ungültige Song-Daten"}), 400

    # Überprüfen, ob der Song bereits in der Liste ist
    for song in download_list:
        if song['SONG_ID'] == song_id:
            return jsonify({"status": "info", "message": f"Song mit ID {song_id} ist bereits in der Liste."})

    # Song zur Liste hinzufügen
    download_list.append({
        "SONG_ID": song_id,
        "SONG_INTERPRET": song_interpret,
        "SONG_TITEL": song_title
    })
    print(f"Download-Liste aktualisiert: {download_list}")
    return jsonify({"status": "success", "message": f"Song {song_title} hinzugefügt.", "download_list": download_list})

@app.route('/remove_from_download', methods=['POST'])
def remove_from_download():
    """Entfernt einen Song aus der Download-Liste."""
    song_id = request.json.get('SONG_ID')

    # Validiere die Song-ID
    if not song_id:
        return jsonify({"status": "error", "message": "Keine Song-ID übermittelt"}), 400

    # Suche und entferne den Song
    # global download_list
    download_list = [song for song in download_list if song['SONG_ID'] != int(song_id)]

    print(f"Download-Liste nach Entfernung: {download_list}")
    return jsonify({"status": "success", "message": f"Song mit ID {song_id} entfernt.", "download_list": download_list})


@app.route('/get_query_list', methods=['GET'])
def get_download_list():
    """Gibt die aktuelle Download-Liste zurück."""
    return jsonify(download_list)

if __name__ == '__main__':

    # HIER
    
    # Check config
    if config:
        # set Application Settings from config-file
        web_server_config = config["WEBSEVER"]
        ip = web_server_config.get("IP", "127.0.0.1") # IP from Setting or Fallback 127.0.0.1
        port = web_server_config.get("PORT", 5000) # Port fron Settubg or Fallback 5000
        debug = web_server_config.get("DEBUG", True) # Debug from Setting or Fallback True

         # Starte die Hintergrundaufgabe in einem separaten Thread
        background_thread = threading.Thread(target=start_background_task, daemon=True)
        background_thread.start()

        app.run(host=ip, port=port, debug=debug)
    else:
        print("Can't find config.json!")