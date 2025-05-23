import pandas as pd
import math
import getGoogleSheetsData
"""
Instructions
1. Run getGoogleSheetsData to download CSV locally from https://docs.google.com/spreadsheets/d/1Au43Tqi2ISWwhzec27fGJm3A5DM86Kq30X5YPMqKkf8/edit?gid=1904121955#gid=1904121955
2. Read/configure code below

"""

"""
Units: mA, A
"""
#Fetch the sheet
# time.sleep(10000)
    





# convertToWatts(50, 'mW')
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

def convertCurrentToAmps(value, unit):
    conversionHashmap = {"mA": 1/1000,
                         "uA": 1/1000000}
    return conversionHashmap[unit] * value
# convertCurrentToAmps(10, "mA")
def convertToOhms(value, unit):
    conversionHashmap = {"kOhms": 1000,
                         "µA": 1/1000000}
    return conversionHashmap[unit] * value 
convertToOhms(15, "µA")
def convertToWatts(value, unit):
    conversionHashmap = {"mW": 1/1000}
    return conversionHashmap[unit] * value 

basePath = r"C:\Users\ringk\OneDrive\Documents\Circuitry\Data"

circuitParameters = pd.read_csv(fr"{basePath}\Circuit Parameters.csv", on_bad_lines='warn') #Constant

##################################################################################
# PARAMETERS
# NOTE: DO NOT HAVE COMMAS IN YOUR CSV
# Mock security cam
# circuitData = pd.read_csv(fr"{basePath}\Mock Security Latch Table.csv", on_bad_lines='warn') #Changing
# circuitRequired = pd.read_csv(fr"{basePath}\Mock Security Latch Required Fields.csv", on_bad_lines='warn') #Changing

# Security cam
circuitData = pd.read_csv(fr"{basePath}\Security Latch Table.csv", on_bad_lines='warn') #Changing
circuitRequired = pd.read_csv(fr"{basePath}\Security Latch Required Fields.csv", on_bad_lines='warn') #Changing
##################################################################################

componentsRequiredValues = {}
for i, row in circuitRequired.iterrows():
    requiredAll = []
    requiredAny = []
    if pd.isna(row['Required Fields (ALL)']) == False:
        requiredAll = row['Required Fields (ALL)'].split(" | ")
        requiredAll = [x.strip() for x in requiredAll]
    if pd.isna(row['Optional Fields (ANY)']) == False:
        requiredAny = row['Optional Fields (ANY)'].split(" | ")
        requiredAny = [x.strip() for x in requiredAny]

    componentsRequiredValues[row['Component Type']] = [requiredAll,requiredAny]

"""
Data structure for conversion to spreadsheet:
Component Type | Required Fields (ALL) | Optional Fields (ANY)
------------------------------------------------------------
Flip-Flop      | Resistance Between Power Ohms, Maximum Input Voltage Volts, Safe Limits Range in Amps | Connected to Transistor Component Name
LED            | Forward Voltage (Vf) Volts, Resistance Between Power Ohms | 
Servo          |  | 
Transistor     | Base-Emitter Voltage Drop V_BE Volts | 


"""

#It works like. [[ALL of these have to be filled], [Only 1 ITEM needs to be in this list]]
# componentsRequiredValues = {
#     # This is for ensuring that the J-K flipflop won't be damaged, and to measure its power
#     "Flip-Flop": [['Resistance Between Power Ohms', 'Maximum Input Voltage Volts', 'Safe Limits Range in Amps'], ['Connected to Transistor Component Name']],
#     "LED": [['Forward Voltage (Vf) Volts', 'Resistance Between Power Ohms'], []],
#     "Servo": [["Operation_Volts", "Operation_Amps_At_Volts"], []],
#     "Transistor": [['Base-Emitter Voltage Drop V_BE Volts'], []],
#     "Arduino Uno R3": [["Idle Power"],[]],
#     "Resistor": [['Resistor Resistance Ohms'],[]]
# }


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
    if len(requiredAll) == 0 and len(requiredOne) == 0:
        statusCode = "FAIL"
        statusMsg = f"{parsedComponent} add components within componentsRequiredValues for either list, [requiredAll], [atLeastOne]"
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


voltsInCircuit = circuitParameters[circuitParameters['Parameter'] == 'voltsInCircuit'].iloc[0]['Value']
kWh = circuitParameters[circuitParameters['Parameter'] == 'kWh in USD'].iloc[0]['Value']
failed = False
circuitStatusMsg = "SUCCEED" #SUCCEED, or it will throw some message.
activePowerConsumption = {} #On success, it will have Power Consumption
currentConsumption = {}
idlePowerConsumptionDict = {}
powerBreakdown = {}
testParsedComponent = ""
printLineSeperator = "-----------------------------------"

maxAmps = -1
voltsRunning = -1 #Just initializing, it will throw an error anyways if it doesn't get set

