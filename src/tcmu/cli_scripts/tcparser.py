import click
from tcmu.cli_scripts.cite import generate_citations
from tcmu.cli_scripts.concatenate_irc import concatenate_irc_paths
from tcmu.cli_scripts.geo import calculate_geometry_parameter
from tcmu.cli_scripts.job_script import optimize_geometry
from tcmu.cli_scripts.read import read_results
from tcmu.cli_scripts.resize_figures import resize
from tcmu.cli_scripts.workflow import workflow


@click.group()
def tcmu():
    """TCMU command line interface."""
    pass


tcmu.add_command(read_results)
tcmu.add_command(optimize_geometry)
tcmu.add_command(generate_citations)
tcmu.add_command(calculate_geometry_parameter)
tcmu.add_command(concatenate_irc_paths)
tcmu.add_command(resize)
tcmu.add_command(workflow)
