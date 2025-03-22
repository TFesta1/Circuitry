import pandas as pd

"""
Instructions
1. Run getGoogleSheetsData to download CSV locally from https://docs.google.com/spreadsheets/d/1Au43Tqi2ISWwhzec27fGJm3A5DM86Kq30X5YPMqKkf8/edit?gid=1904121955#gid=1904121955
2. Read/configure code below

"""

circuitDataPath = r"C:\Users\ringk\OneDrive\Documents\Circuitry\Data\MockSecurityCamCircuitData.csv"

circuitData = pd.read_csv(circuitDataPath, on_bad_lines='skip')




#It works like. [[ALL of these have to be filled], [Only 1 ITEM needs to be in this list]]
componentsRequiredValues = {
    # This is for ensuring that the J-K flipflop won't be damaged, and to measure its power
    "J-K Flip-Flop": [['Resistance Between Power Ohms', 'Maximum Input Voltage Volts', 'Safe Limits Range in Amps'], ['Connected to Transistor Component Name']],
    "LED": [[], []],
    "Servo": [[], []],
    "Transistor": [['Base-Emitter Voltage Drop V_BE Volts'], []]
}


#Parses our component into something we know and can define from above.
def getParsedComponent(component):
    componentReturn = -1
    for key in componentsRequiredValues.keys():
        if key in component:
            return key
    return componentReturn


#parsedComponent needs to be called from getParsedComponent to get the component form the list of componentsRequiredValues
def checkRequiredFields(row, parsedComponent):
    statusCode = "SUCCEED"
    statusMsg = ""

    (requiredAll, requiredOne) = componentsRequiredValues[parsedComponent]
    if len(requiredAll) == 0 or len(requiredOne) == 0:
        statusCode = "FAIL"
        statusMsg = f"{parsedComponent} define this in componentsRequiredValues"
    nullsFound = 0
    itemsMissing = []
    for item in requiredAll:
        if pd.isna(row[item]):
            nullsFound += 1
            itemsMissing.append(item)
    if nullsFound != 0:
        statusCode = "FAIL"
        statusMsg = f"{parsedComponent} is missing the definitions for the following items within the CSV: {' | '.join(itemsMissing)}"
        return (statusCode, statusMsg)
    
    nullsFound = 0
    itemsMissing = []
    for item in requiredOne:
        if pd.isna(row[item]):
            nullsFound += 1
            itemsMissing.append(item)
    if nullsFound != 0 and nullsFound == len(requiredOne):
        statusCode = "FAIL"
        statusMsg = f"{parsedComponent} needs at least ONE definition of the items within the CSV: {' | '.join(itemsMissing)}"
    
        return (statusCode, statusMsg)
    return (statusCode, statusMsg)


voltsInCircuit = 5
failed = False
circuitStatusMsg = "SUCCEED" #SUCCEED, or it will throw some message.
powerConsumption = 0 #On success, it will have Power Consumption 

# Circuit analysis
for i, row in circuitData.iterrows():
    # Checking if voltage goes above any max input volts
    component = row['Component']
    resistanceBetweenPower = row['Resistance Between Power Ohms']
    
    maxInputVoltage = float(row['Maximum Input Voltage Volts'])
    transistorConnectorName = row['Connected to Transistor Component Name']
    limitsRange = row['Safe Limits Range in Amps']
    
    circuitStatusMsg = ""
    presumptiveStatus = f"{component} has 'Maximum Input Voltage Volts' of {maxInputVoltage}v, which is >= than {voltsInCircuit}v, this is above the safe limit."
    
    parsedComponent = getParsedComponent(component)
    if parsedComponent == -1:
        circuitStatusMsg = f"{component} please define this in componentsRequiredValues"
        failed = True
        break

    (statusCode, statusMsg) = checkRequiredFields(row, parsedComponent)
    if statusCode == "SUCCEED": #Only do calcs in this area as we've been sure to check components specifically with their parts only.
        maxSupplyVoltageCondition = maxInputVoltage >= voltsInCircuit
        if parsedComponent in ['J-K Flip-Flop']:
            if pd.isna(transistorConnectorName) == False:
                transistorFilter = circuitData[circuitData['Component'] == transistorConnectorName].iloc[0]
                V_out = voltsInCircuit #Assuming the voltage out of this component would be the same power our circuit is being powered by
                V_be = transistorFilter['Base-Emitter Voltage Drop V_BE Volts'] #Base-emitter
                I_b = (V_out - V_be) / resistanceBetweenPower #Base current of transistor
                firstLimit = float(limitsRange.split(" - ")[0])
                secondLimit = float(limitsRange.split(" - ")[1])
                maxSupplyVoltageCondition = (firstLimit < I_b < secondLimit) == False
                presumptiveStatus = f"{component}. The base current of transistor, {I_b}A, is NOT within the range of {firstLimit}A to {secondLimit}A"

            if maxSupplyVoltageCondition:
                failed = True
                circuitStatusMsg = presumptiveStatus
                break #Simulating returnStatement
    else:
        print(statusMsg)
        failed = True
        break #Simulating returnStatement

