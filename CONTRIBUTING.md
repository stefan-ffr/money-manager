# Contributing to Money Manager

Vielen Dank für dein Interesse, zu Money Manager beizutragen! 🎉

## Wie kann ich beitragen?

### Bugs melden

Wenn du einen Bug findest:
1. Prüfe ob der Bug bereits als Issue existiert
2. Falls nicht, erstelle ein neues Issue mit:
   - Beschreibung des Problems
   - Schritte zur Reproduktion
   - Erwartetes vs. tatsächliches Verhalten
   - Screenshots (falls relevant)
   - System-Info (OS, Browser, Docker Version)

### Features vorschlagen

Feature-Vorschläge sind willkommen!
1. Erstelle ein Issue mit dem Label "enhancement"
2. Beschreibe das gewünschte Feature
3. Erkläre den Nutzen
4. Falls möglich, skizziere eine Implementierung

### Code beitragen

1. **Fork das Repository**
2. **Erstelle einen Branch**
   ```bash
   git checkout -b feature/dein-feature-name
   ```

3. **Entwickle lokal**
   ```bash
   docker compose up -d
   ```

4. **Teste deine Änderungen**
   ```bash
   # Backend Tests
   cd backend
   pytest

   # Frontend Tests
   cd frontend
   npm test
   ```

5. **Commit deine Änderungen**
   ```bash
   git commit -m "feat: Kurze Beschreibung"
   ```

   Verwende [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - Neues Feature
   - `fix:` - Bug Fix
   - `docs:` - Dokumentation
   - `style:` - Formatierung
   - `refactor:` - Code Refactoring
   - `test:` - Tests
   - `chore:` - Maintenance

6. **Push zum Fork**
   ```bash
   git push origin feature/dein-feature-name
   ```

7. **Erstelle einen Pull Request**

## Code Style

### Python (Backend)
- Folge PEP 8
- Nutze `black` für Formatierung
- Nutze `flake8` für Linting

```bash
black .
flake8 .
```

### TypeScript/React (Frontend)
- Folge den ESLint Regeln
- Nutze TypeScript strict mode
- Verwende funktionale Components mit Hooks

```bash
npm run lint
```

## Projekt-Struktur

```
money-manager/
├── backend/          # FastAPI Backend
│   ├── app/
│   │   ├── api/      # API Endpoints
│   │   ├── models/   # SQLAlchemy Models
│   │   ├── services/ # Business Logic
│   │   └── core/     # Config, Database
│   └── telegram_bot.py
├── frontend/         # React Frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
└── .github/workflows/
```

## Testing

### Backend
```bash
cd backend
pytest
pytest --cov  # Mit Coverage
```

### Frontend
```bash
cd frontend
npm test
npm run test:coverage
```

## Dokumentation

- API Dokumentation: `/docs` (automatisch via FastAPI)
- Code sollte selbsterklärend sein
- Komplexe Logik mit Kommentaren versehen
- README aktualisieren bei neuen Features

## Review Prozess

1. Mindestens ein Maintainer muss den PR reviewen
2. Alle CI Checks müssen grün sein
3. Keine merge conflicts
4. Code Style eingehalten
5. Tests vorhanden und bestanden

## Fragen?

- Erstelle ein Issue mit dem Label "question"
- Oder schreibe in die Discussions

Vielen Dank für deinen Beitrag! 🙏
