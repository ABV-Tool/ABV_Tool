# ABV-Antragstool

Ein webbasiertes Django-Tool für die Verwaltung von Anträgen im Allgemeinen Bereich des Studierendenrats (STURA) der HTW Dresden. Das System ermöglicht die digitale Erfassung, Verwaltung und Bearbeitung von Anträgen für Plenar- und Referatssitzungen.

## 🎯 Projektübersicht

Das ABV-Antragstool ist eine umfassende Webanwendung, die den gesamten Lebenszyklus von Anträgen im Studierendenrat abbildet - von der Einreichung durch Antragsteller bis zur Beschlussfassung in Sitzungen. Das Tool standardisiert und digitalisiert den Antragsprozess und ermöglicht eine strukturierte Verwaltung aller Anträge.

### Hauptfunktionalitäten

-   **Antragsmanagement**: Digitale Erfassung verschiedener Antragstypen (Finanzanträge, Personenwahlen, Benehmen, etc.)
-   **Sitzungsverwaltung**: Organisation von Plenar- und Referatssitzungen mit automatischer Tagesordnungserstellung
-   **Beschlussverwaltung**: Dokumentation von Abstimmungsergebnissen und Beschlüssen
-   **Etherpad-Integration**: Kollaborative Dokumentbearbeitung über API-Anbindung
-   **E-Mail-Benachrichtigungen**: Automatische Kommunikation zwischen Antragstellern und Verwaltung
-   **Anlagenverwaltung**: Upload und Verwaltung von Dokumenten zu Anträgen

### Datenmodell

Das System basiert auf folgenden Hauptentitäten:

-   **Antrag**: Zentrale Entität mit Titel, Text, Typ und Zuordnungen
-   **Sitzung**: Plenar- oder Referatssitzungen mit Datum und Zuordnung
-   **Beschluss**: Abstimmungsergebnisse und Entscheidungen
-   **Referat**: Organisatorische Einheiten innerhalb des STURA
-   **Antragssteller**: Personen, die Anträge einreichen
-   **Antragstyp**: Kategorisierung (Finanzantrag, Personenwahl, etc.)
-   **Anlage**: Dateien und Dokumente zu Anträgen

## 🚀 Development Environment Setup

### Option 1: Docker Compose (Empfohlen)

**Für Production/Standard-Setup:**

```bash
# Im src/ Verzeichnis
docker-compose up
```

Dies startet:

-   ABV-Tool auf Port 8020
-   PostgreSQL Datenbank auf Port 5432
-   Mailcatcher auf Port 1080

**Für Development:**

```bash
# Im src/ Verzeichnis
docker-compose -f docker-compose.dev.yml up
```

### Option 2: Lokale Entwicklung (Virtual Environment)

1. **Virtual Environment erstellen und aktivieren:**

```bash
cd src/
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

2. **Dependencies installieren:**

```bash
pip install -r requirements.txt
```

3. **Environment-Variablen setzen:**
   Eine `.env` Datei im src/ Verzeichnis erstellen mit:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DB_NAME=Antragstool
DB_USER=abv
DB_PASSWORD=abv
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=localhost
EMAIL_PORT=1025
```

4. **Datenbank starten:**

```bash
# PostgreSQL separat starten oder Docker verwenden:
docker-compose -f docker-compose.dev.yml up db
```

5. **Django Backend starten:**

```bash
cd abv/
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata Antragstool/fixtures/referate.json
python manage.py loaddata Antragstool/fixtures/antragstyp.json
python manage.py createsuperuser  # Optional
python manage.py runserver 8000
```

6. **TailwindCSS Frontend (parallel in neuem Terminal):**

```bash
cd abv/
python manage.py tailwind start
```

### Wichtige URLs und Ports:

-   **Hauptanwendung**: http://localhost:8020 (Docker) oder http://localhost:8000 (lokal)
-   **Admin-Interface**: http://localhost:8020/admin oder http://localhost:8000/admin
-   **PostgreSQL**: Port 5432
-   **Mailcatcher**: http://localhost:1080

## 🔧 Detaillierte Projektstruktur

### Backend-Architektur (Django)

Das Projekt folgt dem Django MVC-Pattern und ist wie folgt strukturiert:

