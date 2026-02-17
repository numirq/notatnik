from flask import Flask, render_template, request, redirect, url_for, flash
import json
from ftplib import FTP
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH_MB', 16)) * 1024 * 1024

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
LOG_FILE = os.path.join(BASE_DIR, 'ip_log.txt')
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ext.strip().lower()
    for ext in os.environ.get('ALLOWED_EXTENSIONS', 'txt,pdf,doc,docx,jpg,jpeg,png').split(',')
    if ext.strip()
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_saved_uploads():
    files = []
    for name in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, name)
        if os.path.isfile(path):
            files.append((name, os.path.getmtime(path)))
    files.sort(key=lambda item: item[1], reverse=True)
    return [name for name, _ in files]


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

    def ftp_configured(self):
        return all([
            os.environ.get('FTP_HOST'),
            os.environ.get('FTP_USER'),
            os.environ.get('FTP_PASSWORD')
        ])

    def wyslij_plik_na_ftp(self, filepath, subject, title):
        ftp_adres = os.environ.get('FTP_HOST')
        ftp_uzytkownik = os.environ.get('FTP_USER')
        ftp_haslo = os.environ.get('FTP_PASSWORD')

        if not ftp_adres or not ftp_uzytkownik or not ftp_haslo:
            raise ValueError('Brak konfiguracji FTP (FTP_HOST, FTP_USER, FTP_PASSWORD).')

        dzisiaj = datetime.now().strftime('%Y-%m-%d')
        safe_subject = secure_filename(subject) or 'przedmiot'
        safe_title = secure_filename(title) or 'notatka'
        nazwa_plik = f"{safe_subject}_{safe_title}_{dzisiaj}{os.path.splitext(filepath)[1]}"
        folder_path = f"PROGRAMY/lekcje/{safe_subject}/"

        try:
            with FTP(ftp_adres) as ftp:
                ftp.login(user=ftp_uzytkownik, passwd=ftp_haslo)
                try:
                    ftp.mkd(folder_path)
                except Exception:
                    pass

                with open(filepath, 'rb') as plik:
                    ftp.storbinary(f'STOR {folder_path}{nazwa_plik}', plik)
        except Exception as e:
            raise RuntimeError(f'Wystąpił błąd podczas wysyłania pliku: {e}') from e


notatnik = Notatnik(przedmiot='EUTK')


@app.route('/')
def index():
    return render_template('index.html', saved_uploads=get_saved_uploads())


@app.route('/upload', methods=['POST'])
def upload_file():
    subject = request.form.get('przedmiot', '').strip()
    title = request.form.get('tytul', '').strip()
    uploaded_file = request.files.get('file')

    if not subject or not title:
        flash('Uzupełnij pola: przedmiot i tytuł.')
        return redirect(url_for('index'))

    if not uploaded_file or uploaded_file.filename == '':
        flash('Nie wybrano pliku.')
        return redirect(url_for('index'))

    if not allowed_file(uploaded_file.filename):
        flash('Nieobsługiwany format pliku.')
        return redirect(url_for('index'))

    safe_subject = secure_filename(subject) or 'przedmiot'
    safe_title = secure_filename(title) or 'notatka'
    ext = os.path.splitext(secure_filename(uploaded_file.filename))[1].lower()
    dzisiaj = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'{safe_subject}_{safe_title}_{dzisiaj}{ext}'
    file_path = os.path.join(UPLOAD_DIR, filename)
    uploaded_file.save(file_path)

    if notatnik.ftp_configured():
        try:
            notatnik.wyslij_plik_na_ftp(file_path, subject, title)
            flash('Plik został wysłany na FTP i zapisany lokalnie.')
        except Exception as e:
            flash(f'Błąd FTP. Plik zapisano lokalnie. Szczegóły: {e}')
    else:
        flash('Plik zapisany lokalnie (FTP nie jest skonfigurowane).')

    return redirect(url_for('index'))


@app.before_request
def log_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    czas = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{czas} - {ip}\n")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
