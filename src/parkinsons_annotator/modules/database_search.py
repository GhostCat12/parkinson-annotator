"""
This module performs a database search using SQLAlchemy ORM.

Functions:
    database_list: Return list of database objects matching the search criteria.
        Example: if search_type is 'variant', return list of patients with that variant.

Exceptions:
    SearchFieldEmptyError: Raised if search_type or search_value is empty.
    NoMatchingRecordsError: Raised if search finds no records matching the search criteria.
"""

from parkinsons_annotator.modules.models import Variant, Patient, Connector
from parkinsons_annotator.logger import logger
from parkinsons_annotator.modules.db import get_db_session
from sqlalchemy import select

# Custom exceptions
class SearchFieldEmptyError(Exception):
    pass


class NoMatchingRecordsError(Exception):
    pass


# Search function
def database_list(search_category=None, search_value=None, search_classification=None):
    """
    Search the database based on user-specified category and value.

    Args:
        search_category (str): Category of search specified by the user.
            Determines what is returned:
                - 'variant': List of patients with matching variant and dictionary of variant info.
                - 'gene_symbol': List of variants for that gene.
                - 'classification': List of variants with that classification.
                - 'patient': List of variants for that patient.
        search_value (str): Input value for the search, e.g. "NM_001377265.1:c.841G>T".
        search_classification (str): Classification to search for, e.g. "Pathogenic". Only used in classification search.

    Returns:
        list: List of query results (e.g., patient names).
    """

    # Get database session for query
    db_session = get_db_session()

    # Raise error if no search category or value provided
    if not search_category:
        logger.warning("Search called without search_category")
        raise SearchFieldEmptyError("Missing search field input.")

    # Based on search category, perform SQL query to return list from database
    # --- Search by variant ---
    if search_category == 'variant':
        logger.info("Searching database for variant")

        # Normalise search value: strip whitespace and convert to uppercase
        search_value = search_value.strip().upper()

        # Search in HGVS format:
        if search_value.startswith(("NM", "NC")):
            logger.info(f"Searching variant by HGVS: {search_value}")
            filter_column = Variant.hgvs

        else:
            filter_column = Variant.vcf_form

        # Single join query to get patient name and variant object info
        stmt = (
            select(
                Variant, Patient.name
            )
            .join(Connector, Variant.vcf_form == Connector.variant_vcf_form)
            .join(Patient, Patient.name == Connector.patient_name)
            .where(filter_column.ilike(search_value))
        )

        # Execute query and fetch results
        query_results = db_session.execute(stmt).mappings().all()
        logger.info(f"Found {len(query_results)} patients with variant.")

        # Raise exception if no matching records found
        if not query_results:
            logger.info(f"No patients found with variant '{search_value}'.")
            raise NoMatchingRecordsError(f"No patients found with variant '{search_value}'.")

        # Returns list of tuples [(Variant Object, patient_name1), (Variant Object, patient_name2), ...]
        # Variant search returns an ORM object which is not compatible with .mappings()
        # and so is handled in search route
        return query_results

    # --- Search by gene symbol ---
    elif search_category == 'gene_symbol':
        logger.info(f"Searching database for gene symbol= '{search_value}'")

        # Find list of variants for that gene with patient name and variant classification
        stmt = (
            select(
                Variant.hgvs,
                Patient.name,
                Variant.classification
            )
            .join(Connector, Connector.variant_vcf_form == Variant.vcf_form)
            .join(Patient, Patient.name == Connector.patient_name)
            .where(Variant.gene_symbol.ilike(search_value))
        )
        # Query DB: mappings() converts SQLAlchemy tuple to list of dictionaries for JSON
        query_results = db_session.execute(stmt).mappings().all()
        logger.info(f"Found {len(query_results)} for gene symbol '{search_value}'")

        # Raise exception if no matching records found
        if not query_results:
            logger.info(f"No variants found with gene symbol '{search_value}'.")
            raise NoMatchingRecordsError(f"No variants found with gene symbol '{search_value}'.")

        # Convert SQLAlchemy rowmapping objects into real dictionaries for JSON
        return [dict(row) for row in query_results]

    # --- Search by patient ---
    elif search_category in ('patient', 'patient_name'):
        logger.info(f"Searching database for patient= '{search_value}'")

        # Find list of variants for that patient with the pathogenicity
        stmt = (
            select(
                Variant.hgvs,
                Variant.gene_symbol,
                Variant.classification
            )
            .join(Connector, Connector.variant_vcf_form == Variant.vcf_form)
            .join(Patient, Patient.name == Connector.patient_name)
            .where(Patient.name.ilike(f"%{search_value}%"))
        )
        query_results = db_session.execute(stmt).mappings().all()
        logger.info(f"Found {len(query_results)} variants for patient '{search_value}'")

        # Raise exception if no matching records found
        if not query_results:
            logger.info(f"No variants found for patient '{search_value}'.")
            raise NoMatchingRecordsError(f"No variants found for patient '{search_value}'.")

        # Convert SQLAlchemy rowmapping objects into real dictionaries for JSON
        return [dict(row) for row in query_results]

    elif search_category == 'classification':
        logger.info(f"Searching database for classification= '{search_classification}'")
        # Find list of variants with that classification
        stmt = (
            select(Variant.hgvs, Variant.gene_symbol)
            .where(Variant.classification.ilike(search_classification))
        )

        query_results = db_session.execute(stmt).mappings().all()
        logger.info(f"Found {len(query_results)} variants for classification '{search_classification}'")
        # Raise exception if no matching records found
        if not query_results:
            logger.info(f"No variants found for classification '{search_classification}'.")
            raise NoMatchingRecordsError(f"No variants found for classification '{search_classification}'.")
        # Convert SQLAlchemy rowmapping objects into real dictionaries for JSON
        return [dict(row) for row in query_results]