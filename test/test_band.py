import os
from tcmu.results.read import read, quick_status
import pprint
from scm import plams

j = os.path.join

# res = read(j(os.path.split(__file__)[0], "fixtures", "pEDA"))
res = read(j(os.path.split(__file__)[0], "fixtures", "BAND"))
# res = read(j(os.path.split(__file__)[0], "fixtures", "ethane"))

# molecule:plams.Molecule = res.molecule.input
# print(molecule)

print(res.engine)

print("Band engine")
pprint.pprint(res.band)

print("Properties")
pprint.pprint(res.properties)

print("Status:", quick_status(j(os.path.split(__file__)[0], "fixtures", "BAND_SAC_Pd_4NDG_Py")))

print("Molecules")
pprint.pprint(res.molecule)