# For power consumption, we need to stay under our power source.
mainPowerSource = circuitData[circuitData['Main Power Source'] == True]
if len(mainPowerSource) != 1:
    failed = True
    circuitStatusMsg = "Set one component's 'Main Power Source' to True to indiciate that this is mainly where the circuit is getting power from"

elif len(mainPowerSource) == 1:
    maxAmps = mainPowerSource.iloc[0]['Operation_Amps_At_Volts']
    voltsRunning = mainPowerSource.iloc[0]['Operation_Volts']
    if pd.isna(maxAmps) or pd.isna(voltsRunning):
        circuitStatusMsg = "Set the 'Main Power Source' Operation_Amps_At_Volts and Operation_Volts"
        failed = True
        


if failed == False:
    # Circuit analysis
    for i, row in circuitData.iterrows():
        # Checking if voltage goes above any max input volts
        component = row['Component'].strip()
        resistanceBetweenPower = row['Resistance Between Power Ohms']
        
        maxInputVoltage = float(row['Maximum Input Voltage Volts'])
        transistorConnectorName = row['Connected to Transistor Component Name']
        limitsRange = row['Safe Limits Range in Amps']
        forwardVoltage = row['Forward Voltage (Vf) Volts']
        idlePowerConsumption = row['Idle Power']
        ignore = row['Ignore In Script']
        quantity = row['Quantity']
        resistance = row['Resistor Resistance Ohms']
        operationalVolts = row['Operation_Volts']
        operationalAmpsAtVolts = row['Operation_Amps_At_Volts']
        normalPowerOperation = row['Normal Power Operation']
        isPowerSource = row['Main Power Source']
        componentPrefix = f"{component} -"
        # print(f"{component}")
        
        if ignore != True: #For stuff like pushbuttons, we may not need to do any calc, but we still want it listed as a material.
            parsedComponent = getParsedComponent(component)
            if parsedComponent == -1:
                circuitStatusMsg = f"{component} please define this in componentsRequiredValues"
                failed = True
                break
            
            (statusCode, statusMsg) = checkRequiredFields(row, parsedComponent)
            if statusCode == "SUCCEED": #Only do calcs in this area as we've been sure to check components specifically with their parts only.
                maxSupplyVoltageCondition = maxInputVoltage >= voltsInCircuit
                presumptiveStatus = f"{component} has 'Maximum Input Voltage Volts' of {maxInputVoltage}v, which is >= than {voltsInCircuit}v, this is above the safe limit."

                if parsedComponent == 'Flip-Flop':
                    
                    if pd.isna(transistorConnectorName) == False:
                        transistorFilter = circuitData[circuitData['Component'] == transistorConnectorName].iloc[0]
                        V_out = voltsInCircuit #Assuming the voltage out of this component would be the same power our circuit is being powered by
                        V_be = transistorFilter['Base-Emitter Voltage Drop V_BE Volts'] #Base-emitter
                        I_b = (V_out - V_be) / resistanceBetweenPower #Base current of transistor
                        firstLimit = float(limitsRange.split(" - ")[0])
                        secondLimit = float(limitsRange.split(" - ")[1])
                        maxSupplyVoltageCondition = (firstLimit < I_b < secondLimit) == False
                        presumptiveStatus = f"{component}. The base current of transistor, {I_b}A, is NOT within the range of {firstLimit}A to {secondLimit}A"

                if row['PowerComponent'] == True:
                    # Doing power
                    if parsedComponent == "LED":
                        pass
                        # 5. Assuming forward voltage of 2V and a current-limiting resistor of 330Ω
                        # 6. I_led = (5V - 2V) / 330Ω = 0.009A (9mA)
                        # 7. P_led = 2V * 0.009A = 0.018W (18mW)
                        
                        I_component = (voltsInCircuit - forwardVoltage) / resistanceBetweenPower
                        P_component = (forwardVoltage * I_component) * quantity #This is in Watts
                        print(f"{componentPrefix} Using our circuit power supply of {voltsInCircuit}V, and a forward voltage of {forwardVoltage}V and a current-limiting resistor of {resistanceBetweenPower}Ω")
                        print(f"{componentPrefix} I_component = (({voltsInCircuit}v - {forwardVoltage}V) / {resistanceBetweenPower}Ω) * {quantity}quantity = {round(P_component, 4)}W ")
                        print(printLineSeperator)
                        currentConsumption[component] = I_component

                        activePowerConsumption[component] = P_component 
                    elif parsedComponent == "Resistor":
                        # 3. Using Ohms law (I = V/R) and Power formula (P = V * I) we get P = V^2/R. So, for 1kΩ connected to 5V we get P = (5V)^2 / 1000 Ω = 0.025W (25mW)
                        # 4. For 8 resistors, we get 8 * 0.025W = 0.2W (200mW)
                        P_component = ((math.pow(voltsInCircuit,2))/resistance) * quantity #Watts
                        print(f"{componentPrefix} Using Ohms law (I = V/R) and Power formula (P = V * I) we get P = V^2/R. So, for {resistance}Ω connected to {voltsInCircuit}V")
                        print(f"{componentPrefix} P_component = (({voltsInCircuit}V ^ 2) / {resistance}Ω) * {quantity}quantity = {round(P_component,4)}W")
                        print(printLineSeperator)
                        activePowerConsumption[component] = P_component
                    elif normalPowerOperation == True:
                        # 8. Assuming this draws 100mA at 5V
                        # 9. P_servo = 5V * 0.1A = 0.5W (500mW)
                        # 10. P_servos = 2*0.5W = 1.0W
                        if voltsInCircuit != operationalVolts:
                            circuitStatusMsg = f"{componentPrefix} failed, the volts in circuit is {voltsInCircuit}V, but the operational volts specified here is {operationalVolts}. These do not equal eachother when they should. Please get the data for the operational voltage for which matches the circuit voltage"
                            failed = True
                            break
                            
                        P_component = (voltsInCircuit * operationalAmpsAtVolts) * quantity
                        if isPowerSource != True:
                            currentConsumption[component] = operationalAmpsAtVolts
                        if parsedComponent == "Solar Panel Source":
                            getSolarPanelManager = circuitData[circuitData['Component'].str.contains("Solar Panel Manager")]
                            

                            if len(getSolarPanelManager) != 1:
                                circuitStatusMsg = f"{componentPrefix} failed, please add in a Solar Panel Manager, since you have a Solar Panel"
                                failed = True
                                break
                            maxChargeCurrent = getSolarPanelManager.iloc[0]['Max Charge Current']
                            if maxChargeCurrent >= operationalAmpsAtVolts:
                                failed = True
                                circuitStatusMsg = f"{componentPrefix} failed, the operational amps of {operationalAmpsAtVolts}A at {voltsInCircuit}V is <= the max charge current of {maxChargeCurrent}A of the Solar Panel Manager, which is above the max"
                                break
                            
                            P_component *= -1 #If it's in the negatives, it's SURPLUS charge for solar panels


                            
                        
                        activePowerConsumption[component] = P_component
                        print(f"{componentPrefix} Using that this draws {operationalAmpsAtVolts}A at {voltsInCircuit}V")
                        print(f"{componentPrefix} P_component = ({voltsInCircuit}V * {operationalAmpsAtVolts}A) * {quantity}quantity = {round(P_component,4)}W")
                        print(printLineSeperator)
                        # 8. Assuming this draws 100mA at 5V
                        # 9. P_servo = 5V * 0.1A = 0.5W (500mW)

                        # break
                    #This is probably the source of power, so we'd want to incorporate this
                    if pd.isna(idlePowerConsumption) == False:
                        idlePowerConsumptionDict[component] = idlePowerConsumption * quantity
                        # break

                if maxSupplyVoltageCondition:
                    failed = True
                    circuitStatusMsg = presumptiveStatus
                    break #Simulating returnStatement
            else:
                circuitStatusMsg = statusMsg
                failed = True
                break #Simulating returnStatement
        if component == testParsedComponent:
            break

