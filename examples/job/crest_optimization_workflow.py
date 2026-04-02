from tcmu import WorkFlow
import os

# to create a WorkFlow we simply decorate a function with a WorkFlow object
@WorkFlow(delete_files=False)
def Conformers(molecule: str):
    # any imports that are needed in the workflow
    # need to be imported within the function
    from tcmu import CRESTJob, ADFJob, read
    from tcmu import workflow_status
    from pprint import pprint

    workflow_status.stage('Performing CREST calculation')
    # we first perform a CRESTJob calculation to
    # obtain the conformers of the molecule of interest
    with CRESTJob(use_slurm=False) as crest_job:
        crest_job.molecule(molecule)
        crest_job.name = 'crest'
        crest_job.md_temperature(500)
        crest_job.md_length('1.5x')
        crest_job.do_crossing(False)

    ret = {}
    conformers = crest_job.get_conformer_xyz(10)
    for i, xyz in enumerate(conformers):
        workflow_status.stage(f'Performing conformer optimization {i+1}/{len(conformers)}')
        # and reoptimize them using ADF
        with ADFJob(use_slurm=False) as adf_job:
            adf_job.molecule(xyz)
            adf_job.functional('OLYP')
            adf_job.basis_set('DZP')
            adf_job.name = f'optimization_{i+1}'
            adf_job.optimization()
            adf_job.vibrations(False)
            adf_job.settings.input.ams.properties.pespointcharacter = 'Yes'

        # load the results
        results = read(adf_job.workdir)
        # and store the energies and molecules
        ret[results.molecule.output] = results.properties.energy.bond

    return ret



@WorkFlow(delete_files=False)
def Example(num: int):
    import time
    time.sleep(3)
    print(f'Number is {num}')
    return num

for i in range(40): 
    Example(i, user_hash=f'Number ({i})')


for file_name in ['NaCl.xyz', 'water_dimer.xyz', 'butane.xyz', 'asc.xyz']:
    mol = Conformers(os.path.abspath(file_name), user_hash=file_name.removesuffix('.xyz'))
    print(mol)


