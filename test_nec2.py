from io import StringIO
from nec2 import (Deck, Wire, StructureModel, VoltageSource, FreqSteps, 
                  ExecutionBlock, RadPatternSpec)


def test_Deck():
    d = Deck()
    d.put_card('GW', 0, 7, 0., 0., -.25, 0., 0., .25, 1.0E-5)
    d.put_card('GE', 0)
    d.put_card('EX', 0, 0, 4, 0, 1.0)
    d.put_card('EN')
    d2 = Deck([('GW', 0, 7, 0.0, 0.0, -0.25, 0.0, 0.0, 0.25, 1e-05),
               ('GE', 0),
               ('EX', 0, 0, 4, 0, 1.0),
               ('EN',)])
    print(d==d2)


def test_Deck_load_necfile():
    test_necin = \
"""\
CM TESTEX1
CE EXAMPLE 1. CENTER FED LINEAR ANTENNA
CE345678901234567890123456789012345678901234567890123456789012345678901234567890
GW  0    7       0.0        0.      -.25        0.        0.       .25      .001
GE  0
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


def test_Deck_exec_as_pynec():
    d = Deck()
    cntxt = d.exec_as_pynec()
    for f in range(1):
        inp_parms = cntxt.get_input_parameters(f)
        print(inp_parms.get_impedance())


def test_StructureModel():
    model = StructureModel()
    p1 = (+0.5, 0., 0.1)
    p2 = (+0.5, 0., 0.9)
    p3 = (-0.5, 0., 0.9)
    p4 = (-0.5, 0., 0.1)
    l12 = (p1, p2)
    l23 = (p2, p3)
    l34 = (p3, p4)
    wire_rad = 0.001
    #bob1 = model.newtag('bob1')
    #bob1.make_wire(*l12, wire_rad, name='+X', nr_seg=100)
    model['xing']['X+'] = Wire(*l12, wire_rad)
    #main = model.newtag('main')
    #main.make_wire(*l23, wire_rad, name='mid')
    model['xing']['mid'] = Wire(*l23, wire_rad)
    #bob1.make_wire(*l34, wire_rad, name='-X', nr_seg=100)
    model['xing']['X-'] = Wire(*l34, wire_rad)

    #main.make_port('mid', 0.5, VoltageSource(1.0))
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

test_StructureModel()
