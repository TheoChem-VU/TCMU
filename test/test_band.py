import os
import tcmu
import pprint
import pytest
from scm import plams

j = os.path.join

res = tcmu.read(j(os.path.split(__file__)[0], "fixtures", "pEDA"))
# res = tcmu.read(j(os.path.split(__file__)[0], "fixtures", "BAND"))
# res = tcmu.read(j(os.path.split(__file__)[0], "fixtures", "ethane"))

# molecule:plams.Molecule = res.molecule.input
# print(tcmu.write_mol_to_amv_file("scrumpy", [molecule, molecule, molecule]))

print(res.engine)

print("Band engine")
pprint.pprint(res.band)

print("Properties")
pprint.pprint(res.properties)

print("Status:", tcmu.quick_status(j(os.path.split(__file__)[0], "fixtures", "BAND_SAC_Pd_4NDG_Py")))

# print("Molecules")
# pprint.pprint(res.molecule)

def test_pEDA():
    pEDA = tcmu.read(j(os.path.split(__file__)[0], "fixtures", "pEDA"))

    # Bond == interaction in pEDA, because that's what ADF gives and we need to be consistent. Dont think about it 
    assert pEDA.properties.energy.bond == pEDA.properties.energy.bond

    # Test the fragment energies
    assert pEDA.properties.energy.fragment_bond[0] == pytest.approx(-19420.55, abs=1e-2)
    assert pEDA.properties.energy.fragment_bond[1] == pytest.approx(-1654.13, abs=1e-2)

    # Test the interaction energy
    assert pEDA.properties.energy.interaction == pytest.approx(-47.66, abs=1e-2)

    # Test the dispersion energy
    assert pEDA.properties.energy.dispersion == pytest.approx(-15.10, abs=1e-2)

    # Test the electrostatic interaction energy
    assert pEDA.properties.energy.elstat.elstat == pytest.approx(-129.83, abs=1e-2)

    # Test the orbital interaction energy 
    assert pEDA.properties.energy.orbint.total == pytest.approx(-107.96, abs=1e-2)

    # Test the pauli repulsion energy
    assert pEDA.properties.energy.pauli.total == pytest.approx(205.23, abs=1e-2)

def test_band():
    band = tcmu.read(j(os.path.split(__file__)[0], "fixtures", "BAND"))

    # Test the bond energy
    assert band.properties.energy.bond == pytest.approx(555.91, abs=1e-2)

    # Test the band gap energy
    assert band.properties.energy.band_gap == pytest.approx(124.95, abs=1e-2)

    # Test the Fermi energy
    assert band.properties.energy.fermi_energy == pytest.approx(-440.57, abs=1e-2)

def test_lattices():
    band = tcmu.read(j(os.path.split(__file__)[0], "fixtures", "BAND"))

    # Check that VEC1 x y z has the correct values
    assert band.molecule.lattice_vectors_out[0][0] == pytest.approx(27.83, abs=1e-2)
    assert band.molecule.lattice_vectors_out[0][1] == pytest.approx(-0.17, abs=1e-2)
    assert band.molecule.lattice_vectors_out[0][2] == pytest.approx(0.0, abs=1e-2)

    # Check that VEC2 x y z has the correct values
    assert band.molecule.lattice_vectors_out[1][0] == pytest.approx(13.77, abs=1e-2)
    assert band.molecule.lattice_vectors_out[1][1] == pytest.approx(24.18, abs=1e-2)
    assert band.molecule.lattice_vectors_out[1][2] == pytest.approx(0.0, abs=1e-2)

    # 2 in, 2 out
    assert (band.molecule.lattice_n_in == band.molecule.lattice_n_out) and band.molecule.lattice_n_in == 2

if __name__ == "__main__":
    pytest.main()