import math
import cmath
from nec2 import (StructureModel, VoltageSource, FreqSteps, Wire,
                  ExecutionBlock, RadPatternSpec)

PRINT_inpparm = True
PRINT_radpat = True

puck_width = 0.090
puck_height = 1.6
ant_arm_len = 1.38
p1 = (-(ant_arm_len+puck_width)/2, 0.0, puck_height-ant_arm_len/math.sqrt(2))
p2 = (-puck_width/2, 0.0, puck_height)
p3 = (-p2[0], -p2[1], p2[2])
p4 = (-p1[0], -p1[1], p1[2])
l12 = (p1, p2)
l23 = (p2, p3)
l34 = (p3, p4)
wire_radius = 0.003

model_name = __file__.replace('.py','')
lba_model = StructureModel(model_name)
lba_model.set_commentline(lba_model.name)
lba_model.set_commentline('Author: T. Carozzi')
lba_model.set_commentline('Date: 2024-03-03')

lba_model['ant_X']['-X'] = Wire(*l12, wire_radius)
lba_model['puck']['LNA_connect'] = Wire(*l23, wire_radius)
lba_model['ant_X']['+X'] = Wire(*l34, wire_radius)
lba_model['puck']['LNA_connect'].add_port(0.5, 'LNA_x', VoltageSource(1.0))
lba_model.arrayify(element=['ant_X','puck'],
                   array_positions=[[0.,0.,0.], [0., 2., 0.],[0.,4.,0.]])
_frq_cntr = FreqSteps('lin', 1, 50.0, 1.0)
_epl = RadPatternSpec(nth=3, dth=10, phis=0.)
print('SEGMENTS', lba_model.segmentalize(201, _frq_cntr.max_freq()))

for antnr in range(3):
    _prt_exc = ((antnr, 'LNA_x'), VoltageSource(2.0))
    _xb = ExecutionBlock(_frq_cntr, [_prt_exc], _epl)
    lba_model.add_executionblock('xb0' , _xb, reset=True)
    print("Antenna nr:", antnr)
    deck = lba_model.as_neccards()
    deck.save_necfile(lba_model.name+str(antnr))
    for nec_context in deck.exec_pynec():
        for f in range(1):
            if PRINT_inpparm:
                inp_parms = nec_context.get_input_parameters(f)
                print('Frequency:', inp_parms.get_frequency())

                Z = inp_parms.get_impedance()[0]
                I = inp_parms.get_current()[0]
                V = inp_parms.get_voltage()[0]
                print('Impedance', Z)
                print('Current', I)
                print('Voltage', V, I*Z)
            if PRINT_radpat:
                radpat_out = nec_context.get_radiation_pattern(f)
                e_vert = radpat_out.get_e_theta()
                _e = [cmath.polar(e_i) for e_i in e_vert]
                e_vert_ampphs_str = [(e_i[0], math.degrees(e_i[1]-0*_e[0][1])) 
                                     for e_i in _e] 

                print('Theta [deg], Voltage [V (amp, rel.phas/deg)]')
                for _p in zip(radpat_out.get_theta_angles(),
                              e_vert_ampphs_str):
                    print(*_p)
            print()

#print(dir(inp_parms))
