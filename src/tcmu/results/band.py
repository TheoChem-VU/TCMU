from typing import Dict, List

import numpy as np
from scm.plams import KFReader

import tcmu.results.cache as cache
from tcmu import constants
from tcmu.results.cache import TrackKFReader
from tcmu.results.result import Result
from tcmu.results import adf
from tcmu.typing_utilities import Array1D, ensure_list

# Im not sure I care about this
def get_calc_settings(info: Result) -> Result:
    """Function to read calculation settings for a BAND calculation.

    Args:
        info: Result object containing BAND calculation settings.

    Returns:
        :Result object containing properties from the BAND calculation:

            - **task (str)** – the task that was set for the calculation.
            - **charge (int)** - the charge of the system.
    """
    assert info.engine == "band", f"This function reads band data, not {info.engine} data"

    settings = Result()

    # Set the task
    settings.task = info.input.task

    reader_band = cache.get(info.files["band.rkf"])

    settings.charge = reader_band.read("Molecule", "Charge")

    return settings

### copy of adf without vdd
def get_properties(info: Result) -> Result:
    """Function to get properties from an BAND calculation.

    Args:
        info: Result object containing BAND properties.

    Returns:
        :Result object containing properties from the BAND calculation:

            - **energy.bond (float)** – bonding energy (|kcal/mol|).
            - **energy.elstat.total (float)** – total electrostatic potential (|kcal/mol|).
            - **energy.elstat.Vee (float)** – electron-electron repulsive term of the electrostatic potential (|kcal/mol|).
            - **energy.elstat.Ven (float)** – electron-nucleus attractive term of the electrostatic potential (|kcal/mol|).
            - **energy.elstat.Vnn (float)** – nucleus-nucleus repulsive term of the electrostatic potential (|kcal/mol|).
            - **energy.orbint.total (float)** – total orbital interaction energy containing contributions from each symmetry label and correction energy(|kcal/mol|).
            - **energy.orbint.{symmetry label} (float)** – orbital interaction energy from a specific symmetry label (|kcal/mol|).
            - **energy.orbint.correction (float)** - orbital interaction correction energy, the difference between the total and the sum of the symmetrized interaction energies (|kcal/mol|)
            - **energy.pauli.total (float)** – total Pauli repulsion energy (|kcal/mol|).
            - **energy.dispersion (float)** – total dispersion energy (|kcal/mol|).
            - **vibrations.number_of_modes (int)** – number of vibrational modes for this molecule, 3N-5 for non-linear molecules and 3N-6 for linear molecules, where N is the number of atoms.
            - **vibrations.number_of_imag_modes (int)** – number of imaginary vibrational modes for this molecule.
            - **vibrations.frequencies (float)** – vibrational frequencies associated with the vibrational modes, sorted from low to high (|cm-1|).
            - **vibrations.intensities (float)** – vibrational intensities associated with the vibrational modes (|km/mol|).
            - **vibrations.modes (list[float])** – list of vibrational modes sorted from low frequency to high frequency.
            - **vibrations.character (str)** – Character of the molecule based on the number of imaginary vibrational modes. Can be "minimum" or "transition state".
    """

    assert info.engine == "band", f"This function reads BAND data, not {info.engine} data"

    properties = Result()

    if info.band.task.lower() == "vibrationalanalysis":
        reader_ams = cache.get(info.files["ams.rkf"])
        properties.vibrations = adf._read_vibrations(reader_ams)
        return properties

    reader_band = cache.get(info.files["band.rkf"])

    # read energies (given in Ha in rkf files)
    properties.energy.bond = reader_band.read("Bond energies", "final bond energy") * constants.HA2KCALMOL

    # determine if MOs are unrestricted or not
    # general, nspin is 1 for restricted and 2 for unrestricted calculations
    properties.unrestricted_mos = reader_band.read("DOS", "nSpin") == 2

    # properties.energy.elstat = reader_band.read("PEDA", "FragmentElstat")[1] * constants.HA2KCALMOL
    # properties.energy.dispersion = reader_band.read("PEDA", "FragmentDispersion")[1] * constants.HA2KCALMOL

    properties.band_gap = reader_band.read("BandStructure", "BandGap") * constants.HA2KCALMOL
    properties.energy.fermi_energy = reader_band.read("DOS", "Fermi Energy") * constants.HA2KCALMOL


    return properties

    # total electrostatic potential
    ret.energy.elstat.total = reader_band.read("Energy", "elstat") * constants.HA2KCALMOL

    # we can further decompose elstat if it was enabled
    if info.files.out:
        with open(info.files.out) as output:
            lines = output.readlines()

        skip_next = -1
        for line in lines:
            if "Electrostatic Interaction Energies" in line:
                skip_next = 4
                continue
            if skip_next == 0:
                f1, f2, Vee, Ven, Vnn, total = line.strip().split()
                ret.energy.elstat.Vee = float(Vee) * constants.HA2KCALMOL
                ret.energy.elstat.Ven = float(Ven) * constants.HA2KCALMOL
                ret.energy.elstat.Vnn = float(Vnn) * constants.HA2KCALMOL
            skip_next -= 1

    # print(info.files)

    # read the total orbital interaction energy
    ret.energy.orbint.total = reader_band.read("Energy", "Orb.Int. Total") * constants.HA2KCALMOL

    # to calculate the orbital interaction term:
    # the difference between the total and the sum of the symmetrized interaction energies should be calculated
    # therefore the correction is first set equal to the total orbital interaction.
    ret.energy.orbint.correction = ret.energy.orbint.total

    # looping over every symlabel, to get the energy per symmetry label
    for symlabel in info.band.symmetry.labels:
        symlabel = symlabel.split(":")[0]
        ret.energy.orbint[symlabel] = reader_band.read("Energy", f"Orb.Int. {symlabel}") * constants.HA2KCALMOL

        # the energy per symmetry label is abstracted from the "total orbital interaction"
        # obtaining the correction to the orbital interaction term
        ret.energy.orbint.correction -= ret.energy.orbint[symlabel]

    ret.energy.pauli.total = reader_band.read("Energy", "Pauli Total") * constants.HA2KCALMOL
    ret.energy.dispersion = reader_band.read("Energy", "Dispersion Energy") * constants.HA2KCALMOL

    if ("Thermodynamics", "Gibbs free Energy") in reader_band:
        ret.energy.gibbs = reader_band.read("Thermodynamics", "Gibbs free Energy") * constants.HA2KCALMOL
        ret.energy.enthalpy = reader_band.read("Thermodynamics", "Enthalpy") * constants.HA2KCALMOL
        ret.energy.nuclear_internal = reader_band.read("Thermodynamics", "Internal Energy total") * constants.HA2KCALMOL

    # vibrational information
    if ("Vibrations", "nNormalModes") in reader_band:
        ret.vibrations = adf._read_vibrations(reader_band)

    # read spin-squared operator info
    # the total spin
    S = abs(info.band.spin_polarization) / 2
    ret.s2_expected = S * (S + 1)
    # # this is the real expectation value
    if ("Properties", "S2calc") in reader_band:
        ret.s2 = reader_band.read("Properties", "S2calc")
    else:
        ret.s2 = 0

    # # calculate the contamination
    # # if S is 0 then we will get a divide by zero error, but spin-contamination should be 0
    if S != 0:
        ret.spin_contamination = (ret.s2 - ret.s2_expected) / (ret.s2_expected)
    else:
        ret.spin_contamination = 0

    ret.dipole_vector = reader_band.read("Properties", "Dipole")
    ret.dipole_moment = np.linalg.norm(ret.dipole_vector)
    ret.quadrupole_moment = reader_band.read("Properties", "Quadrupole")
    ret.dens_at_atom = ensure_list(reader_band.read("Properties", "Electron Density at Nuclei"))

    ret.excitations = adf._read_excitations(reader_band)

    return ret