```
src/abv/
├── abv/                    # Django-Projektkonfiguration
│   ├── settings.py         # Haupt-Settings mit Environment-Handling
│   ├── urls.py            # URL-Routing
│   └── wsgi.py            # WSGI-Konfiguration
├── Antragstool/           # Hauptapplikation
│   ├── models.py          # Datenmodelle (Antrag, Sitzung, etc.)
│   ├── views.py           # View-Logic und Request-Handling
│   ├── forms.py           # Django-Forms für Datenerfassung
│   ├── admin.py           # Django-Admin-Konfiguration
│   ├── api.py             # Etherpad-API-Integration
│   ├── mails.py           # E-Mail-Funktionalitäten
│   ├── urls.py            # URL-Patterns der App
│   ├── fixtures/          # Testdaten und Standardwerte
│   ├── static/            # Statische Dateien (CSS, JS, Images)
│   ├── templates/         # Django-Templates
│   └── migrations/        # Datenbankmigrationen
└── manage.py              # Django-Management-Script
```

### Datenmodelle im Detail

#### Antrag

-   **Stammdaten**: UUID, Titel, Text, Priorität
-   **Beziehungen**: Sitzung, Antragstyp, Antragssteller, Beschluss
-   **Metadaten**: Anzahl Anlagen, Erstellungsdatum

#### Sitzung

-   **Eigenschaften**: Datum, Nummer im Jahr, Beschlussfähigkeit
-   **Beziehung**: Zugeordnetes Referat
-   **Funktionen**: Automatische Nummerierung, Datum-Validierung

#### Beschluss

-   **Abstimmung**: Ja-/Nein-/Enthaltungs-Stimmen
-   **Ergebnis**: Angenommen/Abgelehnt/Vertagt/Unbehandelt
-   **Dokumentation**: Behandlungstext, Beschlusstext, Ausfertigung

### Frontend-Technologien

-   **Templates**: Django Template Engine mit Bootstrap-Layout
-   **Styling**: TailwindCSS für modernes, responsives Design
-   **Icons**: FontAwesome für konsistente Ikonografie
-   **Interaktivität**: Minimal JavaScript für Form-Handling

### API-Integrationen

#### Etherpad-API

```python
# Funktionen in api.py:
- create_pad(pad_id)        # Neues Etherpad erstellen
- get_text(pad_id)          # Text aus Pad abrufen
- append_text(pad_id, text) # Text zu Pad hinzufügen
- delete_pad(pad_id)        # Pad löschen
```

### Deployment-Konfiguration

#### Docker-Setup

-   **Base Image**: Python 3.9 Buster
-   **Webserver**: Gunicorn + Nginx
-   **Datenbank**: PostgreSQL in separatem Container
-   **E-Mail**: Mailcatcher für Entwicklung

#### Environment-Management

-   **Entwicklung vs. Produktion**: Über ENV-Variable steuerbar
-   **Konfiguration**: Über `.env`-Datei und Umgebungsvariablen
-   **Sicherheit**: Secret Key über Environment-Variable

### Bekannte Probleme und Lösungen

#### JSONField-Kompatibilität

-   **Problem**: Django-JSONField Compatibility mit neueren Django-Versionen
-   **Lösung**: Lokale Virtual Environment verwenden bei Fehlern

#### TailwindCSS-Entwicklung

-   **Requirement**: NPM für Tailwind-Compiler
-   **Start**: `python manage.py tailwind start` für Development
-   **Build**: `python manage.py tailwind build` für Production

### Standard-Credentials (Development)

-   **Admin-Login**: abv
-   **E-Mail**: abv@stura.htw-dresden.de
-   **Passwort**: J9AHJL4hD3vc2PwP

### Datenbank-Fixtures

Für die Ersteinrichtung sind Standard-Fixtures verfügbar:

```bash
# Referate laden
python manage.py loaddata referate

# Antragstypen laden
python manage.py loaddata antragstyp

# Test-Sitzungen (nur für Entwicklung)
python manage.py loaddata sitzungen
```

### Testing und Code-Qualität

-   **Linting**: Flake8 für Python-Code-Style
-   **Testing**: Django Test Framework (weitere Tests geplant)
-   **Dokumentation**: Automatische API-Dokumentation via PyDoc

## 📝 Entwicklungshinweise

### Code-Conventions

-   **Python**: PEP 8 Standard mit Flake8-Validierung
-   **Templates**: Django Template Standards
-   **CSS**: TailwindCSS Utility-First Approach

### Git-Workflow

-   **Feature-Branches**: Neue Features in separaten Branches
-   **Commit-Messages**: Klare, beschreibende Commit-Nachrichten
-   **Pull Requests**: Code-Review vor Merge in Main-Branch

### Performance-Optimierungen

-   **Database Queries**: Select_related und Prefetch_related nutzen
-   **Static Files**: Collectstatic für Production-Deployment
-   **Caching**: Django-Caching für häufige Datenbankabfragen (geplant)

## 📄 Lizenz

Dieses Projekt wurde im Rahmen einer Belegarbeit für Software Engineering an der HTW Dresden entwickelt.

**Entwickelt für den Allgemeinen Bereich des Studierendenrats der HTW Dresden**
