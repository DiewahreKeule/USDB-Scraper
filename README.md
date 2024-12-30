# USDB Scraper
Search and Download your favorite songs for UltraStar Deluxe

UltraStar Deluxe: https://github.com/UltraStar-Deluxe/USDX

## Features
- Search for Songs
- Download Songs (Lyrics, Audio, Video)
- Creates a folder for UltraStar Deluxe
- Save all your Songs in SQLite Database

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
3. `docker build -t flask-app .`
4. `docker run -v your/local/folder:/app/output -p 5000:5000 flask-app`