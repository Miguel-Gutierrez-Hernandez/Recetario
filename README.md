# Boti — Asistente Personal

Boti es un asistente de voz y texto hecho en Python con Flet. Está pensado para gestionar notas, recetas, búsquedas y controles multimedia desde una única interfaz.

- Interfaz de chat y paneles para notas, recetas y ajustes
- Sincronización con Notion para notas y recetas
- Integración local con SQLite para recetario y datos persistentes
- Comandos de voz y texto con soporte para YouTube, Spotify, Wikipedia y más

---

## Requisitos

- Python 3.12
- Flet compatible con Flutter SDK
- Cuenta Anthropic con API key
- Cuenta Notion y bases de datos configuradas (opcional)

---

## Instalación

```bash
git clone https://github.com/tu-usuario/Recetario.git
cd Recetario
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r src/boti/requirements.txt
```

> Nota: este repositorio no incluye un archivo `.env.ejemplo`. Crea manualmente un `.env` en la raíz del proyecto y agrega tus claves.

---

## Configuración

Crea el archivo `.env` en la raíz del proyecto con las variables necesarias:

```env
NOTION_TOKEN=secret_...
NOTION_NOTES_DB=id-de-tu-base-de-datos
NOTION_RECIPES_DB=id-de-tu-base-de-datos
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
```

- `NOTION_TOKEN`: token de integración de Notion
- `NOTION_NOTES_DB`: ID de la base de datos de notas
- `NOTION_RECIPES_DB`: ID de la base de datos de recetas
- `SPOTIFY_CLIENT_ID` y `SPOTIFY_CLIENT_SECRET`: opcionales para búsquedas en Spotify

---

## Ejecución local

```bash
source .venv/bin/activate
python src/boti/main.py
```

---

## Compilar para Android

```bash
flet build apk src/boti
```

---

## Estructura principal

```text
Recetario/
├── .env                    # Variables de entorno (no versionado)
├── README.md
├── src/boti/
│   ├── main.py             # Enrutador y gestor principal de Flet
│   ├── config.py           # Carga de entorno, detección de plataforma y rutas seguras
│   ├── flet.yaml           # Configuración de Flet / Android
│   ├── pyproject.toml      # Configuración del proyecto Flet
│   ├── requirements.txt    # Dependencias Python
│   ├── modules/            # Lógica de comandos e integraciones
│   ├── views/              # Vistas de la interfaz
│   └── utils/              # Utilidades de voz, texto y comandos
```

---

## Funcionalidades clave

- Chat de texto con Boti usando Claude
- Recetario local con SQLite
- Notas sincronizables con Notion
- Búsqueda en Wikipedia
- Reproducción de YouTube desde comandos
- Control de música/Spotify
- Manejo de hora y alarmas
- Soporte multiplataforma local y Android

---

## Comandos de ejemplo

- `receta de tortilla` → busca en el recetario local
- `anota: comprar leche` → guarda la nota local y la sincroniza a Notion
- `qué es la fotosíntesis` → busca en Wikipedia
- `pon música de jazz` → abre YouTube
- `qué hora es` → responde con la hora actual
- cualquier otra cosa → responde Claude (Boti)
