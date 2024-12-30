from flask import Flask, jsonify, render_template, request
from classes.USDBScraperDB import USDBScraperDB
from classes.USDBUtility import USDBUtility
from classes.USDBScraperBeatifulSoap import USDBScraperBeatifulSoap
import os
import json
import asyncio
import threading
import requests
import re
import feedparser
import logging

# Load Config-File
usdbUtilityObj = USDBUtility()
config = usdbUtilityObj.load_config('config.json')

app = Flask(__name__)

# Create Flask Logger
flask_logger = logging.getLogger('flask_logger')
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', filename='flask_scraper.log', encoding='utf-8', level=logging.DEBUG)


async def background_task():    
    """    
    Asyncrone function, that runs in a cycle and execute a task every 20 seconds.
    """

    usdbUtilityObj = USDBUtility()
    databaseObj = USDBScraperDB("usdb_scrapper.db")    

    while True:        
        flask_logger.debug("Background Task is running...")

        # Create Database Object        
        query_song_list = databaseObj.fetch_all_songs()
        
        # Loop all songs that STATUS = 0
        for song in query_song_list:
            usdb_song_id = song.get("USDB_SONG_ID")

            # STATUS 0  ->  Scrapping
            if song.get("STATUS") == 0:                                
                print("STATUS 0 -> Get Song Information from Database - USDB_SONG_ID: " + str(usdb_song_id))
                flask_logger.debug("STATUS 0 -> Get Song Information from Database - USDB_SONG_ID: " + str(usdb_song_id))
                
                # Update Song Status -> 1 (Scraping)
                databaseObj.update_song_status(usdb_song_id, 1)

                # USDB Config to Variable
                usdb_config = config["USDBScraper"]                    

                flask_logger.debug("USDB Scraping start...")

                # Scraping Song Information from USDB -> OLD                                
                usdbScraperObject = USDBScraperBeatifulSoap(usdb_config.get("USERNAME", ""), usdb_config.get("PASSWORD", ""), usdb_config.get("PHPSESSID", ""), usdb_config.get("PK_ID", ""))
                song_infos = usdbScraperObject.srape_song(usdb_song_id)

                # Update Song in Database
                databaseObj.upate_song_by_id(usdb_song_id, song_infos.get("YOUTUBE_URL", ""), song_infos.get("SONG_TEXT", ""), 2)
                flask_logger.debug("USDB Scraping end...")

            # STATUS 2  -> Scraping Completed
            if song.get("STATUS") == 2:
                print("STATUS 2 -> Download Video / mp3 / Create Folder - USDB_SONG_ID: " + str(usdb_song_id))
                flask_logger.debug("STATUS 2 -> Download Video / mp3 / Create Folder - USDB_SONG_ID: " + str(usdb_song_id))

                # Application Config
                application_config = config["APPLICATION"] 

                # Update Song Status -> 3 (Downloading / Create Folder)
                databaseObj.update_song_status(usdb_song_id, 3)

                # 1. Create Folder
                flask_logger.debug("Create Song Folder...")               
                song_folder_name = song.get("SONG_INTERPRET") + "-" + song.get("SONG_TITLE")  
                output_path  = usdbUtilityObj.create_song_folder(song_folder_name, application_config.get("OUTPUT_DIRECTORY", "output"))
                media_file_path = output_path + "/" + song_folder_name
                
                # 2. Save Lyrics in a text file (Filename: SONG_INTERPRET - SONG_TITLE.txt)
                flask_logger.debug("Create Song Lyrics File...")      
                song_text = song.get('SONG_ULTRA_STAR_LYRICS')

                # 3. Save File
                output_file = media_file_path + ".txt"
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(song_text)
                                
                # 4. Download Audio and Video from Youtube
                flask_logger.debug("Download Audio...")   
                usdbUtilityObj.youtube_to_mp3(song.get('SONG_YT_VIDEO_LINK'), media_file_path) 
                 
                flask_logger.debug("Download Video...") 
                usdbUtilityObj.youtube_to_mp4(song.get('SONG_YT_VIDEO_LINK'), media_file_path)
                
                # 5. Download Cover Image
                flask_logger.debug("Download Cover...")   
                image_path = output_path + "/" + song_folder_name + ".jpg"
                usdbUtilityObj.download_image(song.get('SONG_COVER_URL'), image_path)    

                # Update Song Status -> 3 (Downloading / Create Folder)
                databaseObj.update_song_status(usdb_song_id, 4)
                flask_logger.debug("Download Completed...")

                # prepare Song for UltraStar
                usdbUtilityObj.prepare_song_ultra_star(output_path)
                flask_logger.debug("Song Scraping Completed...")

        flask_logger.debug("Background Task finished / wait 20 seconds...")
        await asyncio.sleep(20)  # wait 20 seconds

