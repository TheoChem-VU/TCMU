"""
This module is used for gathering data about literature and generating citations formatted in various ways.
"""
import requests
import json
import os
from tcmu import spell_check, cache_file


## Helper functions handling identifiers
def _extract_doi(identifier: str) -> str:
	'''
	Extract the DOI part from a identifier.

	Args:
		identifier: a identifier possibly containing a DOI. 
			This could be a plain DOI or a link to a webpage.

	Returns:
		If the identifier contains a DOI return the DOI. Else returns ``None``.
	'''
	# all DOIs start with a 10.
	if not '10.' in identifier:
		return None

	# remove all parts after '?' that may be present on a identifier
	identifier = identifier.split('?')[0]
	# split on the '10.' and return the DOI
	return '10.' + identifier.split('10.')[1]


@cache_file('dois')
def _get_doi_data(doi: str) -> dict:
	'''
	Get information about an article using the crossref.org API.

	Args:
		doi: the DOI to get information about.
	'''
	print(f'http://api.crossref.org/works/{doi}')
	data = requests.get(f'http://api.crossref.org/works/{doi}').text
	if data == 'Resource not found.':
		raise ValueError(f'Could not find DOI {doi}.')
	data = json.loads(data)
	return _standardize_doi_data(data)


def _standardize_doi_data(data: dict) -> dict:
	...


