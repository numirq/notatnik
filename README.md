# Notatnik (Flask + FTP)

To jest aplikacja backendowa Flask, więc **nie może działać bezpośrednio na GitHub Pages** (Pages hostuje tylko statyczne strony).

## Jak to „hostować na GitHubie” poprawnie

Najlepszy układ:
- kod i CI na GitHub,
- deployment backendu na Render (automatycznie z GitHub).

W tym repo dodałem:
- workflow CI: `.github/workflows/python-ci.yml`,
- workflow auto-deploy do Render przez deploy hook: `.github/workflows/deploy-render.yml`,
- `render.yaml` (Blueprint), żeby łatwo podpiąć usługę po imporcie repo.

## Szybki setup

### 1) Wrzuć repo na GitHub
```bash
git remote add origin <twoj-url-repo>
git push -u origin <branch>
```

### 2) Podłącz repo do Render
W Render:
1. `New +` -> `Blueprint` (albo `Web Service`),
2. wskaż to repo,
3. ustaw zmienne środowiskowe:
   - `FTP_HOST`
   - `FTP_USER`
   - `FTP_PASSWORD`
   - (opcjonalnie) `ALLOWED_EXTENSIONS`, `MAX_CONTENT_LENGTH_MB`

### 3) (Opcjonalnie) Auto deploy z GitHub Actions
1. W Render skopiuj `Deploy Hook URL`.
2. W GitHub -> `Settings` -> `Secrets and variables` -> `Actions` dodaj sekret:
   - `RENDER_DEPLOY_HOOK_URL`
3. Po pushu na `main/master` workflow odpali deploy.

## Uwaga o GitHub Pages
Jeśli chcesz stricte `*.github.io`, trzeba przerobić projekt na czysto statyczny frontend + osobne API backend (np. Render/Railway/Fly).
