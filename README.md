# Genially-to-PDF Backend

## Why?

My teachers in high school were sending Genially presentations. Of course there was no way of downloading them. Convenience of having a presentation in a PDF format is massive. You can change pages faster and look at it wherever you want and however you want. So I built a backend (and a website) that handles it easily.

## Description

A FastAPI-based web service that converts [Genially](https://view.genially.com/) interactive presentations into PDF files. It uses browser automation to navigate through slides, captures each one as a PDF page, and merges them into a single downloadable document.

## How It Works

```text
User submits Genially URL → Task queued (Huey) → Browser captures slides as PDFs → Slides merged → PDF ready for download
```

1. **Submit** a Genially presentation URL via `POST /create-task`
2. **Poll** task status via `GET /task/{task_id}` to track progress
3. **Download** the final PDF via `GET /download/{task_id}` when status is `finished`

API documentation is available at `/docs` (Swagger UI) when the server is running.

## API Endpoints

| Method | Path                  | Description                                           | Rate Limit |
| ------ | --------------------- | ----------------------------------------------------- | ---------- |
| GET    | `/`                   | Redirects to Swagger docs                             | 15/min     |
| POST   | `/create-task`        | Submit a Genially URL for conversion                  | 3/min      |
| GET    | `/tasks`              | Get task statistics (total, today, completed, failed) | 10/min     |
| GET    | `/task/{task_id}`     | Check task status and progress                        | 60/min     |
| DELETE | `/task/{task_id}`     | Delete a task                                         | 5/min      |
| GET    | `/download/{task_id}` | Download the generated PDF                            | 5/min      |

### Task Statuses

- `queued` — waiting in the Huey queue
- `capturing_slides` — browser is navigating through slides
- `converting_to_pdf` — individual slide PDFs are being merged
- `finished` — PDF ready to download
- `error` — something went wrong (check `error_message`)

### Creating a Task

```json
POST /create-task
Content-Type: application/json

{
  "url": "https://view.genially.com/..."
}
```

The URL must be a `https://view.genially.com/` link.

### Pipeline Details

1. **Browser Automation** (`capture.py`): Uses [CloakBrowser](https://github.com/cloakhq/cloakbrowser) (Playwright-based) to open the Genially presentation, accept cookie banners, disable CSS animations, and hide navigation elements (including the Genially watermark). It reads the total slide count from Genially's view API, then walks through every slide using the on-screen next-slide control until the last one. Each slide is printed to PDF at A4 landscape format at 2× scale factor.

2. **PDF Merging** (`converter.py`): Sorts captured slide PDFs by number, then merges them with `PyPDF2.PdfMerger` into a single file stored in the presentations directory.

3. **Task Queue** (`huey_manager.py`): Tasks are processed asynchronously via Huey with SQLite backend. A periodic task runs every minute to clean up files older than the configured TTL.

4. **Cleanup** (`cleanup.py`): Removes presentation PDFs and slide directories that exceed `TIME_BEFORE_CLEANUP` (default: 5 minutes).

## Configuration

All configuration is via environment variables (see `app/config.py`):

| Variable                 | Default               | Description                              |
| ------------------------ | --------------------- | ---------------------------------------- |
| `DATA_DIRECTORY`         | `data/`               | Base data directory                      |
| `SLIDES_DIRECTORY`       | `data/slides/`        | Temporary slide PDF storage              |
| `PRESENTATION_DIRECTORY` | `data/presentations/` | Final merged PDF storage                 |
| `DATABASE_STORAGE_PATH`  | `database/`           | SQLite database directory                |
| `TIME_BEFORE_CLEANUP`    | `300` (5 min)         | File retention in seconds                |
| `BROWSER_DIMENTIONS`     | `1920,1080`           | Browser viewport size                    |
| `WAIT_BETWEEN_ACTIONS`   | `300`                 | ms between slide actions                 |
| `WAIT_FOR_ANIMATIONS`    | `1000`                | ms to wait for slide animations          |
| `SCALE_FACTOR`           | `2`                   | Device pixel ratio for higher resolution |
| `SLIDE_VISIBLE_TIMEOUT`  | `10000`               | ms timeout for slide visibility          |
| `NAVIGATION_TIMEOUT`     | `30000`               | ms timeout for page navigation           |
| `HEADLESS`               | `true`                | Run browser in headless mode             |
| `DEV_MODE`               | `false`               | Disable origin checking for local dev    |
| `WORKERS_COUNT`          | `2`                   | Huey consumer worker count               |

## Deployment

Configuration is in .env file

### Docker (recommended)

```bash
docker compose up --build
```

This runs the service on port `53714` (mapped to container port `8000`). See `docker-compose.yml` for resource limits and volume configuration.

The Docker image is based on `python:3.12-slim` and installs Chromium's system dependencies via Playwright. During the build it pre-downloads CloakBrowser's free Chromium build (no license key required), so the first conversion starts without delay.

### Manual

UV is required

```bash
uv sync
./start.sh
```

`start.sh` runs both the Uvicorn server and Huey consumer in parallel.

## Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Browser Automation**: [CloakBrowser](https://github.com/cloakhq/cloakbrowser) (Playwright)
- **Task Queue**: [Huey](https://huey.readthedocs.io/) (SQLite)
- **ORM**: [Peewee](https://docs.peewee-orm.com/) (SQLite)
- **PDF**: [PyPDF2](https://pypdf2.readthedocs.io/)
- **Rate Limiting**: [SlowAPI](https://slowapi.readthedocs.io/)
- **Async Server**: Uvicorn with uvloop

## License

Apache 2.0. See [LICENSE](LICENSE).

---

**Built with 💜 by [Leon135](https://leon135.xyz)**
