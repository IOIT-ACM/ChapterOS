# ChapterOS - AISSMS IOIT ACM Internal Dashboard

ChapterOS is the central management hub for the AISSMS IOIT ACM Student Chapter. It's an internal web application designed to streamline committee operations, from managing recruitment and analyzing statistics to planning events and maintaining documentation and annual events calender.

**Landing Page**
![Landing Page](docs/landing.jpeg)

**Recruitment Dashboard**
![Recruitment Dashboard](docs/drive.jpeg)

**Response Statistics**
![Response Statistics](docs/stats.jpeg)

**Application Architecture**
![Application Architecture](docs/flowchart.jpeg)

## Apps

- `recruitments`: Manage and analyze data from member recruitment drives.
- `form_builder`: Create custom forms for event registrations, feedback, surveys and events.
- `documentation`: A central repository for all chapter-related documents, reports, and assets.
- `events`: Plan, track, and manage all chapter events, workshops, and speaker sessions.
- `users`: Manage committee member profiles, roles, and internal permissions.
- _and more comming soon..._

## Tech Stack

- **Backend:** Django, Python
- **Frontend:** HTML, Tailwind CSS, Vanilla JavaScript
- **Database:** MySQL
- **Deployment:** Gunicorn / Passenger

## Setup

Follow these instructions to set up the project on your local machine for development and testing.

### Prerequisites

- Python 3.6.8
- Node.js and npm
- A running MySQL server

### 1. Clone the Repository

```bash
git clone https://github.com/IOIT-ACM/ChapterOS.git
cd ChapterOS
```

### 2. Setup the Environment

A `Makefile` is provided to simplify the setup process. This command will create a Python virtual environment, install all Python and Node.js dependencies, and create a `.env` file from the example.

```bash
make setup
```

### 3. Configure Environment Variables

Edit the newly created `.env` file with your MySQL database credentials.

```ini
# .env
DB_HOST="127.0.0.1"
DB_NAME="chapteros_db"
DB_USER="your_db_user"
DB_PASSWORD="your_db_password"
```

### 4. Run Initial Database Migrations

Apply the initial database schema and create all necessary tables.

```bash
# Make sure your virtual environment is active
source venv/bin/activate

python3 manage.py migrate
```

### 5. Create a Superuser

To access the Django Admin panel (`/admin/`), you need to create a superuser account.

```bash
python3 manage.py createsuperuser
```

Follow the prompts to create your admin account.

## Running the Application

For development, you need to run two processes in separate terminal windows.

1.  **Start the Django Development Server**
    This runs the backend on `http://127.0.0.1:8000/`.

    ```bash
    make run
    # Or manually: python3 manage.py runserver
    ```

2.  **Start the Tailwind CSS Watcher**
    This watches for changes in your template and CSS files and automatically rebuilds the stylesheet.

    ```bash
    npm run watch
    ```

## ⚠️ Important: Database Migrations

Migrations are how Django tracks changes to your database schema (your `models.py` files). It is critical that all developers handle them correctly to ensure consistency.

### The Correct Workflow

1.  After you change a model (e.g., add a field to `apps/users/models.py`), run `makemigrations`. This creates a new migration file that represents your changes.
    ```bash
    python3 manage.py makemigrations
    ```
2.  Next, run `migrate` to apply this change to your local database.
    ```bash
    python3 manage.py migrate
    ```
3.  Commit both your model changes and the **newly generated migration file** to Git.

### Key Rules

- **DO NOT DELETE MIGRATION FILES.** These files are a historical record of your database schema. Deleting them can cause irreversible issues for other developers and in production. If you make a mistake, it's better to create a new migration to reverse the change.
- **ALWAYS RUN `migrate` AFTER PULLING CHANGES.** After you pull new code from the repository, always run `python3 manage.py migrate` to apply any database changes made by other developers.
- **RESOLVE MIGRATION CONFLICTS CAREFULLY.** If you encounter conflicts, ask for help. Never just delete the conflicting files. Contact webmaster while doing so.

## Building for Production

When deploying the application, you need to build the static assets and collect them into a single directory.

1.  **Build Static CSS**
    This command compiles and minifies the Tailwind CSS.

    ```bash
    npm run build
    ```

2.  **Collect Django Static Files**
    This command gathers all static files (CSS, JS, images) into the `staticfiles` directory, which is then served by WhiteNoise or your web server.
    ```bash
    python3 manage.py collectstatic
    ```
