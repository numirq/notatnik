# Notatnik — wersja pod GitHub Pages

Zgodnie z Twoją decyzją projekt jest przygotowany do hostowania **tylko na GitHubie** (GitHub Pages).

## Co jest wdrożone

- statyczna strona w katalogu `docs/` (to publikuje GitHub Pages),
- automatyczny deployment przez workflow `.github/workflows/deploy-pages.yml`,
- workflow CI `.github/workflows/python-ci.yml` zostawiony do kontroli kodu Pythona.

## Ważne ograniczenie

GitHub Pages hostuje wyłącznie statyczne pliki (HTML/CSS/JS).
To oznacza, że funkcje backendowe Flask (np. upload na FTP) **nie działają** bez zewnętrznego serwera.

## Jak uruchomić publikację

1. Wgraj repo na GitHub.
2. Wejdź: `Settings -> Pages`.
3. W sekcji *Build and deployment* wybierz: **GitHub Actions**.
4. Zrób push na `main` / `master` / `work`.
5. Workflow `Deploy static site to GitHub Pages` opublikuje katalog `docs/`.
