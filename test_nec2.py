import sys
from io import StringIO
import numpy as np
import matplotlib.pyplot as plt
from nec2 import (ArrayModel, StructureModel, Deck, Wire, VoltageSource,
                  FreqSteps, ExecutionBlock, RadPatternSpec)


def test_Deck():
    """\
    Test: create a Deck object which represents a wire excited

    Examples
    --------
    >>> test_Deck()
    True
    """
    print("SYS", sys.path)
    d = Deck()
    d.append_card('GW', 0, 7, 0., 0., -.25, 0., 0., .25, 1.0E-5)
    d.append_card('GE', 0)
    d.append_card('EX', 0, 0, 4, 0, 1.0)
    d.append_card('EN')
    d2 = Deck([('GW', 0, 7, 0.0, 0.0, -0.25, 0.0, 0.0, 0.25, 1e-05),
               ('GE', 0),
               ('EX', 0, 0, 4, 0, 1.0),
               ('EN',)])
    print(d==d2)


def test_Deck_load_necfile():
    """
    Test: load in a Deck object from a .nec file

    Examples
    --------
    >>> test_Deck_load_necfile()

    """
    test_necin = \
"""\
CM TESTEX1
CE EXAMPLE 1. CENTER FED LINEAR ANTENNA
CE345678901234567890123456789012345678901234567890123456789012345678901234567890
GW  0    7       0.0        0.      -.25        0.        0.       .25      .001
GE  0
FR  0    2    0    0       50.        2.
EX  0    0    4    0        1.        0.        0.        0.        0.        0.
XQ  0
LD  0    0    4    4       10. 3.000E-09 5.300E-11
PQ  0    0    0    0
NE  0    1    1   15      .001        0.        0.        0.        0.    .01786
EN
"""
    d = Deck()
    d.load_necfile(StringIO(test_necin), 'COLUMNS')
    print(d)
    return d


def test_Deck_exec_pynec():
    """\
    Test: create Deck and then execute it using pynec
    """
    d = test_Deck_load_necfile()
    cntxt = next(d.exec_pynec())
    for f in range(2):
        inp_parms = cntxt.get_input_parameters(f)
        print(inp_parms.get_impedance())


def test_StructureModel():
    p1 = (+0.5, 0., 0.1)
    p2 = (+0.5, 0., 0.9)
    p3 = (-0.5, 0., 0.9)
    p4 = (-0.5, 0., 0.1)
    l12 = (p1, p2)
    l23 = (p2, p3)
    l34 = (p3, p4)
    wire_rad = 0.001
    model = StructureModel('Big_Xing')
    model['xing']['X+'] = Wire(*l12, wire_rad)
    model['xing']['mid'] = Wire(*l23, wire_rad)
    model['xing']['X-'] = Wire(*l34, wire_rad)
    model['xing']['mid'].add_port(0.5, 'VS', VoltageSource(1.0))
    fs = FreqSteps('lin', 3, 100., 10.)
    rps = RadPatternSpec()
    ex_ports = [('VS', VoltageSource(1.0))]
    eb = ExecutionBlock(fs, ex_ports, rps)
    model.segmentalize(15, fs.max_freq())
    model.add_executionblock('exblk', eb)
    d = model.as_neccards()
    cntxt = next(d.exec_pynec())
    for f in range(len(fs.aslist())):
        inp_parms = cntxt.get_input_parameters(f)
        for pnr, portname in enumerate(ex_ports):
            print(portname, inp_parms.get_impedance()[pnr])


def test_ArrayModel_offcenter():
    lamhalf = 1.0
    w_radii = 1e-5*2*lamhalf
    dip_len = lamhalf
    p1 = (-dip_len/2, 0., 0.)
    p2 = (+dip_len/2, 0., 0.)
    l12 = (p1, p2)
    offcnt = ArrayModel('Off_Center')
    offcnt['dip']['Z'] = Wire(*l12, w_radii).add_port(0.5,'VS')
    fs = FreqSteps('lin', 1, 3e8/(10*2*lamhalf)/1e6)  # MHz
    offcnt.segmentalize(65, fs.max_freq())
    ex_port = ('VS', VoltageSource(1.0))
    rps = RadPatternSpec(nth=3, dth=10., nph=2*2, phis=90.0, dph=45.)
    arr_pos = [[10., 21., 15.]]
    offcnt.arrayify(element=['dip'], array_positions=arr_pos)
    eb = ExecutionBlock(fs, ex_port, rps)
    eepdat = offcnt.calc_eeps(eb, save_necfile=True)
    sv = offcnt.calc_steering_vector(eb)
    ant_nr = 0
    frq_nr = 0
    print('Steeing vector phases:')
    ref_ampphs0 = np.conj(sv[ant_nr, frq_nr,0,0])
    print(np.angle(sv[ant_nr, frq_nr]*ref_ampphs0, deg=True))
    ref_ampphs = np.conj(eepdat.eeps[ant_nr].ef_phi[frq_nr][0,0])
    _relangs = np.angle(eepdat.eeps[ant_nr].ef_phi[frq_nr]*ref_ampphs, deg=True)
    print('Field phase rel. theta=0.')
    print(_relangs)


def test_Array_2_lamhalfdip_sbys():
    """
    Test of two lambda/2 dipole side-by-side array

    See Balanis Antenna Theory 2016, Fig 8.21
    """
    lamhalf = 1.0
    w_radii = 1e-5*2*lamhalf
    dip_len = lamhalf
    p1 = (0., 0., -dip_len/2)
    p2 = (0., 0., +dip_len/2)
    l12 = (p1, p2)
    twodip = ArrayModel('2dip_sbs')
    twodip['dip']['Z'] = Wire(*l12, w_radii).add_port(0.5,'VS')
    fs = FreqSteps('lin', 1, 3e8/(2*lamhalf)/1e6)  # MHz
    print("Freq", fs.start, 'MHz')
    # rps = None  # RadPatternSpec()
    twodip.segmentalize(65, fs.max_freq())
    ex_port = ('VS', VoltageSource(1.0))
    dists = 2*lamhalf * np.linspace(0.0, 3., 50)[1:]
    mutimp = []
    for dist in dists:
        arr_pos = [[0.,0.,0.], [dist, 0., 0.]]
        twodip.arrayify(element=['dip'],
                        array_positions=arr_pos)
        eepdat = twodip.calc_eeps(ExecutionBlock(fs, ex_port))
        impmat = eepdat.get_impedances()
        mutimp.append(impmat[0,0,1])
    mutimp = np.array(mutimp)
    plt.plot(dists/(2*lamhalf), np.real(mutimp))
    plt.plot(dists/(2*lamhalf), np.imag(mutimp))
    plt.legend(['Resistive','Reactive'])
    plt.xlabel('Separation [lambda]')
    plt.ylabel('Mutual-impedance [Ohm]')
    plt.title('2 side-by-side half-wave dipoles\n'
              'simulated with NEC2 '
              f'(wire radius={w_radii/(2*lamhalf)} lambda)')
    plt.show()


test_Deck()
test_Deck_load_necfile()
test_Deck_exec_pynec()
test_StructureModel()
test_ArrayModel_offcenter()
test_Array_2_lamhalfdip_sbys()

