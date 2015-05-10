from pymol import cmd, plugins

class Residue(object):
    def __init__(self, model, segi, chain, resi, resn):

        self.model = model
        try:
            self.segi  = int(segi)
        except:
            self.segi  = None
        self.chain = chain
        self.resi  = int(resi)
        self.resn  = resn

    def selector(self):
        return "/{}/{}/{}/{}".format(
                self.model,
                self.segi or '',
                self.chain,
                self.resi)

    def __str__(self):
        return "{}({})".format(self.selector(), self.resn)

    def zoom_around(self, near = 5, zoom = 4):
        cmd.hide()
        sele = self.selector()

        tgt = '{} and ! name c+n+o+h'.format(sele)
        cmd.set_bond('stick_color', 'white', sele)
        cmd.set_bond('stick_radius', 0.14,  sele)
        cmd.set('sphere_scale', 0.25, sele)
        cmd.show('sticks', tgt)
        cmd.show('spheres', tgt)

        cmd.select('rz-target', sele)
        cmd.select('rz-around', 'byres {} around {}'.format(sele, near))
        cmd.deselect()

        cmd.show('(byres {} around {}) and ! name c+n+o+h'.format(sele, near))
        cmd.show('////HOH')

        cmd.show('ribbon', 'byres {} expand {}'.format(sele, near))
        cmd.orient(sele)
        cmd.zoom(sele, zoom)

class ResidueZoomer(object):
    residue_names = set([
        'ALA', 'ARG', 'ASN', 'ASP', 'CYS',
        'GLN', 'GLU', 'GLY', 'HIS', 'ILE',
        'LEU', 'LYS', 'MET', 'PHE', 'PRO',
        'SER', 'THR', 'TRP', 'TYR', 'VAL',
        'HOH'
        ])

    def __init__(self, sele, target = set([
        'HIS', 'ASN', 'GLN',
        'ASP', 'GLU',
        'LYS', 'ARG'])):

        self.target = target

        curi     = [0]
        residues = []

        def append_residue(model, segi, chain, resi, resn):
            resi = int(resi)
            if curi[0] != resi:
                curi[0] = resi
                residues.append(Residue(model, segi, chain, resi, resn))

        cmd.iterate(sele, 'append(model, segi, chain, resi, resn)',
                space = {'append': append_residue})

        self.residues = residues

    def __iter__(self):
        import itertools

        ts = type(self).residue_names - self.target
        return itertools.ifilter(lambda x: x.resn not in ts, self.residues)

import Tkinter

class ResidueZoomerGUI(Tkinter.Toplevel):
    def __init__(self, master = None):
        Tkinter.Toplevel.__init__(self, master)

        self.resizable(height = False, width = False)

        self.title('residue zoomer')

        fr = Tkinter.Frame(self)
        fr.pack(fill = Tkinter.X)

        def update(event):
            try:
                self.set_selector(sele.get())
            except:
                pass

        count = Tkinter.StringVar()
        sele = Tkinter.Entry(fr)
        sele.insert(0, 'all')
        sele.pack(side = Tkinter.LEFT, fill = Tkinter.BOTH, expand = 1)
        sele.bind('<Return>', update)

        btn = Tkinter.Button(fr, text = 'select')
        btn.pack(side = Tkinter.LEFT)
        btn.bind('<Button-1>', update)

        Tkinter.Label(fr, textvariable = count).pack(side = Tkinter.LEFT)

        self.count    = count
        self.listbox  = None
        self.residues = []

    def init_listbox(self):
        if self.listbox is not None: return

        frame = Tkinter.Frame(self)
        frame.pack(fill = Tkinter.BOTH, expand = 1)

        scroll = Tkinter.Scrollbar(frame, orient = Tkinter.VERTICAL)
        scroll.pack(side = Tkinter.RIGHT, fill = Tkinter.Y)

        lb = Tkinter.Listbox(frame, yscrollcommand = scroll.set)
        lb.pack(fill = Tkinter.BOTH, expand = 1)
        scroll.config(command = lb.yview)

        self.listbox = lb

        def selected(event):
            cs = lb.curselection()
            if cs:
                i = int(cs[0])
                self.residues[i].zoom_around()

        lb.bind('<<ListboxSelect>>', selected)


    def set_selector(self, sele):
        self.title(sele)
        residues = list(ResidueZoomer(sele))

        self.residues = residues
        length = len(residues)

        self.init_listbox()

        self.count.set(length)
        self.listbox.config(height = min(25, length))

        self.listbox.delete(0, Tkinter.END)
        for i, res in enumerate(residues):
            self.listbox.insert(i, res)

def __init_plugin__(self = None):
    root = plugins.get_tk_root()

    def residue_zoomer():
        ResidueZoomerGUI(root)

    plugins.addmenuitem('residue zoomer', residue_zoomer)
