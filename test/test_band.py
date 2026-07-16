import os

from tcmu.results.read import read, quick_status
from tcmu.results.result import Result
import pprint

j = os.path.join

res = read(j(os.path.split(__file__)[0], "fixtures", "pEDA"))
# res = read(j(os.path.split(__file__)[0], "fixtures", "ethane_adf"))

print("Band engine")
pprint.pprint(res.band)
print("Properties")
pprint.pprint(res.properties)
print("Status:", quick_status(j(os.path.split(__file__)[0], "fixtures", "BAND_SAC_Pd_4NDG_Py")))