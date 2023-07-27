import enum
import pyvisa

class RangeOptions(enum.Enum):
    minRange = "MIN"
    maxRange = "MAX"
    defRange = "DEF"

class OutputStates(enum.Enum):
    """Device's output state."""

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

class ValueToMeas(enum.Enum):
    """Current characteristic for step setting."""

    voltage     = "VOLT"
    current     = "CURR"
    resistance  = "RES"     # Two-wire ohms measurement
    fresistance = "FRES"    # Four-wire ohms measurement
    frequency   = "FREQ"
    period      = "PER"
    continuity  = "CONT"
    diode       = "DIOD"

class CurrentType(enum.Enum):
    """Type of current to supply or to measure."""

    alternating = "AC"
    direct      = "DC"

class Instrument():
    """
    Class meant to define a generic measurement instrument using GPIB
    connection, and must be inherited by device's specific classes.

    Methods
    -------
    * __init__()        - Called when the class is instantiated.
    * __str__()         - Called when trying to print a class instance.
    * getID()           - Query the instrument's ID string.
    * reset()           - Reset the instrument.
    * clearStatus()     - Clear device's internal status.
    * writeText()       - Write custom text on device's screen.
    * getErrorQueue()   - Read and log device's error queue.
    """

    def __init__(self, rm: pyvisa.ResourceManager, resource: str):
        self.resource = rm.open_resource(resource)
        self.description = "Generic instrument"
    
    def __str__(self):
        return self.description

    def getID(self):
        """Query the instrument's ID string."""

        print(self.resource.query("*IDN?"))

    def reset(self):
        """Reset the instrument."""

        print(self.resource.write("*RST"))
    
    def clearStatus(self):
        """Clear device's internal status."""

        print(self.resource.write("*CLS"))
    
    def writeText(self, text: str):
        """Write custom text on device's screen."""

        print(self.resource.write('DISP:TEXT "{0}"'.format(text)))
    
    def getErrorQueue(self):
        """Read and log device's error queue."""

        print("Error queue from " + self.description)
        print(self.resource.query("SYST:ERR?"))

class FrequencyGenerator_33220A(Instrument):
    """
    Class meant to define the Agilent 33220A Waveform Generator.

    Methods
    -------
    * setOutput()   - Set the generator's output state.
    * setWaveform() - Set up the waveform to generate.
    """

    def __init__(self, rm: pyvisa.ResourceManager, resource: str):
        Instrument.__init__(self, rm, resource)
        self.description = "20MHz Function/Arbitrary Waveform Generator - 33220A"

    def setOutput(self, state: OutputStates):
        """Set the generator's output state. It can be on or off."""

        print("state:", state.value)
        print(self.resource.write("OUTP {0}".format(state.value)))
    
    def setWaveform(self, form: Waveshapes, load: int=50, lowVol: float=0,
                    highVol: float=0.75, period: float=1e-3, width:float=100e-6,
                    trans: float=10e-9, freq:float=2500, ampl: float=1.2,
                    offset: float=0.4):
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
        freq : float, optional
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
        
        self.resource.write("FUNC {0}".format(form.value))
        self.resource.write("OUTP:LOAD {0}".format(load))
        if form == Waveshapes.pulse:
            self.resource.write("VOLT:LOW {0}".format(lowVol))
            self.resource.write("VOLT:HIGH {0}".format(highVol))
            self.resource.write("PULS:PER {0}".format(period))
            self.resource.write("PULS:WIDT {0}".format(width))
            self.resource.write("PULS:TRAN {0}".format(trans))
        elif form == Waveshapes.sine:
            self.resource.write("FREQ {0}".format(freq))
            self.resource.write("VOLT {0}".format(ampl))
            self.resource.write("VOLT:OFFS {0}".format(offset))
        else:
            print("No implementation for {0} waveform.".format(form.value))


class MultiMeter_34401A(Instrument):
    """
    Class meant to define the Agilent 34401A Multimeter
    
    Methods
    -------
    * setMeasurements() - Set the way to run measurements.
    * getMeas()         - Get value measurement from current measurement setup.
    * read()            - Simply read the value shown on the device.
    """

    def __init__(self, rm: pyvisa.ResourceManager, resource: str):
        Instrument.__init__(self, rm, resource)
        self.description = "Agilent 6 1/2 Digit Multimeter - 34401A"
    
    def setMeasurements(self, type: CurrentType=CurrentType.direct,
                        voltRange: float=10, resolution: float=0.001):
        """Set the way to run measurements. No measure is made at this step."""

        # print(self.resource.write("CONF:CURR:{0} {1}, {2}".format(type.value, voltRange, resolution)))
        print(self.resource.write("CONF:CURR:DC MAX, MAX"))

    def getMeas(self, mode: ValueToMeas, curr_type: CurrentType):
        """Get value measurement from current measurement setup."""

        print(self.resource.query_ascii_values("MEAS:{0}:{1}?".format(mode.value, curr_type.value)))
    
    def read(self):
        """Simply read the value shown on the device."""

        return self.resource.query("READ?")


class PowerSupply_E3644A(Instrument):
    """
    Class meant to define the Agilent E3644A Power Supply.

    Methods
    -------
    * setPower()    - Set the power generated by the power supply device.
    * setOutput()   - Set the generator's output state. It can be on or off.
    * setStepSize() - Set the step size used when calling voltUp() or voltDown().
    * voltUp()      - Increase the volt value provided by the device.
    * voltDown()    - Decrease the volt value provided by the device.
    * getMeasCurr() - Return the current provided by the device, in Amperes.
    """

    def __init__(self, rm: pyvisa.ResourceManager, resource: str):
        Instrument.__init__(self, rm, resource)
        self.description = "Agilent DC Power Supply - E3644A\n \
                            0-8V, 8A / 0-20V, 4A"
    
    def setPower(self, volt: float, maxAmp: float):
        """Set the power generated by the power supply device."""

        print(self.resource.write("APPL {0}, {1}".format(volt, maxAmp)))

    def setOutput(self, state: OutputStates):
        """Set the generator's output state."""

        print("state:", state.value)
        print(self.resource.write("OUTP {0}".format(state.value)))
    
    def setStepSize(self, mode: ValueToMeas, step: float):
        """Set the step size used when calling voltUp() or voltDown()."""

        print(self.resource.write("{0}:STEP {1}".format(mode.value, step)))

    def voltUp(self):
        """Increase the volt value provided by the device, based on the selected
        step size"""
        print(self.resource.write("VOLT UP"))

    def voltDown(self):
        """Decrease the volt value provided by the device, based on the selected
        step size"""
        print(self.resource.write("VOLT DOWN"))

    def getMeasCurr(self):
        """Return the current provided by the device, in Amperes."""
        print(self.resource.query("MEAS:CURR?"))