import enum

class OutputStates(enum.Enum):
    """Device's output state. Can be on or off."""

    on      = "on"
    off     = "off"

class Waveshapes(enum.Enum):
    """Waveshapes to set up on generators."""

    sine    = "SIN"
    square  = "SQU"
    ramp    = "RAMP"
    pulse   = "PULS"
    noise   = "NOISe"
    dc      = "DC"
    user    = "USER"

class StepCharac(enum.Enum):
    """Current characteristic for step setting."""

    voltage = "VOLT"
    current = "CURR"

class CurrentType(enum.Enum):
    """Type of current to supply or to measure."""
    
    alternating = "AC"
    direct      = "DC"

class Instrument():
    """Class meant to define a generic measurement instrument using GPIB
        connection, and must be inherited by device's specific classes."""

    def __init__(self, resource):
        self.resource = resource
        self.description = "Generic instrument"
    
    def __str__(self):
        return self.description

    def getID(self):
        """Query the instrument's ID string."""

        print(self.resource.query("*IDN?"))

    def reset(self):
        """Reset the instrument."""

        print(self.resource.write("*RST"))


class FrequencyGenerator_33220A(Instrument):
    """Class meant to define the Agilent 33220A Waveform Generator."""

    def __init__(self, resource):
        Instrument.__init__(self, resource)
        self.description = "20MHz Function/Arbitrary Waveform generator - 33220A"

    def setOutput(self, state):
        """Set the generator's output state. It can be on or off."""

        print("state:", state)
        print(self.resource.write("OUTP {0}".format(state)))
    
    def setWaveform(self, form, load=50, lowVol=0, highVol=0.75, period=1e-3, width=100e-6, trans=10e-9, freq=2500, ampl=1.2, offset=0.4):
        """
        Set up the waveform to generate.

        Parameters
        ----------
        form : Waveshapes
            The waveshape needed
        load : int, optional
            The load impedance, in Ohms (default is 50 Ohms).
        lowVol : float, optional
            Low level in Volts (default is 0 V)
        highVol : float, optional
            High level in volts (default is 0.75 V)
        period : float, optional
            Interval between pulses in seconds (default is 1 ms)
        width : float, optional
            Pulse width in seconds (default is 100 µs)
        trans : float, optional
            Edge time, where rise time = fall time in seconds (default is 10 ns)
        freq : int, optional
            Signal frequency (default is 2500 Hz)
        ampl : float, optional
            Signal amplitude in Vpp (default is 1.2 Vpp)
        offset : float, optional
            Measure offset in Volts (default is 0.4)

        Depending on the selected waveshape, not every arguments are needed,
        as explained below:
        * sine:
            Needed arguments are highVol, lowVol, period, width and trans
        * square:
            Needed arguments are freq, ampl and offset
        * ramp:
            TODO: Not implemented
        * pulse:
            TODO: Not implemented
        * noise:
            TODO: Not implemented
        * dc:
            TODO: Not implemented
        * user:
            TODO: Not implemented
    
        Returns
        -------
        None
        """
        
        self.resource.write("FUNC {0}".format(form))
        self.resource.write("OUTP:LOAD {0}".format(load))
        if form == Waveshapes.pulse.value:
            self.resource.write("VOLT:LOW {0}".format(lowVol))
            self.resource.write("VOLT:HIGH {0}".format(highVol))
            self.resource.write("PULS:PER {0}".format(period))
            self.resource.write("PULS:WIDT {0}".format(width))
            self.resource.write("PULS:TRAN {0}".format(trans))
        elif form == Waveshapes.sine.value:
            self.resource.write("FREQ {0}".format(freq))
            self.resource.write("VOLT {0}".format(ampl))
            self.resource.write("VOLT:OFFS {0}".format(offset))
        else:
            print("Waveform not implemented.")


class MultiMeter_34401A(Instrument):
    """Class meant to define the Agilent 34401A Multimeter"""

    def __init__(self, resource):
        Instrument.__init__(self, resource)
        self.description = "Agilent 6 1/2 Digit Multimeter - 34401A"
    
    def setMeasurements(self, type=CurrentType.direct.value, voltRange=10, resolution=0.001):
        print(self.resource.write("CONF:VOLT:{0} {1}, {2}".format(type, voltRange, resolution)))

    def getMeasVolt(self):
        print(self.resource.query_ascii_values("MEAS:VOLT:DC?"))
    
    def read(self):
        return self.resource.query("READ?")


class PowerSupply_E3644A(Instrument):
    """Class meant to define the Agilent E3644A Power Supply"""

    def __init__(self, resource):
        Instrument.__init__(self, resource)
        self.description = "Agilent DC Power Supply - E3644A\n \
                            0-8V, 8A / 0-20V, 4A"
    
    def setPower(self, volt, maxAmp):
        print(self.resource.write("APPL {0}, {1}".format(volt, maxAmp)))

    def setOutput(self, state):
        print("state:", state)
        print(self.resource.write("OUTP {0}".format(state)))
    
    def setStepSize(self, mode, step):
        print(self.resource.write("{0}:STEP {1}".format(mode, step)))

    def voltUp(self):
        print(self.resource.write("VOLT UP"))

    def voltDown(self):
        print(self.resource.write("VOLT DOWN"))
    
    def clearStatus(self):
        print(self.resource.write("*CLS"))

    def getMeasCurr(self):
        print(self.resource.query("MEAS:CURR?"))