import pyvisa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time

from instr import *

def printData(width, data, date, sampleRate, sine_wave, sine_ampl):

    fig = plt.figure(figsize=(width/42, 9), dpi=300, facecolor='w', edgecolor='k')
    plt.plot(data.t, data.V)
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.title('Agilent 34401A measurement\nRange: 10V (DC), Resolution: 4.5 digits @ ' +
              str(sampleRate) + ' Sa/s, $f$ = ' + str(sine_wave) + 'Hz, $v_0$ = ' + str(sine_ampl) + 'V$_{pp}$')
    plt.grid(True)
    plt.savefig('{0}_measurement_result.png'.format(date))
    # plt.show()

sineWave       = 1
sineAmpl       = 0.5
rm              = pyvisa.ResourceManager()
res_list        = rm.list_resources()
print(res_list)

# power_supply    = PowerSupply_E3644A(rm, res_list[0])
frequ_gen       = FrequencyGenerator_33220A(rm, res_list[1])
multimeter      = MultiMeter_34401A(rm, res_list[2])

# print(power_supply)
print(frequ_gen)
print(multimeter)

frequ_gen.getID()
frequ_gen.reset()
frequ_gen.setWaveform(Waveshapes.pulse, load=50, lowVol=0, highVol=2, period=0.5, width=0.2, trans=5e-9)
# frequ_gen.setWaveform(Waveshapes.sine, load=50, freq=sine_wave, ampl=sine_ampl, offset=0)
frequ_gen.setOutput(OutputStates.on)

multimeter.getID()
multimeter.reset()
multimeter.setMeasurements(type=CurrentType.alternating)

# power_supply.getID()
# power_supply.reset()
# power_supply.setStepSize(StepMode.voltage, 0.2)
# power_supply.setPower(3.2, 0.25)
# power_supply.setOutput(OutputStates.on)

N = 2048
# N = 200
# N = 512
data = pd.DataFrame(columns=['t', 'V'])
date = datetime.datetime.now().strftime('%Y.%m.%d_%Hh%Mm%Ss%f')

print(date)
t0 = time.time()
for i in range(N):
    if i % 20 == 0:
        print("Iteration {0}".format(i))
    data.loc[i] = [time.time() - t0, multimeter.read()]

data.V = data.V.astype(float)

# print(data)
elapsedTime = data.iloc[N-1].t
sampleRate = str(np.round((len(data)-1)/elapsedTime, 3))
print("Elapsed time: ", elapsedTime)
print("Sampling rate: ", sampleRate)

printData(N, data, date, sampleRate, sineWave, sineAmpl)

frequ_gen.writeText("Cleaning buffer...")
frequ_gen.getErrorQueue()
frequ_gen.clearStatus()
multimeter.writeText("Cleaning buffer...")
multimeter.getErrorQueue()
multimeter.clearStatus()

frequ_gen.writeText("JOB DONE")
multimeter.writeText("JOB DONE")

# power_supply.setOutput(instr.OutputStates.off.value)