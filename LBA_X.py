import math
from nec2 import (StructureModel, VoltageSource, FreqSteps, Wire,
                  ExecutionBlock, RadPatternSpec)

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
_hemisph = RadPatternSpec().hemisphere(nth=30, nph=40)
print('SEGMENET', lba_model.segmentalize(201, _frq_cntr.max_freq()))

for antnr in range(3):
    _prt_exc = ((antnr, 'LNA_x'), VoltageSource(2.0))
    _xb = ExecutionBlock(_frq_cntr, [_prt_exc], _hemisph)
    lba_model.add_executionblock('xb0' , _xb, reset=True)

    deck = lba_model.as_neccards()
    deck.save_necfile(lba_model.name+str(antnr))
    if True:
        for nec_context in deck.exec_pynec():
            for f in range(1):
                inp_parms = nec_context.get_input_parameters(f)
                print(inp_parms.get_impedance()[0])

