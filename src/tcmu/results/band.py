import tcmu.results.cache as cache
from tcmu import constants
from tcmu.results.result import Result

# Results module for ams BAND, the periodic software package

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

def get_properties(info: Result) -> Result:
    """Function to get properties from a BAND calculation.

    Args:
        info: Result object containing BAND properties.

    Returns:
        :Result object containing properties from the BAND calculation:

            - **energy.bond (float)** – bonding energy (|kcal/mol|).
            - **energy.fermi (float)** – Fermi energy (|kcal/mol|).
            - **energy.band_gap (float)** – band gap energy (|kcal/mol|).
            - **energy.elstat.total (float)** – total electrostatic potential (|kcal/mol|).
            - **energy.orbint.total (float)** – total orbital interaction energy (|kcal/mol|).
            - **energy.pauli.total (float)** – total Pauli repulsion energy (|kcal/mol|).
            - **energy.dispersion (float)** – total dispersion energy (|kcal/mol|).
            - **energy.interaction (float)** – total interaction energy (|kcal/mol|).
    """

    assert info.engine == "band", f"This function reads BAND data, not {info.engine} data"

    properties = Result()

    reader_band = cache.get(info.files["band.rkf"])

    # read energies (given in Ha in rkf files)
    properties.energy.bond = reader_band.read("Bond energies", "final bond energy") * constants.HA2KCALMOL

    # Only reported in pEDA calculations, ALSO disappointingly absent in older versions of band
    # it's not mentioned in the changelog exactly when, but the 2023 version doesn't have it while the 2025 version does
    if "PEDA bond energy terms" in reader_band._sections:
        properties.energy.elstat.elstat = reader_band.read("PEDA bond energy terms", "Electrostatic") * constants.HA2KCALMOL
        properties.energy.pauli.total = reader_band.read("PEDA bond energy terms", "PauliRepulsion") * constants.HA2KCALMOL
        properties.energy.orbint.total = reader_band.read("PEDA bond energy terms", "OrbitalInteraction") * constants.HA2KCALMOL

        # Can be absent if the dispersion wasn't turned on
        if "Dispersion" in reader_band:
            properties.energy.dispersion = reader_band.read("PEDA bond energy terms", "Dispersion") * constants.HA2KCALMOL
        else:
            properties.energy.dispersion = 0.0

        properties.energy.interaction = reader_band.read("PEDA bond energy terms", "TotalInteraction") * constants.HA2KCALMOL
    
    # determine if MOs are unrestricted or not
    # generally, nspin is 1 for restricted and 2 for unrestricted calculations
    properties.unrestricted_mos = reader_band.read("DOS", "nSpin") == 2

    # Notable band properties
    properties.energy.band_gap = reader_band.read("BandStructure", "BandGap") * constants.HA2KCALMOL
    properties.energy.fermi_energy = reader_band.read("DOS", "Fermi Energy") * constants.HA2KCALMOL

    return properties