print(f"failed {failed} - {circuitStatusMsg}")
#Fetch the sheet
# time.sleep(10000)
    




"""
Units: mA, A
"""
def convertCurrentToAmps(value, unit):
    conversionHashmap = {"mA": 1/1000}
    return conversionHashmap[unit] * value
convertCurrentToAmps(4, "mA")
def convertToOhms(value, unit):
    conversionHashmap = {"kOhms": 1000}
    return conversionHashmap[unit] * value 

# convertToOhms(1, "kOhms")
# Analyzing Voltage Issues
"""
Datasheet key values with math breakdown example
74HC73 Dual J-K Flip-Flop:
1. Maximum Supply Voltage (Vcc): 4.46V
2. Maximum Input Voltage: Should not exceed Vcc (4.46V)
3. Output Current Limit: The maximum current the output pins can source/sink without damage (explain)

NPN Transistor BJT
1. Collector-Emitter Voltage (Vce): Max voltage the transistor can handle between collector and emitter
2. Base-Emitter Voltage (Vbe): Max volt between base and emitter
3. Maximum Collector Current (lc): Determines the load the transistor can handle.

LED:
1. Forward Voltage (Vf): Voltage required to turn the LED on (2v typically for red)
2. Maxumum Forward Current: Usually ~20mA for standard LEDs (explain)

Servo Motors (assuming ours draws 100mA at 5V):
1. Operating voltage: Check if they operate on 5V
2. Current Draw: Peak current during movement



Math example on circuit 
https://www.tinkercad.com/things/3fEo4d1NZqQ/editel?returnTo=%2Fdashboard%2Fdesigns%2Fcircuits
https://docs.google.com/spreadsheets/d/1Au43Tqi2ISWwhzec27fGJm3A5DM86Kq30X5YPMqKkf8/edit?gid=1904121955#gid=1904121955

Steps:
1.Arduino is 5V
2 Since safe limit of 74HC73 is 4.46V, and 5V > 4.46, we add 1kΩ on pins here. I_B = (V_out - V_BE) / R
I_B = Base current of transistor
V_out = Output voltage of 74HC73 (5V within our circuit)
V_BE = base-emitter voltage drop of NPN Transistor (typically 0.7V for standard BJTs)
R = Resistance (1kΩ)

I_B = (5V - 0.7V) / 1000Ω = 0.0043A = 4.3mA --> safe limits of 74HC73
Output current of 74HC73:
I_OH: Maximum current output can source, when it is HIGH (typically 4-8mA for 5V) --> One we're using
I_OL: Maximum current output can source, when it is LOW (typically 4-8mA for 5V)

Relevant sections on datasheet:
- "Absolute Maximum Ratings": Max current the IC can handle without damage
- "Electrical Characteristics": Specifies maximum I_OH/I_OL under 5V or other typical voltages


#Power calc for resistors
3. Using Ohms law (I = V/R) and Power formula (P = V * I) we get P = V^2/R. So, for 1kΩ connected to 5V we get P = (5V)^2 / 1000 Ω = 0.025W (25mW)
4. For 8 resistors, we get 8 * 0.025W = 0.2W (200mW)
#Power calc for LED
5. Assuming forward voltage of 2V and a current-limiting resistor of 330Ω
6. I_led = (5V - 2V) / 330Ω = 0.009A (9mA)
7. P_led = 2V * 0.009A = 0.018W (18mW)
# Power calc for 2 servos (these draw a lot of current)
8. Assuming this draws 100mA at 5V
9. P_servo = 5V * 0.1A = 0.5W (500mW)
10. P_servos = 2*0.5W = 1.0W
# Total power
11. Resistors (200mW) LED (18mW) Servos (1.0W)
P_total = 0.2W + 0.018W + 1.0W = 1.218W

#Note: When it is turned off (momentary button not pressed)
12. Arduino's idle power and leakage current is assumed to be 50mW

Total Power Draw: 1.218W
Circuit is off: ~50mW


"""