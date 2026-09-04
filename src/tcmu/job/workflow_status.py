from tcmu.job import workflow_db
from tcmu import cache
import os
import sys
from pathlib import Path

@cache
def _detect_hsh():
	import __main__
	parts = Path(__main__.__file__).parts
	hsh = parts[-2]
	wf = parts[-4]
	return hsh, wf


def stage(message):
	hsh, wf = _detect_hsh()
	# if the job is not managed by tcmu we simply print the message
	if hsh is None:
		return

	# otherwise update the workflow DB
	workflow_db.update(wf, hsh, stage=message)
