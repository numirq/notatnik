from flask import Flask, render_template, request, redirect, url_for
import json
from ftplib import FTP
from datetime import datetime
import os

app = Flask(__name__)

# === Notatnik ===
class Notatnik:
    def __init__(self, przedmiot, nazwa_pliku=None):
        if nazwa_pliku is None:
            dzisiaj = datetime.now().strftime('%Y-%m-%d')
            self.nazwa_pliku = f'notatki_{przedmiot}_{dzisiaj}.json'
        else:
            self.nazwa_pliku = nazwa_pliku
        self.notatki = self.wczytaj_notatki()

    def wczytaj_notatki(self):
        try:
            with open(self.nazwa_pliku, 'r', encoding='utf-8') as plik:
                return json.load(plik)
        except FileNotFoundError:
            return []

    def zapisz_notatki(self):
        with open(self.nazwa_pliku, 'w', encoding='utf-8') as plik:
            json.dump(self.notatki, plik, ensure_ascii=False, indent=4)

    def dodaj_notatke(self, temat, tresc):
        notatka = {'temat': temat, 'tresc': tresc}
        self.notatki.append(notatka)
        self.zapisz_notatki()

    def wyslij_plik_na_ftp(self, filepath, subject, title):
        ftp_adres = 'mzsp.edu.pl'
        ftp_uzytkownik = '2TI'
        ftp_haslo = 'grOga7'
        dzisiaj = datetime.now().strftime('%Y-%m-%d')
        nazwa_plik = f"{subject}_{title}_{dzisiaj}{os.path.splitext(filepath)[1]}"
        folder_path = f"PROGRAMY/lekcje/{subject}/"

        try:
            with FTP(ftp_adres) as ftp:
                ftp.login(user=ftp_uzytkownik, passwd=ftp_haslo)
                try:
                    ftp.mkd(folder_path)
                except Exception as e:
                    print(f'Folder {folder_path} może już istnieć: {e}')
                with open(filepath, 'rb') as plik:
                    ftp.storbinary(f'STOR {folder_path}{nazwa_plik}', plik)
        except Exception as e:
            print(f'Błąd podczas wysyłania pliku: {e}')

notatnik = Notatnik(przedmiot="EUTK")

# === Strony Flask ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    subject = request.form['przedmiot']
    title = request.form['tytul']
    uploaded_file = request.files['file']

    if uploaded_file.filename != '':
        file_path = os.path.join('uploads', uploaded_file.filename)
        uploaded_file.save(file_path)
        notatnik.wyslij_plik_na_ftp(file_path, subject, title)
        os.remove(file_path)

    return redirect(url_for('index'))

# === Logowanie IP ===
LOG_FILE = os.path.join(os.path.dirname(__file__), 'ip_log.txt')

@app.before_request
def log_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    czas = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{czas} - {ip}\n")

# === Wyświetlanie logów na stronie ===
@app.route('/logi')
def show_logs():
    klucz = request.args.get("klucz")
    if klucz != "1234":
        return "Dostęp zabroniony", 403

    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    logs = []
    for line in lines:
        parts = line.strip().split(" - ")
        if len(parts) == 2:
            logs.append({'time': parts[0], 'ip': parts[1]})
    
    return render_template('logi.html', logs=logs)

# === Uruchomienie ===
if __name__ == "__main__":
    app.run()
