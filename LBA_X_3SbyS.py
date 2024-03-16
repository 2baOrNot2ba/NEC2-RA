import math
import numpy as np
from nec2 import (ArrayModel, VoltageSource, FreqSteps, Wire,
                  ExecutionBlock, RadPatternSpec)

np.set_printoptions(precision=4, linewidth=80)
PRINT_inpparm = False
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
lba_model = ArrayModel(model_name)
lba_model.set_commentline(lba_model.name)
lba_model.set_commentline('Author: T. Carozzi')
lba_model.set_commentline('Date: 2024-03-03')

lba_model['ant_X']['-X'] = Wire(*l12, wire_radius)
lba_model['puck']['LNA_connect'] = Wire(*l23, wire_radius)
lba_model['ant_X']['+X'] = Wire(*l34, wire_radius)
lba_model['puck']['LNA_connect'].add_port(0.5, 'LNA_x', VoltageSource(1.0))

arr_pos =[[0., 0., 0.], [0., 2., 0.],[0., 4., 0.]]
lba_model.arrayify(element=['ant_X','puck'],
                   array_positions=arr_pos)
nr_freqs = 1
frq_cntr = 70.0
_frq_cntr_step = FreqSteps('lin', nr_freqs, frq_cntr, 2.0)
lba_model.segmentalize(201, frq_cntr)
_port_ex = ('LNA_x', VoltageSource(1.0))
nr_ants = len(arr_pos)
_epl = RadPatternSpec(nth=3, dth=20.0, nph=0, dph=1., phis=90.)
print('Wavelength', 3e2/frq_cntr)
eb_arr = ExecutionBlock(_frq_cntr_step, _port_ex, _epl)
eepSCdat = lba_model.calc_eeps(eb_arr, save_necfile=True)
eelSCdat = eepSCdat.get_EELs()
eepOCdat = eepSCdat.transform_to('OC')
eelOCdat = eepOCdat.get_EELs()
eepdat = eepSCdat
eeldat = eelOCdat
print("Impedances")
Z =  eepdat.get_impedances()
print(Z)
print()

# Get steering vectors
sv = lba_model.calc_steering_vector(eb_arr)

refantnr = 0
for antnr in range(nr_ants):
    eep = eepdat.eeps[antnr]
    eel = eeldat.eels[antnr]
    print("Antenna nr:", antnr)
    for fidx, frq in enumerate(eep.freqs):
        indent = '  '
        print(indent+'Frequency:', frq)
        #print(2*indent+'Radpats', eep.thetas.shape, eep.phis.shape)
        if PRINT_inpparm:
            print(2*indent+'Impedance', eep.inp_Z)
            print(2*indent+'Current', eep.inp_I)
            print(2*indent+'Voltage', eep.inp_V)
        if PRINT_radpat:
            #print('E_theta_amp', np.abs(eep.ef_tht[fidx]))
            #print('E_theta_phs', np.rad2deg(np.angle(eep.ef_tht[fidx])))
            print(2*indent+'Theta, Phi:')
            #thetagrd , phigrd = np.meshgrid(eep.thetas, eep.phis,
            #                                indexing='ij')
            #print(thetagrd, phigrd)
            print(2*indent+'E_phi_amp')
            print(3*indent, str(np.abs(eep.f_phi[fidx])
                                ).replace('\n', '\n'+3*indent))
            print(2*indent+'E_phi_phs')
            _ref_amphs = eepdat.eeps[refantnr].f_phi[fidx]
            print(3*indent, str(np.angle(
                eep.f_phi[fidx]*np.conj(_ref_amphs), deg=True)
                                ).replace('\n', '\n'+3*indent))
            #
            print(2*indent+'eff. lengths')
            print(3*indent, str(np.abs(eel.f_phi[fidx])
                                ).replace('\n', '\n'+3*indent) )
            print(2*indent+'steering_phs')
            print(3*indent, str(np.angle(sv[antnr, fidx], deg=True)
                                ).replace('\n', '\n'+3*indent))

    print()
