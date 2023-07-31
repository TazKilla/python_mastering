# Main file to test and run intruments for test automation

import datetime
import time

import numpy as np
import pandas as pd
import pyvisa

from instr import *

wavFreq         = 5.0
wavAmpl         = 10.0
rm              = pyvisa.ResourceManager()
res_list        = rm.list_resources()
print(res_list)

# power_supply    = PowerSupply_E3644A(rm, res_list[0])
frequGen        = FrequencyGenerator_33220A(rm, res_list[1])
multimeter      = MultiMeter_34401A(rm, res_list[2])

# print(power_supply)
print(frequGen)
print(multimeter)

frequGen.getID()
frequGen.reset()
frequGen.setWaveform(
    Waveshapes.pulse,
    load    = 50,
    lowVol  = -(wavAmpl / 2),
    highVol = wavAmpl / 2,
    period  = 1 / wavFreq,
    width   = 0.1,
    trans   = 5e-9
)
# frequGen.setWaveform(
#     Waveshapes.sine,
#     load    = 50,
#     freq    = wavFreq,
#     ampl    = wavAmpl,
#     offset  = 0
# )
frequGen.setOutput(OutputStates.on)

multimeter.getID()
multimeter.reset()
multimeter.setMeasurements(ValueToMeas.current, CurrentType.direct, -1, -1)

# power_supply.getID()
# power_supply.reset()
# power_supply.setStepSize(StepMode.voltage, 0.2)
# power_supply.setPower(3.2, 0.25)
# power_supply.setOutput(OutputStates.on)

# N = 32768
N = 2048
# N = 1024
# N = 512
# N = 200
data = pd.DataFrame(columns=['t', 'V'])
date = datetime.datetime.now().strftime('%Y.%m.%d_%Hh%Mm%Ss%f')

print(date)
t0 = time.time()
for i in range(N):
    if i % 32 == 0:
        print("Iteration {0}".format(i))
    data.loc[i] = [time.time() - t0, multimeter.read()]

data.V = data.V.astype(float)

# print(data)
elapsedTime = data.iloc[N-1].t
sampleRate = str(np.round((len(data)-1)/elapsedTime, 3))
print("Elapsed time: ", elapsedTime)
print("Sampling rate: ", sampleRate)

# plotData(N, data, date, sampleRate, wavFreq, wavAmpl)
testData            = PrintData()
testData.format     = FigureFormat.png
testData.imgWidth   = N
testData.valToMeas  = ValueToMeas.current
testData.date       = date
testData.sampleRate = sampleRate
testData.wavFreq    = wavFreq
testData.wavAmpl    = wavAmpl

multimeter.plotData(data, testData)

frequGen.writeText("Cleaning buffer...")
frequGen.getErrorQueue()
frequGen.clearStatus()
frequGen.setOutput(OutputStates.off)

multimeter.writeText("Cleaning buffer...")
multimeter.getErrorQueue()
multimeter.clearStatus()
time.sleep(2)
frequGen.writeText("JOB DONE")
multimeter.writeText("JOB DONE")

# power_supply.setOutput(instr.OutputStates.off.value)