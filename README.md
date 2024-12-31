# USDB Scraper
![image](/static/android-chrome-192x192.png)

Search and Download your favorite Songs from UlstraStar Database for UltraStar Deluxe\
UltraStar Deluxe: https://github.com/UltraStar-Deluxe/USDX

## Features
- Search for Songs (Title, Interpret)
- Download Songs (Lyrics, Audio, Video)
- Creates Song Foolders for UltraStar Deluxe (simply copy the Song Folders to your UltraStar Deluxe Installation)
- Save all your Songs in SQLite Database
- All Song Information will saved to the Database; You can recreate the Song Folders later

## Installation
1. Install `git`, `Python 3.11` and `pip`
2. Clone this Repository `git clone https://github.com/DiewahreKeule/USDB-Scraper.git`
3. `cd USDB-Scraper`
4. `pip install -r requirements.txt`
5. Change Settings in `config.json` (Example: config.json.example)
6. Start the App `python.exe .\main.py`

## Installation (Docker)
1. Clone this Repository `git clone https://github.com/DiewahreKeule/USDB-Scraper.git`
2. `cd USDB-Scraper`
3. `docker build -t usdb-scraper .`
4. `docker run -v your/local/folder:/app/output -p 5000:5000 usdb-scraper`