if maxAmps != -1:
    sumOfComponentsConsumption = sum(currentConsumption.values())
    if sumOfComponentsConsumption >= maxAmps:
        failed = True
        circuitStatusMsg = f"{currentConsumption} Amps of each component {sumOfComponentsConsumption} >= maxAmps allowed of {maxAmps}A"
print(f"failed {failed} - {circuitStatusMsg}")
if failed == False:
    print(f"Active power consumption components: {activePowerConsumption}")

    P_Active = sum(activePowerConsumption.values())
    P_Active_Max = sum([x for x in activePowerConsumption.values() if x > 0])
    print(f"P_Active Range: {round(P_Active,4)}W | {round(P_Active_Max,4)}W")
    costPerHour = 0
    if P_Active < 0:
        print("Negative indicates a surplus charge, so probably using a LiPo battery for storing excess charge")
    # else:
    costPerHour = (P_Active_Max/1000) * kWh
    print(f"Calculating cost per hour, personal rate of kWh is {kWh}kWh, our active watts is {round(P_Active_Max, 2)}W")
    print(f"Energy = ((P_Active / 1000)-->conversionToKWH * 1hr) * RatePerKWH = (({round(P_Active_Max, 2)}W / 1000) * 1hr) * {kWh} = {round(costPerHour,4)}$ per hour")
    
    print(printLineSeperator)
    
    print(f"Current consumption of components: {currentConsumption}")
    print(f"Sum of current consumption of components {round(sumOfComponentsConsumption,2)}A < maxAmps {maxAmps}A which is good, this circuit has enough amps to run")
    print(printLineSeperator)
    print(f"Idle power consumption components: {idlePowerConsumptionDict}")
    P_Idle = sum(idlePowerConsumptionDict.values())
    print(f"P_Idle = {round(P_Idle,4)}W")



