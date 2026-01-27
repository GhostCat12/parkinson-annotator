"""
Routes for UI, search, upload, and shutdown.

These creates the user interface and generates variables from the search and input sections which can
be used within the rest of the program.
The visuals and interactive elements of the interface are stored in a html file.
"""

import os
import markdown
from dotenv import load_dotenv
from flask import Blueprint, render_template, request, jsonify, current_app

from parkinsons_annotator.modules.database_search import (
    database_list,
    SearchFieldEmptyError,
    NoMatchingRecordsError
)
from parkinsons_annotator.modules.data_extraction import (
    dataframes,
    load_single_file,
    fill_variant_notation,
    enrich_hgvs,
    enrich_clinvar,
    insert_dataframe_to_db
)
from parkinsons_annotator.modules.db import get_db_session, close_db_session
from parkinsons_annotator.logger import logger
from parkinsons_annotator.utils.data_checks import compare_uploaded_vs_existing


load_dotenv()  # Load environment variables from .env file

route_blueprint = Blueprint("routes", __name__)


@route_blueprint.route('/', methods=['GET'])
def index():
    """Render the index HTML page."""
    return render_template("index.html")


@route_blueprint.route('/about', methods=['GET'])
def about():
    """Render the about HTML page."""
    return render_template("about.html")


@route_blueprint.route('/search', methods=['POST'])
def search():
    """Handle search queries."""
    data = request.get_json()
    search_value = data.get('query', '').lower().strip()
    search_category = data.get('searchCategory', '').lower().strip()
    search_classification = data.get('searchClassification', '').lower().strip()

    #Specify column orders to display in Flask for each search category
    column_orders = {
        "patient_name": ["hgvs", "gene_symbol", "classification"],
        "classification": ["hgvs", "gene_symbol"],
        "gene_symbol": ["hgvs", "classification", "name"],
        "variant": None,  # handled separately
    }

    logger.info(f"User searched for: {search_value}, category: {search_category}")

    # Call the database search function
    try:
        results = database_list(search_category=search_category, search_value=search_value, search_classification=search_classification)
    except SearchFieldEmptyError:
        return jsonify({"message": "Missing search fields"}), 400
    except NoMatchingRecordsError:
        return jsonify({"message": "No matching records found"}), 404
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        return jsonify({"message": "Internal server error"}), 500

    # Special handling for variant searches which return 2 tables:
    if search_category == 'variant':
        # results = [(VariantORM, "patient1"), (VariantORM, "patient2"), ...]
        variant_object = results[0].Variant  # get first ORM object in list, contains variant info
        patient_list = [row.name for row in results]  # get list of patient names from all rows

        # Create a dictionary for the variant with variant info fields
        variant_dict = {
            "HGVS notation": variant_object.hgvs,
            "Genomic notation": variant_object.vcf_form,
            "ClinVar variant ID": variant_object.clinvar_id,
            "Gene symbol": variant_object.gene_symbol,
            "cDNA change": variant_object.cdna_change,
            "ClinVar accession": variant_object.clinvar_accession,
            "ClinVar consensus classification": variant_object.classification,
            "Number of submitted records": variant_object.num_records,
            "Review status": variant_object.review_status,
            "Associated condition": variant_object.associated_condition,
            "ClinVar record URL": variant_object.clinvar_url,
        }

        return jsonify({
            "column_order": list(variant_dict.keys()), # Table column order set to the same as variant_dict order
            "results": {"variant": variant_dict, "patients": patient_list}
        }), 200

    # Other search types:
    else:
        column_order = column_orders.get(search_category)
        return jsonify({
            "column_order": column_order,
            "results": results
        }), 200


@route_blueprint.route('/upload', methods=['POST'])
def upload_file():
    """Handle a single file upload, enrich variant data, and insert into the database."""
    # Check if a file was uploaded
    if 'file' not in request.files:
        return "No file part in the request", 400

    # Get file from form
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    # Ensure upload folder exists
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    # Save file to upload directory
    filepath = os.path.join(upload_dir, file.filename)
    file.save(filepath)
    logger.info(f"Uploaded file saved to: {filepath}")

    # Get database session
    session = get_db_session()

    # Run data extraction and insertion
    try:
        # Clear cache of previous dataframes
        dataframes.clear()
        # Load uploaded file
        load_single_file(filepath)
        # Enrich + insert for ONLY this patient
        for patient_name, df in dataframes.items():
            # Ensure patient does not already exist in DB with same variants
            result = compare_uploaded_vs_existing(patient_name, df, session)
            if result["exists"] and result["identical"]:
                logger.info(f"Upload for '{patient_name}' skipped — identical variants.")
                return (f"Patient '{patient_name}' already exists in upload folder with identical variants. "
                        f"Upload rejected."), 409

            # Get notation/HGVS/ClinVar annotation then insert into DB
            df = (df
                  .pipe(fill_variant_notation)
                  .pipe(enrich_hgvs, session=session)
                  .pipe(enrich_clinvar, session=session)
                  )
            insert_dataframe_to_db(patient_name, df, session)
        # Commit any changes to DB
        session.commit()
        logger.info(f"File '{file.filename}' uploaded and processed successfully!")
        return f"File '{file.filename}' uploaded and processed successfully!", 200

    except Exception as e:
        logger.error(f"Data extraction failed: {e}")
        if session:
            session.rollback()  # rollback on error
        return f"Upload failed: {e}", 500

    finally:
        if session:
            close_db_session()  # ensures session is closed