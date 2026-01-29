"""
Application entry point for the Parkinsons Annotator Flask app.

Initializes the Flask application, database, routes, and optionally
loads initial data before starting the development server.
"""

import os
import threading
import webbrowser
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from parkinsons_annotator.logger import logger
from parkinsons_annotator.modules.db import (
    close_db_session,
    create_db_engine,
    create_tables,
    has_full_data
)
from parkinsons_annotator.modules.routes import route_blueprint
from parkinsons_annotator.modules.data_extraction import load_and_insert_data

load_dotenv()  # Load environment variables from .env file

DB_NAME = os.getenv("DB_NAME", "parkinsons_data.db")


# Opens the URL when program is run
def open_browser():
    """Open the local Flask application in a web browser on port 5000."""
    webbrowser.open_new("http://127.0.0.1:5000/")

def create_app():
    logger.info("Building app")

    # Get path to package folder (parkinsons_annotator) based on location of current file
    pkg_root = Path(__file__).resolve().parent

    # Determine instance folder depending on environment
    if os.getenv("IN_DOCKER") == "true":
        instance_path = Path("/app/instance")  # Docker location
    else:
        instance_path = pkg_root / "instance"  # Local development

    # Create Flask app
    app = Flask(
        __name__,
        template_folder=str(pkg_root / "templates"),
        instance_path=str(instance_path)
    )

    # Create instance folder if needed
    instance_path.mkdir(parents=True, exist_ok=True)

    # Set upload folder to within Flask instance folder
    upload_path = instance_path / "uploads"
    upload_path.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_path)

    # Put database within instance folder too because it is written at runtime
    db_path = instance_path / DB_NAME
    app.config["DB_NAME"] = str(db_path)

    # Ensure DB session is closed after each request
    app.teardown_appcontext(close_db_session)

    # Register the blueprint
    app.register_blueprint(route_blueprint)

    return app

def main():
    logger.info("Starting Parkinsons Annotator Application")

    app = create_app()

    with app.app_context():
        # Get path to database file
        db_path = Path(app.config["DB_NAME"])
        # If database does not exist, create database and tables
        if not db_path.exists():
            logger.info(f"Database '{DB_NAME}' not found. Creating new database and tables.")
            create_db_engine()  # Create the database engine and session
            create_tables()  # Create tables in the database

        # Load initial data if a table is empty
        if not has_full_data():
            try:
                logger.info("Loading initial data into the database...")
                load_and_insert_data()
            except Exception as e:
                logger.error(f"Failed to load initial data: {e}")

    # Open browser after 1 second if running locally
    if not os.getenv("IN_DOCKER"):
        threading.Timer(1, open_browser).start()
    else:
        logger.info("App available at http://localhost:8000")

    # Start the Flask app
    host = "0.0.0.0" if os.getenv("IN_DOCKER") == "true" else "127.0.0.1"
    app.run(
        host=host,
        port=5000,
        debug=True,
        use_reloader=False  # Use_reloader prevents two interfaces from opening
    )


if __name__ == "__main__":
    main()