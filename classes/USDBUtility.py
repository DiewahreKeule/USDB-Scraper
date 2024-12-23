import yt_dlp
import requests
import os
import json

class USDBUtility:

    def load_config(self, file_path):
        """
        Lädt die Konfigurationsdatei und gibt die Daten zurück.

        :param file_path: Pfad zur config.json-Datei
        :return: Dictionary mit Konfigurationsdaten
        """
        try:
            with open(file_path, 'r') as file:
                config = json.load(file)
                return config
        except FileNotFoundError:
            print(f"Konfigurationsdatei {file_path} nicht gefunden.")
            return None
        except json.JSONDecodeError as e:
            print(f"Fehler beim Laden der JSON-Datei: {e}")
            return None

    def create_song_folder(self, song_folder_name):
        # Build full output Folder Name with Song Folder Name joined
        output_path = os.path.join("output", song_folder_name)   

        # create Folder, if not exists
        os.makedirs(output_path, exist_ok=True)

        # return full output folder name
        return output_path


    def download_image(self, url, save_path):
        """
        Lädt ein Bild von der angegebenen URL herunter und speichert es unter save_path.
        :param url: URL des Bildes
        :param save_path: Pfad, unter dem das Bild gespeichert werden soll
        """
        try:
            # HTTP GET-Anfrage an die URL
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Überprüft auf HTTP-Fehler

            # Bildinhalt in einer Datei speichern
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):  # Daten in Blöcken von 1024 Bytes schreiben
                    file.write(chunk)

            print(f"Bild erfolgreich heruntergeladen: {save_path}")
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Herunterladen des Bildes: {e}")

    def youtube_to_mp3(self, youtube_url, output_folder):
        ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_folder}',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

    def youtube_to_mp4(self, youtube_url, output_folder):
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',  # MP4-Format bevorzugen
            'outtmpl': f'{output_folder}',         # Speicherort und Dateiname
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

    def prepare_song_ultra_star(self, song_folder):
        # Rename Song Files (mp3, mp4, jpg, txt)
        try:
            # Check if Folder exists
            if not os.path.isdir(song_folder):
                print(f"Der Ordner '{song_folder}' existiert nicht.")
                return

            # Ordnername extrahieren
            folder_name = os.path.basename(os.path.normpath(song_folder))

            # Liste der Zieldateien
            target_extensions = ['.mp3', '.jpg', '.txt', '.mp4']

            # Dateien im Ordner durchsuchen
            for file_name in os.listdir(song_folder):
                file_path = os.path.join(song_folder, file_name)

                # Überprüfen, ob es sich um eine Datei handelt
                if os.path.isfile(file_path):
                    file_extension = os.path.splitext(file_name)[1].lower()

                    if file_extension in target_extensions:
                        # Neuer Dateiname
                        new_file_name = f"{folder_name}{file_extension}"
                        new_file_path = os.path.join(song_folder, new_file_name)

                        # Datei umbenennen
                        os.rename(file_path, new_file_path)
                        print(f"'{file_name}' wurde umbenannt in '{new_file_name}'")
        except Exception as e:
            print(f"Fehler beim Verarbeiten des Ordners: {e}")
        
        # Replace mp3, mp4, jpg in txt File
        try:
            # Überprüfen, ob der Ordner existiert
            if not os.path.isdir(song_folder):
                print(f"Der Ordner '{song_folder}' existiert nicht.")
                return

            # Finde die .mp3-Datei im Ordner
            mp3_file = None
            for file_name in os.listdir(song_folder):
                if file_name.endswith('.mp3'):
                    mp3_file = file_name
                    break

            # Finde die .mp4-Datei im Ordner
            mp4_file = None
            for file_name in os.listdir(song_folder):
                if file_name.endswith('.mp4'):
                    mp4_file = file_name
                    break

            cover_file = None
            for file_name in os.listdir(song_folder):
                if file_name.endswith('.jpg'):
                    cover_file = file_name
                    break

            if not mp3_file:
                print("Keine .mp3-Datei im Ordner gefunden.")
                return
            
            if not mp4_file:
                print("Keine Video Datei gefunden")
            
            if not cover_file:
                print("Kein Cover gefunden")

            # Finde die .txt-Datei im Ordner
            txt_file = None
            for file_name in os.listdir(song_folder):
                if file_name.endswith('.txt'):
                    txt_file = file_name
                    break

            if not txt_file:
                print("Keine .txt-Datei im Ordner gefunden.")
                return

            # Pfad zur .txt-Datei
            txt_file_path = os.path.join(song_folder, txt_file)

            # Datei einlesen und Zeilen aktualisieren
            with open(txt_file_path, 'r') as file:
                lines = file.readlines()

            updated_lines = []
            for line in lines:
                # mp3-Datei ergänzen
                if line.startswith('#MP3:'):
                    # Aktualisiere die Zeile mit dem neuen mp3-Dateinamen
                    updated_lines.append(f'#MP3:{mp3_file}\n')                            

                # mp4-Datei ergänzen
                elif line.startswith('#VIDEO:'):
                    if mp4_file:
                        # Aktualisiere die Zeile mit dem neuen mp4-Dateinamen
                        updated_lines.append(f'#VIDEO:{mp4_file}\n')                            

                # Cover
                elif line.startswith('#COVER:'):
                    if cover_file:
                        # Aktualisiere die Zeile mit dem neuen Cover
                        updated_lines.append(f'#COVER:{cover_file}\n')
                else:
                    updated_lines.append(line)

            # Datei mit den aktualisierten Zeilen überschreiben
            with open(txt_file_path, 'w') as file:
                file.writelines(updated_lines)

            print(f"Die Datei '{txt_file}' wurde aktualisiert und der MP3-Eintrag gesetzt.")

        except Exception as e:
            print(f"Fehler beim Verarbeiten der .txt-Datei: {e}")