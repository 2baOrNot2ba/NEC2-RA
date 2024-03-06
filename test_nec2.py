from antpat.io.nec2 import StructureModel, VoltageSource, FreqSteps

if False:
    d=Deck()
    d.put_card('GW', 0, 7, 0., 0., -.25, 0., 0., .25, 1.0E-5)
    d.put_card('GE', 0)
    d.put_card('EX', 0, 0, 4, 0, 1.0)
    d.put_card('EN')
    d2=Deck([('GW', 0, 7, 0.0, 0.0, -0.25, 0.0, 0.0, 0.25, 1e-05),
            ('GE', 0),
            ('EX', 0, 0, 4, 0, 1.0),
            ('EN',)])
    print(d==d2)
if False:
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
    d.load_necfile(StringIO(test_necin), 'COLUMNS')
    d=load('/home/tobia/Documents/Work_Proj/nec2/halfwavedip_col.nec', 'COLUMNS')
    print(d)
if False:
    cntxt = d.exec_as_pynec()
    for f in range(1):
        inp_parms = cntxt.get_input_parameters(f)
        print(inp_parms.get_impedance())
if False:
    model = StructureModel()
    p1 = (+0.5, 0., 0.1)
    p2 = (+0.5, 0., 0.9)
    p3 = (-0.5, 0., 0.9)
    p4 = (-0.5, 0., 0.1)
    l12 = (p1, p2)
    l23 = (p2, p3)
    l34 = (p3, p4)
    wire_rad = 0.001
    bob1 = model.newtag('bob1')
    bob1.make_wire(*l12, wire_rad, name='+X', nr_seg=100)
    main = model.newtag('main')
    main.make_wire(*l23, wire_rad, name='mid')
    bob1.make_wire(*l34, wire_rad, name='-X', nr_seg=100)

    main.make_port('mid', 0.5, VoltageSource(1.0))
    model.set_freqstep(FreqSteps())
    model.segmentize(10)
    d=model.as_neccards()
    print(d)
    cntxt = d.exec_as_pynec()
    for f in range(1):
        inp_parms = cntxt.get_input_parameters(f)
        print(inp_parms.get_impedance()[0])
