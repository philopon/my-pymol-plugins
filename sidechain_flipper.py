from pymol import cmd

class Residue(object):
    def __init__(self, model, segi, chain, resi, resn):
        self.model = model
        try:
            self.segi = int(segi)
        except ValueError:
            self.segi = None
        self.chain = chain
        self.resi = int(resi)
        self.resn = resn

    def flip_by_atoms(self, atmA, atmB, atmC, atmD):
        sele = self.selector()

        a, b, c, d = map(lambda a: '{}/{}'.format(sele, a),
                [atmA, atmB, atmC, atmD])

        dh = cmd.get_dihedral(a, b, c, d)
        cmd.edit_mode(1)
        cmd.set_dihedral(a, b, c, d, dh + 180)
        cmd.edit_mode(0)

    def flip(self):
        if self.resn == 'GLN' or self.resn == 'GLU':
            self.flip_by_atoms('cb', 'cg', 'cd', 'oe1')
        elif self.resn == 'ASN' or self.resn == 'ASP':
            self.flip_by_atoms('ca', 'cb', 'cg', 'od1')
        elif self.resn == 'HIS':
            self.flip_by_atoms('ca', 'cb', 'cg', 'nd1')

    def selector(self):
        return '/{}/{}/{}/{}'.format(
                self.model, self.segi or '', self.chain, self.resi, self.resn)

def flip_sidechain(sele = '(all)'):
    curi     = [0]
    residues = []

    def append_residue(model, segi, chain, resi, resn):
        resi = int(resi)

        if curi[0] != resi:
            residues.append(Residue(model, segi, chain, resi, resn))
            curi[0] = resi

    cmd.iterate(sele, 'append(model, segi, chain, resi, resn)',
            space = {'append': append_residue})

    for res in residues:
        res.flip()

def __init_plugin__(self = None):
    cmd.extend('flip', flip_sidechain)
