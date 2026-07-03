# Job imports
from tcmu.cache import cache, cache_file, timed_cache
from tcmu import log
from tcmu.database import DataBase
from tcmu.analysis.pyfrag import PyFragResult, get_pyfrag_results
from tcmu.analysis.task_specific.irc import concatenate_irc_trajectories
from tcmu.analysis.vdd.charge import VDDCharge

# from tcmu.analysis.vdd.manager import VDDChargeManager, create_vdd_charge_manager # Don't load in vdd as it has an annoying pandas dependency that cannot be avoided upon importing
from tcmu.analysis.vibration.ts_vibration import avg_relative_bond_length_delta, determine_ts_reactioncoordinate, validate_transitionstate
from tcmu.cite import cite, _get_doi_data, _get_doi_data_from_title, _get_doi_data_from_query, _get_publisher_city, _get_journal_abbreviation
from tcmu.connect import Connection, Local, Server, ServerFile
from tcmu.data.functionals import categories, functional_name_from_path_safe_name, functionals, get_available_functionals, get_functional
from tcmu.environment import requires_optional_package
from tcmu.geometry import KabschTransform, MolTransform, Transform, apply_rotmat, get_rotmat, rotate, rotmat_to_angles, vector_align_rotmat
from tcmu.results.read import get_info, quick_status, read, get_timing
from tcmu.results.result import Result
from tcmu.job.workflow import WorkFlow
from tcmu.job import workflow_db, workflow_status
from tcmu.job.adf import ADFFragmentJob, ADFJob, DensfJob
from tcmu.job.ams import AMSJob
from tcmu.job.crest import CRESTJob, QCGJob
from tcmu.job.dftb import DFTBJob
from tcmu.job.nmr import NMRJob
from tcmu.job.orca import ORCAJob, GOATJob
from tcmu.job.xtb import XTBJob
from tcmu.molecule import from_string, guess_fragments, load, number_of_electrons, save, write_mol_to_amv_file, write_mol_to_xyz_file
# from tcmu.report.report import SI
from tcmu.timer import timer
from tcmu.report import simple_sheets

__all__ = [
    "ADFFragmentJob",
    "ADFJob",
    "DensfJob",
    "AMSJob",
    "CRESTJob",
    "QCGJob",
    "DFTBJob",
    "NMRJob",
    "ORCAJob",
    "GOATJob",
    "XTBJob",
    "log",
    "from_string",
    "guess_fragments",
    "load",
    "number_of_electrons",
    "save",
    "write_mol_to_amv_file",
    "write_mol_to_xyz_file",
    "get_info",
    "quick_status",
    "read",
    "Result",
    "timer",
    "Connection",
    "Local",
    "Server",
    "ServerFile",
    "cache",
    "cache_file",
    "cite",
    "requires_optional_package",
    "Transform",
    "KabschTransform",
    "MolTransform",
    "get_rotmat",
    "rotmat_to_angles",
    "apply_rotmat",
    "rotate",
    "vector_align_rotmat",
    "PyFragResult",
    "get_pyfrag_results",
    "concatenate_irc_trajectories",
    "VDDCharge",
    "avg_relative_bond_length_delta",
    "determine_ts_reactioncoordinate",
    "validate_transitionstate",
    "categories",
    "functionals",
    "functional_name_from_path_safe_name",
    "get_functional",
    "get_available_functionals",
    # "SI",
    "timed_cache",
]
