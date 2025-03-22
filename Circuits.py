import CircuitAnalysis
"""
Problem#1: Having to charge a 9V battery with a 5V solar panel with 100mA max storage
We can't solely do this, so we need
1) A voltage regulator to turn 5V into 9V for the solar panel. --> DC-DC boost
2) Diode to block the battery from charging BACK to the solar panel (controlling the flow of current)
3) A capacitor may help smooth out the fluctiations in the solar panel's output and provide a steady voltage.

For determining if we need a resistor, we can use Ohlms law
V (9v For the battery) = IR
But as we can see, since we're using a battery, it's more on managing the current flow.


For the capacitance value, we use

C = I(load)/V(voltage ripple) * f (frequency of ripple)
I here is 0.1A, but the rest of these you'll have to find

Example circuit:
1. Solar Cell: Place it on your Tinkercad workspace.
2. Diode: Connect the anode to the positive terminal of the solar cell, and the cathode to the input of a DC-DC boost converter.
3. DC-DC Boost Converter: Connect the output to the positive terminal of your 9V battery.
4. Capacitor: Place it across the output of the boost converter (one leg on the positive output, the other on the negative).
5. Battery: Connect the positive and negative terminals to the corresponding outputs of the boost converter.

# Parts description
############################
NPN Transistor (BJT): This means the current flows from the collector to the emitter when a small current is applied. Base = Signal, Collector = Current, Emitter = Current Exits.
############################


##########################################################################


"""


# Tracking our security cam


