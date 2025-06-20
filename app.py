from flask import Flask, render_template, request, redirect, url_for
import json
from ftplib import FTP
from datetime import datetime
import os
import webbrowser
import threading

app = Flask(__name__)

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
        
        # Stwórz folder przedmiotu, jeśli nie istnieje
        folder_path = f"PROGRAMY/lekcje/{subject}/"
        
        try:
            with FTP(ftp_adres) as ftp:
                ftp.login(user=ftp_uzytkownik, passwd=ftp_haslo)
                try:
                    ftp.mkd(folder_path)  # Utwórz folder przedmiotu
                except Exception as e:
                    # Ignoruj błąd, jeśli folder już istnieje
                    print(f'Folder {folder_path} może już istnieć: {e}')
                
                with open(filepath, 'rb') as plik:
                    ftp.storbinary(f'STOR {folder_path}{nazwa_plik}', plik)
        except Exception as e:
            print(f'Wystąpił błąd podczas wysyłania pliku: {e}')

notatnik = Notatnik(przedmiot="EUTK")  # Domyślny przedmiot

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
        os.remove(file_path)  # Usuń plik lokalnie po wysłaniu na FTP

    return redirect(url_for('index'))

if __name__ == "__main__":
    webbrowser.open_new('http://127.0.0.1:5000')  # Otwiera przeglądarkę od razu
    app.run(debug=True, use_reloader=False)  # Wyłącz reloader
