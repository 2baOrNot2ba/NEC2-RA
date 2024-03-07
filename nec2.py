from dataclasses import dataclass, astuple
import typing
import pathlib
import numpy as np
import PyNEC

PRGINPS = {'STGEOM', 'PCNTRL'}
CARDS_COMMT = {'CE', 'CM'}
CARDS_GEOMT = {'GA', 'GE', 'GF', 'GH', 'GM', 'GR', 'GS', 'GW', 'GX',
               'SP', 'SM'}
CARDS_CNTRL = {'CP', 'EK', 'EN', 'EX', 'FR', 'GD', 'GN', 'KH', 'LD',
               'NE', 'NH', 'NT', 'NX', 'PQ', 'PT', 'RP', 'TL', 'WG', 'XQ'}
CNTRL_COLS = [2,    5,    10,   15,   20,   30,   40,   50,   60, 70]
GEOMT_COLS = [2,    5,    10,   20,   30,   40,   50,   60,   70, 80]
PARLBLS = {'STGEOM': ['I1', 'I2', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'],
           'PCNTRL': ['I1', 'I2', 'I3', 'I4', 'F1', 'F2', 'F3', 'F4', 'F5',
                      'F6']}
CARDDEFS = {
    'CM': {'PRGINP': 'COMMNT'},
    'CE': {'PRGINP': 'COMMNT'},

    'GA': {'PRGINP': 'STGEOM', 
           'I1': 'ITG', 'I2': 'NS',
           'F1': 'RADA', 'F2': 'ANG1', 'F3': 'ANG2', 'F4': 'RAD'},
    'GE': {'PRGINP': 'STGEOM',
           'I1': 'GPFLAG'},
    'GH': {'PRGINP': 'STGEOM',
           'I1': 'ITG', 'I2': 'NS', 'F1': 'S', 'F2': 'HL', 'F3': 'A1',
           'F4': 'B1', 'F5': 'A2', 'F6': 'B2', 'F7': 'RAD'},
    'GM': {'PRGINP': 'STGEOM',
           'I1': 'ITGI', 'I2': 'NRPT', 'F1': 'ROX', 'F2': 'ROY', 'F3': 'ROZ',
           'F4': 'XS', 'F5': 'YS', 'F6': 'ZS', 'F7': 'ITS'},
    'GW': {'PRGINP': 'STGEOM',
           'I1': 'ITG', 'I2':  'NS', 'F1': 'XW1', 'F2': 'YW1',
           'F3': 'ZW1', 'F4': 'XW2', 'F5': 'YW2', 'F6': 'ZW2',
           'F7': 'RAD'},

    'CP': {'PRGINP': 'PCNTRL',
           'I1': 'TAG1', 'I2': 'SEG1', 'I3': 'TAG2', 'I4': 'SEG2'},
    'EK': {'PRGINP': 'PCNTRL',
           'I1': 'ITMP1'},
    'EN': {'PRGINP': 'PCNTRL'},
    'EX': {'PRGINP': 'PCNTRL',
           'I1': 'I1', 'I2': 'I2', 'I3': 'I3', 'I4': 'I4',
           'F1': 'F1', 'F2': 'F2', 'F3': 'F3',
           'F4': 'F4', 'F5': 'F5', 'F6': 'F6'},       
    'FR': {'PRGINP': 'PCNTRL',
           'I1': 'IFRQ', 'I2': 'NFRQ', 'F1': 'FMHZ', 'F2': 'DELFRQ'},
    'GD': {'PRGINP': 'PCNTRL',
           'F1': 'EPSR2', 'F2': 'SIG2', 'F3': 'CLT', 'F4': 'CHT'},
    'GN': {'PRGINP': 'PCNTRL',
           'I1': 'IPERF', 'I2': 'NRADL', 'F1': 'EPSE', 'F2': 'SIG',
           'F3': 'F3', 'F4': 'F4', 'F5': 'F5'},
    'KH': {'PRGINP': 'PCNTRL',
           'F1': 'RKH'},
    'LD': {'PRGINP': 'PCNTRL',
           'I1': 'LDTYP', 'I2': 'LDTAG', 'I3': 'LDTAGF', 'I4': 'LDTAGT',
           'F1': 'ZLR', 'F2': 'ZLI', 'F3': 'ZLC'},
    'NE': {'PRGINP': 'PCNTRL',
           'I1': 'NEAR', 'I2': 'NRX', 'I3': 'NRY', 'I4': 'NRZ',
           'F1': 'XNR', 'F2': 'YNR', 'F3': 'ZNR',
           'F4': 'DXNR', 'F5': 'DYNR', 'F6': 'DZNR'},
    'NH': {'PRGINP': 'PCNTRL',
           'I1': 'NEAR', 'I2': 'NRX', 'I3': 'NRY', 'I4': 'NRZ',
           'F1': 'XNR', 'F2': 'YNR', 'F3': 'ZNR',
           'F4': 'DXNR', 'F5': 'DYNR', 'F6': 'DZNR'},
    'RP': {'PRGINP': 'PCNTRL',
           'I1': 'I1', 'I2': 'NTH', 'I3': 'NPH', 'I4': 'XNDA',
           'F1': 'THETS', 'F2': 'PHIS', 'F3': 'DTH', 'F4': 'DPH',
           'F5': 'RFLD', 'F6': 'GNOR'},
    'PQ': {'PRGINP': 'PCNTRL',
           'I1': 'IPTFLQ', 'I2': 'IPTAQ', 'I3': 'IPTAQF', 'I4': 'IPTAQT'},
    'XQ': {'PRGINP': 'PCNTRL',
           'I1': 'I1'}
}


class Deck:
    """
    NEC deck of cards
    """
    def __init__(self, cardlist=None) -> None:
        self.carddeck = []
        if cardlist is not None:
            self.carddeck = cardlist

    def append_card(self, *cardargs):
        self.carddeck.append(cardargs)
    
    def append_cards(self, cardslist):
        self.carddeck.extend(cardslist)
    
    def get_sections(self):
        commt_cards = [_c for _c in self.carddeck if _c[0] in CARDS_COMMT]
        geomt_cards = [_c for _c in self.carddeck if _c[0] in CARDS_GEOMT]
        cntrl_cards = [_c for _c in self.carddeck if _c[0] in CARDS_CNTRL]
        return commt_cards, geomt_cards, cntrl_cards
    
    @classmethod
    def load_necfile_cls(cls, file, cardformat='COLUMNS'):
        deck =  cls()
        for cardstr in file.readlines():
            cardargs = cls._cardstr2args(cardstr, cardformat)
            deck.append_card(*cardargs)

    def load_necfile(self, file, cardformat='COLUMNS'):
        self.__init__()
        for cardstr in file.readlines():
            cardargs = self.__class__._cardstr2args(cardstr, cardformat)
            self.append_card(*cardargs)
        return self
    
    def save_necfile(self, file):
        necfile_suffix = '.nec'
        if type(file) == str:
            _suff = pathlib.Path(file).suffix
            if _suff:
                if _suff != necfile_suffix:
                    file = file.replace(_suff, necfile_suffix)
            else:
                file = file + necfile_suffix
            f = open(file, 'w')
        else:
            f = file
        f.write(str(self))
        f.close()
    
    def as_pynec(self):
        pynec_code_list = []
        _code_section = []
        # Set up PyNEC module and context and geometry
        _code_section.append("import PyNEC")
        _code_section.append("_nec_context = PyNEC.nec_context()")
        _code_section.append("_nec_geom = _nec_context.get_geometry()")
        for card in self.carddeck:
            mn_id = card[0]
            parms = card[1:]
            if mn_id in CARDS_COMMT: continue
            if mn_id in CARDS_GEOMT:
                _arg = parms + (1.0, 1.0)
                if mn_id == 'GM':
                    parms = (parms[2], parms[3], parms[4],
                             parms[5], parms[6], parms[7],
                             parms[8], parms[1], parms[0])
                    _code_section.append(f"_nec_geom.move{parms}")
                if mn_id == 'GW':
                    _code_section.append(f"_nec_geom.wire{_arg}")
                if mn_id == 'GE':
                    _code_section.append(
                        f"_nec_context.geometry_complete{parms}")
            if mn_id in CARDS_CNTRL:
                if mn_id == 'EX':
                    itmp3, itmp4 = self._split_digits(parms[3], 2)
                    _arg = (parms[:3]+(itmp3, itmp4)+parms[4:])
                    _code_section.append(f"_nec_context.ex_card{_arg}")
                if mn_id == 'EN':
                    pass
                if mn_id == 'FR':
                    _code_section.append(f"_nec_context.fr_card{parms}")
                if mn_id == 'RP':
                    X, N, D, A = self._split_digits(parms[3], 4)
                    _arg = parms[:3]+(X, N, D, A)+parms[4:]
                    _code_section.append(f"_nec_context.rp_card{_arg}")
                    pynec_code_list.append(_code_section)
                    _code_section = []
                if mn_id == 'XQ':
                    _code_section.append("_nec_context.xq_card(0)")
                    pynec_code_list.append(_code_section)
                    _code_section = []
        if len(pynec_code_list) == 0:
            pynec_code_list.append(_code_section)
        # Chop up cards into sections that end with executions
        pynec_code_strs = []
        for _code_section in pynec_code_list:
            pynec_code_strs.append("\n".join(_code_section))

        return pynec_code_strs
    
    def exec_pynec(self, printout=False):
        _locals = {}
        _code = self.as_pynec()
        _nrblcks = len(_code)
        _blcknr = 0
        for _blck in _code:
            _blcknr += 1
            if printout:
                print(f'**** Executing code block {_blcknr}/{_nrblcks}:')
                print(_blck)
            exec(_blck, None, _locals)
            if printout:
                print('**** Finished code block.')
            _nec_context_ = _locals['_nec_context']
            yield _nec_context_
        exec('del _nec_context', None, _locals)

    @classmethod
    def _cardstr2args(cls, cardstr, cardformat='COLUMNS'):

        def split_cols(l, pnames, lbls):
            cardparms = []
            for lbl in lbls:
                nrcols, ntype = cls._parmcolwidth(lbl)
                colstr = l[:nrcols]
                parmtoadd = None
                if lbl in pnames and colstr:
                    try:
                        parmtoadd = ntype(colstr)
                    except ValueError:
                        raise ValueError(
                                f'Card {mn_id}, param {lbl} is corrupt')
                if parmtoadd is not None:
                    cardparms.append(parmtoadd)
                l = l[nrcols:]
            return tuple(cardparms)
        
        def split_csv(l, pnames, lbls):
            cardparms = []
            pnames = list(pnames)
            _parms = l.split()
            lbl2parm = dict(zip(lbls, _parms))
            for lbl in lbl2parm:
                if lbl in pnames:
                    _, ntype = cls._parmcolwidth(lbl)
                    cardparms.append(ntype(lbl2parm[lbl]))
            return tuple(cardparms)
        
        l = cardstr.rstrip()
        card = []
        mn_id = l[:2]
        l = l[2:]
        if mn_id not in CARDDEFS.keys():
            raise ValueError(f"Memnonic id {mn_id} not valid")
        card.append(mn_id)
        if mn_id == 'CM' or mn_id == 'CE':
            card.append(l)
            return tuple(card)
        lbls = PARLBLS[CARDDEFS[mn_id]['PRGINP']]
        pnames = list(filter(lambda _pn : _pn in lbls, CARDDEFS[mn_id]))
        if cardformat == 'COLUMNS':
            card = (mn_id, *split_cols(l, pnames, lbls))
        else:
            card = (mn_id, *split_csv(l, pnames, lbls))
        return card
    
    def _split_digits(self, int_int, nrdigits):
        int_str = f"{int_int :0{nrdigits}d}"
        intcharlist = [*int_str]
        int_list = [int(d) for d in intcharlist]
        return tuple(int_list)
    
    @staticmethod
    def _parmcolwidth(parmlbl):
        numtyp = parmlbl[0]
        if numtyp == 'I':
            ntype = int
            nrcols = 5
            if parmlbl[1] == '1':
                nrcols = 3
        elif numtyp == 'F':
            ntype = float
            nrcols = 10
        return nrcols, ntype
    
    def __iter__(self):
        for card in self.carddeck:
            yield card
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False
        return self.carddeck == other.carddeck
    
    def __ne__(self, other):
        if not isinstance(other, self.__class__): return True
        return self.carddeck == other.carddeck

    def __str__(self):
        lines = []
        #lines += [f'CM *** Created using {__name__}.{__class__.__name__} ***']
        for card in self.carddeck:
            card = list(card)
            mn_id = card.pop(0)
            if mn_id == 'CM' or mn_id == 'CE':
                line = mn_id + card.pop(0)
                lines.append(line)
                continue
            lbls = PARLBLS[CARDDEFS[mn_id]['PRGINP']]
            pnames = list(filter(lambda _pn : _pn in lbls, CARDDEFS[mn_id]))
            line = mn_id  # Initialize output line
            for lbl in lbls:
                nrcols, ntype = __class__._parmcolwidth(lbl)
                nfmt = 'd' if ntype is int else 'g'
                if lbl in pnames:
                    parm = ntype(card.pop(0))
                else:
                    parm = ntype(0)
                parmstr = f"{parm:>{nrcols}{nfmt}}"
                line += parmstr
            lines.append(line)
        _str = '\n'.join(lines) + '\n'
        return _str
    
    def __repr__(self) -> str:
        repr_ = self.__class__.__name__+'('+ repr(self.carddeck)+")"
        return repr_


@dataclass
class VoltageSource:
    amplitude: complex = 1+0j
    type: str = 'applied-E-field'  # or 'current-slope-discontinuity'

    def nec_type(self):
        ex_i1 = 0 if self.type == 'applied-E-field' else 1
        return ex_i1


@dataclass
class Port:
    fractional_position: float = 0.5
    name: str = '' # new
    source: VoltageSource = VoltageSource()


@dataclass
class Wire:
    point_src: typing.Tuple
    point_dst: typing.Tuple
    thickness: float
    nr_seg: int = 0
    port: Port = None

    def parametric_seg(self, fractional_position):
        seg_nr = int(fractional_position * self.nr_seg)+1
        return seg_nr
    
    def add_port(self, fraction_position, port_name='', source=None):
        self.port = Port(fraction_position, port_name, source)
        return self
    
    def length(self):
        _length = np.linalg.norm(np.array(self.point_dst)
                                 - np.array(self.point_src))
        return _length


@dataclass
class Transformations:
    rox: float
    roy: float
    roz: float
    xs: float
    ys: float
    zs: float
    nrpt: int = 0
    itgi: int = 0
    its: int = 0


@dataclass
class FreqSteps:
    steptype: str = 'lin'  # linear or 'log' multiplicative
    nrsteps: int = 1
    start: float = 299.8  # MHz
    incr: float = 1.

    def max_freq(self):
        _max_freq = (self.start+self.incr*(self.nrsteps-1)
                     if self.steptype == 'lin'
                     else self.start*self.incr**(self.nrsteps-1))
        return _max_freq
    
    def to_nec_type(self):
        if self.steptype == 'lin':
            return 0
        elif self.steptype == 'log':
            return 1
    
    def from_nec_type(self):
        pass


@dataclass
class RadPatternSpec:
    calcmode: int = 0   # 0: normal-mode, 1: surface-wave, 2: linear-cliff
                        # 3: circular-cliff, 4: radial-ground-screen
                        # 5: rad-grd-scr-lin-clff, 6: rad-grd-scr-crc-clff
    nth: int = 1
    nph: int = 1
    xnda: int = 1000    # f"{X}{N}{D}{A}" where:
                        # X=0 major & minor axis, =1 vertical, horizontal
                        # N=0 no normalized gain
                        # D=
                        # A=0 no averaging, 
    thets: float = 0.
    phis: float = 0.
    dth: float = 0.
    dph: float = 0.
    rfdl: float = 0.    # Radial distance, =0 factor exp(-jkr)/r dropped
    gnor: float = 0.    # Gain normalization factor see N

    def hemisphere(self, nth=40, nph=10):
        self.nth = nth
        self.nph = nph
        self.dth = int(90/nth)
        self.dph = int(360/nph)
        return self

@dataclass
class Ground:
    iperf: int
    nradl: int
    epse: float
    sig: float
    f3: float = 0.
    f4: float = 0.
    f5: float = 0.

    def astuple(self):
        return (self.iperf, self.nradl, 0, 0, self.epse, self.sig,
                self.f3, self.f4, self.f5)


@dataclass
class ExecutionBlock:
    freqsteps: FreqSteps = FreqSteps()  # Should at least have this
    exciteports: typing.List = None
    radpat: RadPatternSpec = None


class TaggedGroup:

    def __init__(self):
        self.parts = {}
        self._tag_nr = 0
        self._group_id = ''     # Should match one of StructureModel dict
                                # attribute groups keys.
    
    @classmethod
    def _uniq_name(cls, basename, namesdict):
        genericnames = [gn for gn in namesdict if gn.startswith(basename)]
        idx = 0
        while True:
            name = basename+str(idx)
            if name not in genericnames: break
            idx +=1
        name = basename+str(idx)
        return name

    def make_wire(self, point_src, point_dst, thickness, name='', nr_seg=None):
        wire = Wire(point_src, point_dst, thickness, nr_seg)
        if not name:
            name = self._uniq_name('_part_', self.parts)
        self.parts[name] = wire
        return self
    
    def make_transformation(self, rox, roy, roz, xs, ys, zs, nrpt,
                            itgi=0, its=0):
        pass

    def get_ports(self, port_name=None):
        __ports = {}
        for _partid in self.parts:
             __port = self.parts[_partid].port
             if __port:
                 __ports[__port.name] = __port
        if port_name is None:
            return __ports
        else:
            return __ports[port_name]

    def _port_part(self, port_name):
        for __partid in self.parts:
            if port_name == self.parts[__partid].port.name:
                return __partid
        raise KeyError(f"Port '{port_name}' does not exist")

    def _assign_port_segs(self):
        """Assign Port Segments

        Go through all ports in this group, find the segment to attach to and
        assign that segment to be the segment that gets excited together with
        the attributes of the ports attribute.
        """
        for portid in self.get_ports():
            fp = self.get_ports(portid).fractional_position
            partid = self._port_part(portid)
            prmtrc_seg_in_part = self.parts[partid].parametric_seg(fp)
            # Calculate segment offset within group
            offset_seg = 0
            for pid in self.parts:
                if pid == partid: break
                offset_seg += self.parts[pid].nr_seg
            self.get_ports(portid).ex_seg = offset_seg + prmtrc_seg_in_part

    def part_lengths(self):
        lengths = {}
        for pid in self:
            part = self.parts[pid]
            lengths[pid] = part.length()
        return lengths
    
    def total_length(self):
        return np.sum(list(self.part_lengths().values()))

    def get_nrsegments(self):
        return np.sum([self.parts[p].nr_seg for p in self.parts])

    def __iter__(self):
        for pid in self.parts:
            yield pid
        
    def __getitem__(self, part_name):
        return self.parts[part_name]
    
    def __setitem__(self, part_name, taggable):
        if type(taggable) == Wire:
            self.parts[part_name] = taggable
        elif type(taggable) == Transformations:
            pass
        elif type(taggable) == Port:
            raise DeprecationWarning('Setting port to part is discouraged')
            # Check that this group has the desired part
            if not self.parts.get(part_name):
                raise KeyError(
                    f"TaggedGroup '{self._group_id}' has no part '{part_name}'")
            if not taggable.name:
                taggable.name = self._uniq_name('_port_', self.get_ports())
            self.parts[part_name].port = taggable


class StructureModel:

    def __init__(self, name='Model_'):
        self.name = name
        self.groups = {}
        self.executionblocks = {}
        self.element = []  # List of group names that make up element
        self.arr_delta_pos = [[]]
        self.elements_tags = [[]]  # Map element nr to its tags 
        self.excited_elements = []
        self.comments = []
        self.ground = None
        self._last_tag_nr = 0
    
    def set_commentline(self, comment):
        self.comments.append(comment)

    def set_ground(self, grnd=Ground(1, 0, 0, 0)):
        self.ground = grnd    

    def _assign_tags_base(self):
        """\
        Assign sequential tag nrs to base groups and set up element tags
        """
        last_tag_nr = self._last_tag_nr
        # Set tags for non element groups
        nonelemgrps = set(self.groups)-set(self.element)
        inc = 1
        for last_tag_nr, gid in enumerate(nonelemgrps, start=last_tag_nr+inc):
            self.groups[gid]._tag_nr = last_tag_nr
        self._last_tag_nr = last_tag_nr

    def _assign_tags_elem(self):
        """\
        Assign sequential tag nrs to array elements and set up element tags
        """        
        # Set tags for element group
        last_tag_nr = self._last_tag_nr
        inc = 10**len(str(last_tag_nr))
        #inc = 1  # REMOVE this test 
        elem_tags_start = last_tag_nr+inc
        for last_tag_nr, gid in enumerate(self.element, start=last_tag_nr+inc):
            self.groups[gid]._tag_nr = last_tag_nr
        self.elements_tags[0] = list(range(elem_tags_start, last_tag_nr+1))
        self._last_tag_nr = last_tag_nr
        nr_elem_tags = len(self.elements_tags[0])
        for elem_nr in range(1, len(self.arr_delta_pos)):
            elem_tags_start += nr_elem_tags
            _ = range(elem_tags_start, elem_tags_start + nr_elem_tags)
            self.elements_tags.append(list(_))

    def nrsegs_hints(self, min_seg_perlambda, max_frequency):
        nrsegs = {}
        max_frequency = max_frequency * 1e6
        _min_lambda = 3e8/max_frequency
        for gid in self.groups:
            plens = self.groups[gid].part_lengths()
            for pid in plens:
                p_lenlambda = plens[pid]/_min_lambda
                nrsegs[(gid,pid)] = round(p_lenlambda*min_seg_perlambda)
        return nrsegs
    
    def segmentalize(self, min_seg_perlambda, max_frequency):
        if min_seg_perlambda is None:
            min_seg_perlambda = 10
        max_nrseg = self.nrsegs_hints(min_seg_perlambda, max_frequency)
        for gid, pid in max_nrseg:
            self.groups[gid].parts[pid].nr_seg = max_nrseg[(gid, pid)]
        self._assign_tags_base()
        return max_nrseg
    
    def _port_group(self, port_name):
        for gid in self.groups:
            if port_name in self.groups[gid].get_ports():
                return gid
        raise KeyError(f"Port '{port_name}' does not exist")

    def reset_port_srcs(self):
        """Remove all port excitations"""
        for base_gid in self.groups:
            _ports = self.groups[base_gid].get_ports()
            for _port in _ports:
                _pp = self.groups[base_gid]._port_part(_port)
                self.groups[base_gid][_pp].source = None

    def excite_port(self, port_id, voltage_src):
        """Attach a voltage source to port"""
        elem_nr = None
        if type(port_id) == str:
            port_name = port_id
        elif type(port_id) == tuple:
            elem_nr, port_name = port_id
        else:
            raise KeyError(f"Port '{port_id}' does not exist")
        base_gid = self._port_group(port_name)
        self.groups[base_gid].get_ports(port_name).source = voltage_src
        if elem_nr is not None:
            self.excited_elements.append(port_id)
    
    def add_executionblock(self, name, executionblock , reset=False):
        if reset:
            self.executionblocks = {}
        self.executionblocks[name] = executionblock

    def arrayify(self, element, array_positions):
        self.element = element
        self.arr_delta_pos = []
        pos_from = [0., 0., 0.]
        for pos_to in array_positions:
            delta_pos = [pos_to[idx]-pos_from[idx] for idx in range(3)] 
            self.arr_delta_pos.append(delta_pos)
            pos_from = pos_to
        self._assign_tags_elem()

    def as_neccards(self):

        d = Deck()

        def create_geom_for_groups(subgroup_ids):
            nonlocal d
            subgroups = {gid: self.groups[gid] for gid in subgroup_ids}
            for gid in subgroups:
                for pid in subgroups[gid]:
                    tag_nr = subgroups[gid]._tag_nr
                    a_part = subgroups[gid].parts[pid]
                    nr_seg = a_part.nr_seg
                    if type(a_part) == Wire:
                        d.append_card('GW', tag_nr, nr_seg,
                                *a_part.point_src, *a_part.point_dst,
                                a_part.thickness)
        
        def create_excite_for_groups(subgroup_ids):
            nonlocal d
            subgroups = {gid: self.groups[gid] for gid in subgroup_ids}
            for gid in subgroups:
                tag_nr = subgroups[gid]._tag_nr
                subgroups[gid]._assign_port_segs()
                for portid in subgroups[gid].get_ports():
                    port = subgroups[gid].get_ports(portid)
                    if not port.source: continue
                    ex_seg = port.ex_seg
                    ex_type = port.source.nec_type()
                    if ex_type == 0:
                        I2, I3 = tag_nr, ex_seg
                        print_max_rel_admittance_mat = 0
                        print_inp_imp = 1
                        I4 = int(
                            f"{print_max_rel_admittance_mat}{print_inp_imp}")
                    voltage =  port.source.amplitude
                    if ex_type == 0:
                        F1, F2 = voltage.real, voltage.imag
                    d.append_card('EX', ex_type, I2, I3, I4,
                                  F1, F2, 0., 0., 0., 0.)
        
        def create_excite_for_elements(elem_ex_ports):
            nonlocal d
            for egname in self.element:
                self.groups[egname]._assign_port_segs()
            for _portid, __vs in elem_ex_ports:
                eid, pnm = _portid
                gid = self._port_group(pnm)
                element_tag = self.elements_tags[eid][self.element.index(gid)]
                port = self.groups[gid].get_ports(pnm)
                if not port.source: continue
                ex_seg = port.ex_seg
                ex_type = port.source.nec_type()
                if ex_type == 0:
                    I2, I3 = element_tag, ex_seg
                    print_max_rel_admittance_mat = 0
                    print_inp_imp = 1
                    I4 = int(
                        f"{print_max_rel_admittance_mat}{print_inp_imp}")
                voltage =  port.source.amplitude
                if ex_type == 0:
                    F1, F2 = voltage.real, voltage.imag
                d.append_card('EX', ex_type, I2, I3, I4,
                                F1, F2, 0., 0., 0., 0.)
        
        def _create_array():
            nonlocal d
            # Move 1st (base) element into pos0 (no tag increment)
            elem_tags_start = self.elements_tags[0][0]
            pos0 = self.arr_delta_pos[0]
            d.append_card('GM', 0, 0, 0., 0., 0.,
                          pos0[0], pos0[1], pos0[2], elem_tags_start)
            # Copy last element and move by delta_pos 
            #  (increment by nr of tags in base element after each move)
            nr_elem_tags = len(self.elements_tags[0])
            for dpos in self.arr_delta_pos[1:]:
                d.append_card('GM', nr_elem_tags, 1, 0., 0., 0.,
                              dpos[0], dpos[1], dpos[2], elem_tags_start)
                elem_tags_start += nr_elem_tags

        # Comments
        for comment in self.comments:
            d.append_card('CM', ' '+comment)
        d.append_card('CE', '')
        nonelemgrp = set(self.groups)-set(self.element)

        # Structure Geometry for non element groups
        create_geom_for_groups(nonelemgrp)
        # Structure Geometry for element groups
        # # Create initial group to move
        create_geom_for_groups(self.element)
        if self.element:
            # Make array of element
            _create_array()
        # End Geometry
        d.append_card('GE', 0)

        # Program Control (loop over self.executionblocks)
        for _exblk in self.executionblocks.values():
            _freqsteps = _exblk.freqsteps
            _exciteports = _exblk.exciteports
            _radpat = _exblk.radpat

            if _freqsteps:
            # Frequency
                I1, I2 = _freqsteps.to_nec_type(), _freqsteps.nrsteps
                F1, F2 = _freqsteps.start, _freqsteps.incr
                d.append_card('FR', I1, I2, F1, F2)

            # Excitations
            _nonelem_ex_ports = []
            _elem_ex_ports = []
            self.reset_port_srcs()
            for ep in _exciteports:
                self.excite_port(*ep)
                if type(ep[0]) == str:
                    _nonelem_ex_ports.append(ep)
                elif type(ep[0]) == tuple:
                    _elem_ex_ports.append(ep)

            # ... non element group
            create_excite_for_groups(nonelemgrp)
            # ... element group
            create_excite_for_elements(_elem_ex_ports)

            # Cards that trigger execution of NEC2 engine 
            if _radpat:
                d.append_card('RP', *astuple(_radpat))
            else:
                d.append_card('XQ', 0)
        
        # END
        d.append_card('EN', 0)
        return d

    def __getitem__(self, group_id):
        if type(group_id) == str:
            if group_id not in self.groups:
                # New group
                if not group_id:
                    group_id = TaggedGroup._uniq_name('_group_', self.groups)
                tg = TaggedGroup()
                tg._group_id = group_id
                self.groups[group_id] = tg
            else:
                tg = self.groups[group_id]
        elif type(group_id) == tuple:
            tg = self.groups[group_id[1]]
        return tg
    
    def __setitem__(self, group_id, tag_group):
        tag_group._group_id = group_id
        self.groups[group_id] = tag_group

    def __iter__(self):
        for gid in self.groups:
            for pid in self.groups[gid].parts:
                yield gid, pid

    def __str__(self):
        indent = '    '
        out = ["Model: "+self.name]
        for g in self.groups:
            out.append(indent+'group: '+ str(g))
            _gs = self.groups[g]
            for p in _gs.parts:
                out.append(2*indent+"part: "+str(_gs.parts[p]))
        return '\n'.join(out)

#----

class Nec2Out:
    def __init__(self) -> None:
        pass

    @classmethod
    def load_nec(cls):
        return cls()


def load(filename, cardformat='CSV'):
    with open(filename) as file:
        deck = Deck()
        deck.load_necfile(file, cardformat)
    return deck
