"""
Tests for the fetch_variant_validator() function.

References:
Testing APIs with PyTest
(https://codilime.com/blog/testing-apis-with-pytest-mocks-in-python/)

Credit: 
Initial tests were written manually. To improve test coverage, additional tests were generated with 
GitHub Copilot and then reviewed.
"""

from unittest.mock import patch
import requests
import pytest
from parkinsons_annotator.utils.variantvalidator_fetch import fetch_variant_validator, VariantDescriptionError, VariantValidatorResponseError

# Expected successful API call
def test_fetch_variant_validator_success():
    """Test that a correct VCF-style variant returns the correct HGVS, HGNC ID, and OMIM ID."""
    variant_description = "17:45983420:G:T"
    result = fetch_variant_validator(variant_description)
    expected = {
    "HGVS nomenclature": "NM_001377265.1:c.841G>T",
    "HGNC ID": "HGNC:6893",
    "OMIM ID": "157140"
    }
    assert result == expected


# Empty variant description provided
@patch("requests.get")  # Replaces requests.get with a mock object during this test
def test_fetch_variant_validator_empty(mock_get):
    """Test that empty variant strings raise VariantDescriptionError."""
    variant_description = ""
    with pytest.raises(VariantDescriptionError):
        fetch_variant_validator(variant_description)


# Passing a non-string as the variant description
@patch("requests.get")  # Replaces requests.get with a mock object during this test
def test_fetch_variant_validator_non_string_variant(mock_get):
    """Test that non-strings raise VariantDescriptionError."""
    variant_description = 5
    with pytest.raises(VariantDescriptionError):
        fetch_variant_validator(variant_description)


# Invalid variant description provided
@patch("requests.get")  # Replaces requests.get with a mock object during this test
def test_fetch_variant_validator_invalid_description(mock_get):
    """Test that invalid variant styles raise VariantDescriptionError."""
    variant_description = "chr17(GRCh38):g.50198002C>A"
    with pytest.raises(VariantDescriptionError):
        fetch_variant_validator(variant_description)


# Invalid chromosome provided
@patch("requests.get")  # Replaces requests.get with a mock object during this test
def test_fetch_variant_validator_invalid_chromosome(mock_get):
    """Test that chromosome values that aren't 1-22, X, Y raise VariantDescriptionError."""
    variant_description = "23:12345:A:T"
    with pytest.raises(VariantDescriptionError):
        fetch_variant_validator(variant_description)


# Invalid genomic position provided
@patch("requests.get")  # Replaces requests.get with a mock object during this test
def test_fetch_variant_validator_invalid_position(mock_get):
    """Test that genomic positions that aren't numeric raise VariantDescriptionError."""
    variant_description = "17:S:G:T"
    with pytest.raises(VariantDescriptionError):
        fetch_variant_validator(variant_description)


# Invalid reference or alternate bases provided
@patch("requests.get")  # Replaces requests.get with a mock object during this test
def test_fetch_variant_validator_invalid_bases(mock_get):
    """Test that invalid reference or alternate bases raise VariantDescriptionError."""
    variant_description = "17:45983420:Q:T"
    with pytest.raises(VariantDescriptionError):
        fetch_variant_validator(variant_description)


# API failure
@patch("requests.get")  # Replaces requests.get with a mock object during this test
def test_fetch_variant_validator_api_failure(mock_get):  # The mock_get is the mock object
    """Test that an API failure raises VariantValidatorResponseError after max retries using a mocked request."""
    variant_description = "17:45983420:G:T"
    mock_get.side_effect = requests.exceptions.RequestException()  # Simulate an API failure
    with pytest.raises(VariantValidatorResponseError):
        fetch_variant_validator(variant_description)
    assert mock_get.call_count == 5  # Retry loop should call API 5 times before failing


# No valid HGVS key in the JSON response from Variant Validator
@patch("requests.get")  # Replaces requests.get with a mock object during this test
def test_fetch_variant_validator_no_hgvs_key(mock_get):
    """Test that variants with no valid HGVS (:c.) key raise VariantValidatorResponseError."""
    variant_description = "1:9999999999:A:T"
    with pytest.raises(VariantValidatorResponseError):
        fetch_variant_validator(variant_description)
