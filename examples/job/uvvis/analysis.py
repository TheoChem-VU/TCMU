from tcutility import results
from scm.plams import KFReader
import pyfmo
import numpy as np


class EDAExcitation:
    def __init__(self, exc_idx=-1, wavelength=0, photon_energy=0, osc_strength=0):
        self.exc_idx = exc_idx
        self.wavelength = wavelength
        self.photon_energy = photon_energy * 27.2107  # Ha to eV
        self.osc_strength = osc_strength
        self.transitions = []

    def __str__(self):
        s = f'''Excitation({self.exc_idx}):
    λ   = {self.wavelength: .2f} nm
    h𝛎  = {self.photon_energy: .3f} eV
    f12 = {self.osc_strength: .4f} km/mol
    Transitions:
'''
        for ts in self.transitions:
            s += f'\t\t{ts}\n'
        return s

class EDAExcitations:
    def __init__(self, kffile: str, kffile_acc: str = None, acceptor_atom_indices: list[int] = None):
        self.res = results.adf._read_excitations(KFReader(kffile))
        self.orbs = pyfmo.orbitals2.objects.Orbitals(kffile)
        if kffile_acc:
            self.orbs_acc = pyfmo.orbitals2.objects.Orbitals(kffile_acc)
        else:
            self.orbs_acc = None
        self.acceptor_atom_indices = acceptor_atom_indices
        self._load()

    def _load(self):
        self.excitations = []
        acceptor_sfos = [sfo for sfo in self.orbs.sfos if sfo.fragment.lower() == 'acceptor']
        # print(acceptor_sfos)
        donor_sfos = [sfo for sfo in self.orbs.sfos if sfo not in acceptor_sfos]

        for exc_idx in range(self.res.A.SS.number_of_excitations):
            from_MO, to_MO = self.res.A.SS.from_MO[exc_idx], self.res.A.SS.to_MO[exc_idx]
            from_orbs = [self.orbs.mos[MO] for MO in from_MO]
            to_orbs = [self.orbs.mos[MO] for MO in to_MO]
            if self.res.A.SS.oscillator_strengths[exc_idx] < 1e-6:
                continue

            exc = EDAExcitation(exc_idx + 1, self.res.A.SS.wavelengths[exc_idx], self.res.A.SS.energies[exc_idx], self.res.A.SS.oscillator_strengths[exc_idx])
            # go through each pair of orbitals
            for i, (forb, torb) in enumerate(zip(from_orbs, to_orbs)):
                contr = self.res.A.SS.contributions[exc_idx][i]
                if contr < 0.1:
                    continue
                donor_coeffs = np.array([sfo.coefficient(forb) for sfo in donor_sfos])
                all_coeffs = np.array([sfo.coefficient(forb) for sfo in donor_sfos + acceptor_sfos])
                donor_character = sum(donor_coeffs**2) / sum(all_coeffs**2)

                if donor_character < 0.9:
                    continue

                acceptor_coeffs = np.array([sfo.coefficient(torb) for sfo in acceptor_sfos])
                all_coeffs = np.array([sfo.coefficient(torb) for sfo in donor_sfos + acceptor_sfos])
                acceptor_character = sum(acceptor_coeffs**2) / sum(all_coeffs**2)
                if acceptor_character < 0.9:
                    continue

                s = f'{i+1} ({contr: 6.1%}): {forb} ({donor_character: 6.1%}) ⎯► {torb} ({acceptor_character: 6.1%}), '
                if self.orbs_acc:
                    best_sfo = self.orbs_acc.mos.orbitals[np.argmax(abs(acceptor_coeffs))]

                    # check if torb of the sfos are unrestricted
                    if torb.spin in ['A', 'B'] and best_sfo.spin not in ['A', 'B']:
                        best_sfo = self.orbs_acc.mos.orbitals[np.argmax(abs(acceptor_coeffs))//2]

                    cbr_character = br_c_score(self.orbs_acc, best_sfo)
                    if abs(cbr_character) < 0.9:
                        continue
                    s += f'{cbr_character: 7.1%} C-Br, '
                s += f'𝚫ε = {abs(forb.energy - torb.energy): .2f} eV'
                exc.transitions.append(s)

            if len(exc.transitions) > 0:
                print(exc)


def br_c_score(orbs, mo):
    if orbs.sfos.unrestricted:
        br_4ps = [orbs.sfos[f'Br(3P:x_{mo.spin})_{mo.spin}'], orbs.sfos[f'Br(3P:y_{mo.spin})_{mo.spin}'], orbs.sfos[f'Br(3P:z_{mo.spin})_{mo.spin}']]
        c_2ps = [orbs.sfos[f'C(1P:x_{mo.spin})_{mo.spin}'], orbs.sfos[f'C(1P:y_{mo.spin})_{mo.spin}'], orbs.sfos[f'C(1P:z_{mo.spin})_{mo.spin}']]
    else:
        br_4ps = [orbs.sfos[f'Br(3P:x)'], orbs.sfos[f'Br(3P:y)'], orbs.sfos[f'Br(3P:z)']]
        c_2ps = [orbs.sfos[f'C(1P:x)'], orbs.sfos[f'C(1P:y)'], orbs.sfos[f'C(1P:z)']]
    
    shortest = float('inf')
    shortest_idx = None
    for i, ao in enumerate(c_2ps[0]):
        d = ao.molecule[1].distance_to(br_4ps[0].molecule[1])
        if d < shortest:
            shortest = d
            shortest_idx = i

    c_2ps = [c_2ps[0][shortest_idx], c_2ps[1][shortest_idx], c_2ps[2][shortest_idx]]
    br_4ps_c = np.array([sfo.coefficient(mo) for sfo in br_4ps])
    c_2ps_c = np.array([sfo.coefficient(mo) for sfo in c_2ps])

    bv = np.array(br_4ps[0].molecule[1].coords) - np.array(c_2ps[0].molecule[1].coords)
    bv = bv / np.linalg.norm(bv)
    br_4ps_c = br_4ps_c / np.linalg.norm(br_4ps_c)
    c_2ps_c = c_2ps_c / np.linalg.norm(c_2ps_c)

    bv_br = bv @ br_4ps_c
    bv_c = bv @ c_2ps_c
    return  bv_c * bv_br


if __name__ == '__main__':
    import tkinter as tk
    from tkinter import filedialog

    tk.Tk().withdraw()
    # kffile = filedialog.askopenfilename(title='Select complex adf.rkf file!')
    # kffile_acc = filedialog.askopenfilename(title='Select acceptor fragment adf.rkf file!')
    kffile = '/Users/yumanhordijk/Downloads/complex.adf.rkf'
    kffile_acc = '/Users/yumanhordijk/Downloads/singlepoint.adf.rkf'
    EDAExcitations(kffile, kffile_acc)
