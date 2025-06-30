# ChapterOS

An internal dashboard for the IOIT ACM Student Chapter. It helps manage recruitment results, events, and documentation.

## Prerequisites

- Python 3.6.8
- Node.js and npm

## Apps

-   `recruitments`: Manage and analyze data from member recruitment drives.
-   `form_builder`: Create custom forms for event registrations, feedback, surveys and events.
-   `documentation`: A central repository for all chapter-related documents, reports, and assets.
-   `events`: Plan, track, and manage all chapter events, workshops, and speaker sessions.
-   `team`: Manage committee member profiles, roles, and internal permissions.

## Getting Started

A `Makefile` is provided to simplify the setup process.

1.  **Clone the repository**

    ```bash
    git clone https://github.com/IOIT-ACM/ChapterOS.git
    cd ChapterOS
    ```

2.  **Set up the environment**
    This command will create a Python virtual environment, install Python dependencies from `requirements.txt`, and install Node.js dependencies from `package.json`.

    ```bash
    make setup
    ```

    Now, edit the `.env` file with your details.

2.  **Collect Django Static Files**
    This command gathers all static files (including the CSS file you just built) into the `staticfiles` directory, as defined in `settings.py`.
    ```bash
    python3 manage.py collectstatic
    ```

4.  **Run Database Migrations**
    Apply the initial database schema.
    ```bash
    python3 manage.py migrate
    ```

## Running the Application

You will need to run two processes in separate terminals for development.

1.  **Start the Django Development Server**
    This will run the backend server, typically on `http://127.0.0.1:8000/`.

    ```bash
    make run
    ```

    Alternatively, you can run the command manually:

    ```bash
    python3 manage.py runserver
    ```

2.  **Start the Tailwind CSS Watcher**
    This will watch for changes in your template files and CSS source, and automatically rebuild the main stylesheet.
    ```bash
    npm run watch
    ```

## Building for Production

When deploying the application, you need to build the static assets.

1.  **Build Static CSS**
    This command compiles the Tailwind CSS into a single production-ready file.

    ```bash
    npm run build
    ```

2.  **Collect Django Static Files**
    This command gathers all static files (including the CSS file you just built) into the `staticfiles` directory, as defined in `settings.py`.
    ```bash
    python3 manage.py collectstatic
    ```

## Environment Variables

The application requires the following environment variables, which should be placed in a `.env` file in the project root.

| Variable      | Description                           |
| ------------- | ------------------------------------- |
| `DB_HOST`     | Hostname of the MySQL database.       |
| `DB_NAME`     | Name of the MySQL database.           |
| `DB_USER`     | Username for the MySQL database.      |
| `DB_PASSWORD` | Password for the MySQL database user. |
