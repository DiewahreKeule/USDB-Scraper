import requests
from bs4 import BeautifulSoup

class USDBScraperBeatifulSoap:
    def __init__(self, usdb_username, usdb_password, PHPSESSID, _pk_id):
        self.url = "https://usdb.animux.de/"
        self.usdb_username = usdb_username
        self.usdb_password = usdb_password
        self.PHPSESSID = PHPSESSID
        self._pk_id = _pk_id
        self.session = requests.Session()        
        self.session.cookies.set("PHPSESSID", PHPSESSID)        
        self.session.cookies.set("_pk_id.yEplKJvn3znLGB5.5ede", _pk_id)
        
        # Login-Request
        headers = {
            "Host": "usdb.animux.de",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Accept-Language": "de-DE,de;q=0.9",
            "Origin": "https://usdb.animux.de",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=0, i",
        }

        login_payload = {
            "user": usdb_username,
            "pass": usdb_password,
            "login": "Login",
        }

        login_response = self.session.post("https://usdb.animux.de/?link=login", headers=headers, data=login_payload)


    def search_song(self, title, interpret, limit):
        url = "https://usdb.animux.de/?link=list"
        # Header des HTTP-Requests
        headers = {
            "Host": "usdb.animux.de",
            "Cookie": f"PHPSESSID={self.PHPSESSID}; _pk_id.yEplKJvn3znLGB5.5ede={self._pk_id}; _pk_ses.yEplKJvn3znLGB5.5ede=1",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Accept-Language": "de-DE,de;q=0.9",
            "Origin": "https://usdb.animux.de",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://usdb.animux.de/?link=browse",
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=0, i",
        }        

        # Daten des HTTP-Requests
        payload = {
            "interpret": interpret,
            "title": title,
            "edition": "",
            "language": "",
            "genre": "",
            "year": "",
            "creator": "",
            "order": "id",
            "ud": "asc",
            "limit": limit,
            "details": "1",
        }
        # Sende den Post-Request
        response = self.session.post(url, headers=headers, data=payload)

        # Check if Response is OK
        if response.status_code == 200:
            # HTML in BeautifulSoup-Objekt umwandeln
            soup = BeautifulSoup(response.text, "html.parser")

            # Tabelle extrahieren
            tables = soup.find_all("table")
            songs = []

            for table in tables:
                # Prüfe ob es die richtige Tabelle ist
                if table.find_all("tr", {"class": "list_tr2"}):
                    rows = table.find_all("tr", class_="list_tr2")
                    for row in rows:
                        cells = row.find_all("td")
                        if cells:
                            onclick_attr = cells[1].get("onclick")
                            if onclick_attr and "show_detail" in onclick_attr:
                                id_value = onclick_attr.split("(")[1].split(")")[0]
                                id = id_value

                            # cover = cells[1].find("img")["src"] if cells[1].find("img") else "-"
                            interpret = cells[2].text.strip() if len(cells) > 2 else ""
                            title = cells[3].text.strip() if len(cells) > 3 else ""
                            genre = cells[4].text.strip() if len(cells) > 4 else ""
                            year = cells[5].text.strip() if len(cells) > 5 else ""
                            edition = cells[6].text.strip() if len(cells) > 6 else ""
                            golden_notes = cells[7].text.strip() if len(cells) > 7 else ""
                            language = cells[8].text.strip() if len(cells) > 8 else ""
                            creator = cells[9].text.strip() if len(cells) > 9 else ""
                            rating = cells[10].text.strip() if len(cells) > 10 else ""
                            views = cells[11].text.strip() if len(cells) > 11 else ""

                            # print(f"USDB-ID: {id}, Interpret: {interpret}, Titel: {title}, Genre: {genre}, Jahr: {year}, Edition: {edition}, Golden Notes: {golden_notes}, Sprache: {language}, Creator: {creator}, Bewertung: {rating}, Aufrufe: {views}, Cover: {cover}")
                            
                            song_cover_url = "https://usdb.animux.de/data/cover/" + id + ".jpg"
                            
                            songs.append({
                                "SONG_ID": id,
                                "SONG_INTERPRET": interpret,
                                "SONG_TITEL": title,
                                "SONG_COVER_URL": song_cover_url,
                                "GENRE": genre,
                                "YEAR": year,
                                "EDITION": edition,
                                "GOLDEN_NOTES": golden_notes,
                                "LANGUAGE": language,
                                "CREATOR": creator,
                                "RATING": rating,
                                "VIEWS": views
                            })
                break
            return songs
        
    
    def srape_song(self, usdb_song_id):

        # Prepare URL
        url = "https://usdb.animux.de/?link=detail&id=" + str(usdb_song_id)
        response = self.session.get(url)        

        # Check if Response is OK
        if response.status_code == 200:
            # Convert HTML to BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Find Youtube Link
            youtube = soup.find("iframe", {"class": "embed"})['src']            
            youtube_url = "https://www.youtube.com/watch?v=" + youtube.split("embed/")[-1]            

            headers = {
                "Host": "usdb.animux.de",
                "Cache-Control": "max-age=0",
                "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Accept-Language": "de-DE,de;q=0.9",
                "Origin": "https://usdb.animux.de",
                "Content-Type": "application/x-www-form-urlencoded",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate, br",
                "Priority": "u=0, i",
                "Referer": f"https://usdb.animux.de/?link=gettxt&id={usdb_song_id}",
                "Cookie": f"PHPSESSID={self.PHPSESSID}; _pk_id.yEplKJvn3znLGB5.5ede={self._pk_id}; _pk_ses.yEplKJvn3znLGB5.5ede=1",
            }

            # Get TXT Payload
            gettxt_payload = {
                "wd": "1",
            }

            # run gettxt-Request
            gettxt_response = self.session.post(f"https://usdb.animux.de/?link=gettxt&id={usdb_song_id}", headers=headers, data=gettxt_payload)

            # Check if Response is OK
            if gettxt_response.status_code == 200:                
                # Soup Object create    
                soup = BeautifulSoup(gettxt_response.text, "html.parser")
                
                # Extract Lyrics
                lyrics = soup.find("textarea", {"name": "txt"}).text.replace("\r\n", "\n")               

            # Return Object
            return {
                "YOUTUBE_URL": youtube_url,
                "SONG_TEXT": lyrics
            }