def start_background_task():
    """
    start the background task in a new event loop
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(background_task())

# Save the Song-IDs on the Server   
download_list = []

# PAGES
@app.route('/', methods=['GET'])
def page_home():    
    flask_logger.debug("GET: Home Page...")

    feed_url_top_10 = "https://usdb.animux.de/rss/rss_new_top10.php"
    feed_data = feedparser.parse(feed_url_top_10)
    entries_top_10 = feed_data.entries        
    
    feed_url_download_charts = "https://usdb.animux.de/rss/rss_downloads_top10.php"
    feed_data_download_charts = feedparser.parse(feed_url_download_charts)
    entries_download_charts = feed_data_download_charts.entries 

    # Prepare Song Data - extract Interpret and Title
    for song in entries_top_10:
        if 'title' in song:
            parts = song['title'].split(' - ', 1)  # Trenne bei ' - ', max. 1 Mal
            if len(parts) == 2:
                interpret, title = parts
                song['interpret'] = interpret.strip()  # Interpret hinzufügen
                song['title'] = title.strip()         # Titel hinzufügen

    # Prepare Song Data - extract Interpret and Title
    for song in entries_download_charts:
        if 'title' in song:
            parts = song['title'].split(' - ', 1)  # Trenne bei ' - ', max. 1 Mal
            if len(parts) == 2:
                interpret, title = parts
                song['interpret'] = interpret.strip()  # Interpret hinzufügen
                song['title'] = title.strip()         # Titel hinzufügen

    return render_template('home.html', entries_top_10=entries_top_10, entries_download_charts=entries_download_charts)

@app.route('/search-song', methods=['GET'])
def page_search_song():
    flask_logger.debug("GET: Search Song Page...")
    
    return render_template('songs.html')

@app.route('/query-list', methods=['GET'])
def page_query_list():
    flask_logger.debug("GET: Query Page...")

    # Create Databse Object
    databaseObj = USDBScraperDB("usdb_scrapper.db")
    query_song_list = databaseObj.fetch_all_songs()  
    
    return render_template('query_list.html', songs=query_song_list)

@app.route('/downloads', methods=['GET'])
def page_downloads():
    flask_logger.debug("GET: Downloads Page...")

    # Databse Object
    databaseObj = USDBScraperDB("usdb_scrapper.db")    
    downloaded_songs = databaseObj.get_downloaded_songs() 

    return render_template('downloads.html', downloaded_songs=downloaded_songs)

@app.route('/ultrastar-tools', methods=['GET'])
def page_ultrastar_tools():
    flask_logger.debug("GET: UltraStar Tools Page...")
    return render_template('ultrastar_tools.html')

# FUNCTIONS
@app.route('/search', methods=['GET'])
def search():
    """Führt die Suche durch und gibt die Ergebnisse als JSON zurück."""
    flask_logger.debug("GET: Search Song...")
    query = request.args.get('query', '').lower()
    filter_by = request.args.get('filter', 'TITLE')        
    print(filter_by)
    flask_logger.debug("Search Filter: " + str(filter_by))

    # USDB Config
    usdb_config = config["USDBScraper"]    

    # WORKAROUND
    title = ""
    interpret = ""
    if filter_by == "TITLE":
        title = query
    if filter_by == "INTERPRET":
        interpret = query
        

    # New Scraper
    usdbScraperObject = USDBScraperBeatifulSoap(usdb_config.get("USERNAME", ""), usdb_config.get("PASSWORD", ""), usdb_config.get("PHPSESSID", ""), usdb_config.get("PK_ID", ""))
    SONGS = usdbScraperObject.search_song(title,interpret, 30)
    
    return jsonify(SONGS)

@app.route('/query_list_action', methods=['POST'])
def function_query_list_action():
    usdb_song_id = request.json.get('USDB_SONG_ID')
    status = request.json.get('STATUS')

    flask_logger.debug("Change Song Status: " + str(usdb_song_id) + " - " + str(status))

    databaseObj = USDBScraperDB("usdb_scrapper.db")
    databaseObj.update_song_status(usdb_song_id, status)

    return jsonify({"USDB_SONG_ID": f"{usdb_song_id}", "STATUS": f"{status}"})

@app.route('/add_to_download', methods=['POST'])
def add_to_download():
    """Fügt einen Song mit allen Details zur Download-Liste hinzu."""    

    song_id = request.json.get('SONG_ID')
    song_interpret = request.json.get('SONG_INTERPRET')
    song_title = request.json.get('SONG_TITEL')

    flask_logger.debug("Add Song to Downloadlist: " + str(song_id) + " - " + str(song_interpret) + " - " + str(song_title))

    song_cover_url = "https://usdb.animux.de/data/cover/" + song_id + ".jpg"

    # Save Song to Database
    databaseObj = USDBScraperDB("usdb_scrapper.db")
    databaseObj.insert_song_query(song_id, song_title, song_interpret, song_cover_url)

    # Data Validation
    if not (song_id and song_interpret and song_title):
        return jsonify({"status": "error", "message": "Ungültige Song-Daten"}), 400

    # Check if Song is already in the List
    for song in download_list:
        if song['SONG_ID'] == song_id:
            return jsonify({"status": "info", "message": f"Song mit ID {song_id} ist bereits in der Liste."})

    # Add Song to List
    download_list.append({
        "SONG_ID": song_id,
        "SONG_INTERPRET": song_interpret,
        "SONG_TITEL": song_title
    })
    print(f"Download-Liste aktualisiert: {download_list}")
    return jsonify({"status": "success", "message": f"Song {song_title} hinzugefügt.", "download_list": download_list})

@app.route('/remove_from_download', methods=['POST'])
def remove_from_download():
    song_id = request.json.get('SONG_ID')

    # Song ID Validation
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
    flask_logger.debug("Start USDB-Scraper Webserver...")    
    
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
        flask_logger.error("Can't find config.json!")