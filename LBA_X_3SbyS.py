import math
import cmath
import numpy as np
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

arr_pos =[[0.,0.,0.], [0., 2., 0.],[0.,4.,0.]]
lba_model.arrayify(element=['ant_X','puck'],
                   array_positions=arr_pos)
nr_freqs = 1
frq_cntr = 50.0
_frq_cntr_step = FreqSteps('lin', nr_freqs, 50.0, 2.0)
lba_model.segmentalize(201, frq_cntr)
_port_ex = ('LNA_x', VoltageSource(1.0))
nr_ants = len(arr_pos)
_epl = RadPatternSpec(nth=3, dth=1.0, nph=0, dph=3., phis=90.)
print('Wavelength', 3e2/frq_cntr)

eeps = lba_model.calc_eeps(ExecutionBlock(_frq_cntr_step, _port_ex, _epl),
                           save_necfile=True)
for antnr in range(nr_ants):
    eep =  eeps[antnr]
    print("Antenna nr:", antnr)
    for fidx, frq in enumerate(eep.freqs):
        print('Frequency:', frq)
        print('Radpats', eep.thetas[fidx].shape, eep.phis[fidx].shape)
        if PRINT_inpparm:
            print('Impedance', eep.inp_Z)
            print('Current', eep.inp_I)
            print('Voltage', eep.inp_V)
        if PRINT_radpat:
            print('E_theta_amp', np.abs(eep.ef_tht[fidx]))
            print('E_theta_phs', np.angle(eep.ef_tht[fidx]))
            print('E_phi_amp', np.abs(eep.ef_phi[fidx]))
            print('E_phi_phs', np.angle(eep.ef_phi[fidx]))
            #_e = [cmath.polar(e_i) for e_i in eep.ef_phi]
            #e_vert_ampphs_str = [(e_i[0],
            #                      math.degrees(e_i[1]-0*_e[0][1])) 
            #                      for e_i in _e] 
            #print('Theta [deg], Voltage [V (amp, rel.phas/deg)]')
            #for _p in zip(eep.thetas, e_vert_ampphs_str):
            #    print(*_p)
        if (PRINT_inpparm or PRINT_radpat) and antnr+1 < nr_ants:
            print()
