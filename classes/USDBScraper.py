from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import requests

class USDBScraper:
    def __init__(self, driver_path, usdb_username, usdb_password):
        """Initialisiert den WebDriver."""   
        self.url = "https://usdb.animux.de/"    
        self.usdb_username = usdb_username
        self.usdb_password = usdb_password 
        
        # Webdriver Options
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") # start headless
        # options.add_argument("--start-maximized") # Start maximized
        options.add_argument("--disable-gpu")        
        options.add_argument("--no-sandbox")

        # WebDriver initalisieren
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)

        # Login Routine
        try:
            self.driver.get(self.url)
            time.sleep(3)

            # Fill Login Form            
            username_field = self.driver.find_element(By.NAME, "user")  # Ersetze 'username' durch das korrekte Attribut
            password_field = self.driver.find_element(By.NAME, "pass")  # Ersetze 'password' durch das korrekte Attribut

            # Type in Username and Password            
            username_field.send_keys(self.usdb_username)
            password_field.send_keys(self.usdb_password) 

            password_field.send_keys(Keys.RETURN)  # Enter drücken

            # Kurze Pause, um sicherzustellen, dass die Seite vollständig geladen ist
            time.sleep(2)
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")


    def search_song(self, song_title):
        """Sucht nach einem Song."""

        # Songs durchsuchen öffnen
        song_search = self.driver.find_element(By.LINK_TEXT, "Songs durchsuchen")  # Ersetze 'Songliste' durch den richtigen Text
        song_search.click()

        time.sleep(1)

        # Song suchen
        ## Suche Titel 
        search_title = self.driver.find_element(By.NAME, "title")
        search_title.send_keys(song_title)
        search_title.send_keys(Keys.RETURN)  # Enter drücken

        time.sleep(5)

        ## Liste mit Ergebnissen ausgeben
        # Tabelle mit den `<tr>`-Elementen auswählen
        rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'list_tr1') or contains(@class, 'list_tr2')]")

        # Result List
        songs = []

        # Inhalte der gefundenen `<tr>`-Elemente ausgeben
        for row in rows:
            # Erstes <td>-Element finden
            first_td = row.find_element(By.XPATH, ".//td[2]")   

            # 3. TD -> Interpret
            td_interpret = row.find_element(By.XPATH, ".//td[3]")                                
            # print("Interpret: " + td_interpret.text)
            song_interpret = td_interpret.text

            # 4. TD -> Song Titel
            td_song_title = row.find_element(By.XPATH, ".//td[4]")                                
            # print("Titel: " + td_song_title.text)
            song_title = td_song_title.text            

            # `onclick`-Attribut auslesen
            onclick_value = first_td.get_attribute("onclick")
            if onclick_value and "show_detail" in onclick_value:
                # ID extrahieren mit regulärem Ausdruck
                match = re.search(r"show_detail\((\d+)\)", onclick_value)
                if match:
                    id_value = match.group(1)
                    # print(f"Gefundene ID: {id_value}")
                    song_id = id_value

            # print(row.text)  # Gibt den Text des gesamten `<tr>`-Elements aus

            # Song Cover
            song_cover_url = "https://usdb.animux.de/data/cover/" + song_id + ".jpg"

            songs.append({
            "SONG_ID": song_id,
            "SONG_INTERPRET": song_interpret,
            "SONG_TITEL": song_title,
            "SONG_COVER_URL": song_cover_url
            })

        print(f"Es wurden {len(rows)} Zeilen gefunden.")  
        return songs    
    
    def srape_song(self, song_id):
        # Song Seite öffnen
        url = "https://usdb.animux.de/?link=detail&id=" + str(song_id)
        self.driver.get(url)

        time.sleep(5)        

        # Youtube Video Link scrappen  
        play_button = self.driver.find_element(By.CLASS_NAME, "embed")

        # Klick auf den Play-Button ausführen
        youtube_embed_link = play_button.get_attribute("src")
        video_id = youtube_embed_link.split("embed/")[-1]
        # print("Youtube Video Link: https://www.youtube.com/watch?v=" + video_id)    
        youtube_url = "https://www.youtube.com/watch?v=" + video_id

        time.sleep(3)    

        # Songtext holen    
        url = "https://usdb.animux.de/?link=gettxt&id=" + str(song_id)
        self.driver.get(url)

        # Warte 30 Sekunden, bis der Songtext zur Verfügung steht
        time.sleep(30)    

        # Finde das Textarea Element mit dem Text
        songtext_element = self.driver.find_element(By.NAME, "txt")
        # print(songtext_element.text)
        songtext = songtext_element.text

        return {
            "YOUTUBE_URL": youtube_url,
            "SONG_TEXT": songtext
        }

