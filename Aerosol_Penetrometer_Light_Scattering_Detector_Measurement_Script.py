"""Aerosol_Penetrometer_Light_Scattering_Detector_Script

This script allows to make measurements with the optical mask tester.
The script uses the class Aerosol_Penetrometer_Light_Scattering_Detector.

First the sample is inserted, and then the device is flushed with air three
times. Second an offset calibration is carrie out.
Therefore the device measures the offset over the given calibration time.
During calibration no air should be sucked in.
After calibration the measurement starts. The smoke of the e-cigarette is
sucked through the device.
After finishing the measurement the device should be flushed once, the sample
should be taken out and then the device should be flushed with air three times.

Author
------
Sebastian Lifka

Created
-------
Sep 22 2020

Modified
--------
Dec 10
 2020
"""

import Aerosol_Penetrometer_Light_Scattering_Detector as mt

# Define measurement and calibration durations in seconds
measurement_duration = 30
calibration_duration = 15

# Initialize Aerosol_Penetrometer_Light_Scattering_Detector object
if not 'x' in globals():
    x = mt.Aerosol_Penetrometer_Light_Scattering_Detector()
    
x.initSerial()

# Do calibration before every single measurement
print("Insert sample and flush device three times.")
input("Press Enter to start calibration...")
calibration_value = x.calibrate(calibration_duration)
print("Calibration value: ")
print(calibration_value)

# Start of measurement
input("Press Enter to start measurement...")
diode_voltage,turbidity,turbidity_ratio,measurement_time = \
                                        x.liveMeasurement(measurement_duration)
# Flush device
print("Flush device once, remove sample then flush device three times.")
                                          
input("Press Enter to finish measurement and show result...")

# Evaluate measurement and show result
total_turbidity = x.integrateTurbidity(turbidity,measurement_time)
total_turbidity_ratio = x.calculateTotalTurbidityRatio(total_turbidity)
filtered_percentage = x.evaluateMeasurement(total_turbidity_ratio)
print("The sampled filtered " + str(filtered_percentage) + "%")

# Saving data
input_val = input("Save data?")
if input_val == 'y':
    x.saveData(diode_voltage,turbidity,turbidity_ratio,measurement_time,
               calibration_value,total_turbidity,
               total_turbidity_ratio,filtered_percentage)
    
print("Measurement finished!")

x.closeSerial()
