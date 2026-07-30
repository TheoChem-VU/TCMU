import os
import tcmu
import pprint
from scm import plams

j = os.path.join

res = tcmu.read(j(os.path.split(__file__)[0], "fixtures", "pEDA"))
# res = tcmu.read(j(os.path.split(__file__)[0], "fixtures", "BAND"))
# res = tcmu.read(j(os.path.split(__file__)[0], "fixtures", "ethane"))

# molecule:plams.Molecule = res.molecule.input
# print(molecule)

print(res.engine)

print("Band engine")
pprint.pprint(res.band)

print("Properties")
pprint.pprint(res.properties)

print("Status:", tcmu.quick_status(j(os.path.split(__file__)[0], "fixtures", "BAND_SAC_Pd_4NDG_Py")))

# print("Molecules")
# pprint.pprint(res.molecule)