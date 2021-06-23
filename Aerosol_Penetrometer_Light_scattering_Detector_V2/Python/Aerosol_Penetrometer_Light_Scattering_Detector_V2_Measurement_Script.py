"""Aerosol_Penetrometer_Light_Scattering_Detector_V2_Measurement_Script.

This script allows to make measurements with the
Aerosol_Penetrometer_Light_Scattering_Detector_V2.
The script uses the class Aerosol_Penetrometer_Light_Scattering_Detector_V2.

First the sample is inserted, and then the device is flushed with air three
times. Second an offset calibration is carried out.
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
Jan 22 2021

Modified
--------
Jun 23 2021
"""

import Aerosol_Penetrometer_Light_Scattering_Detector_V2 as pen

# =============================================================================
# Define measurement and calibration durations in seconds, measurement volume
# in liter, initial breathing resistance in mbar/l/min and total turbidity
# ratio without mask
# =============================================================================
measurement_duration = 10
calibration_duration = 10
measurement_volume = 60e-3
total_turbidity_ratio_idle = 1.3408  # Mean value of five measurements without
# filter mask sample

# =============================================================================
# Initialize Penetrometer object
# =============================================================================
x = pen.Aerosol_Penetrometer_Light_Scattering_Detector_V2(
    measurement_volume, total_turbidity_ratio_idle)

# =============================================================================
# Do calibration before every single measurement
# =============================================================================
print()
print("Insert sample and flush device three times.")
input("Press Enter to start calibration...")
calibration_value = x.calibrate(calibration_duration)
print()
print("Calibration value: ")
print("Turbidity before mask: " + str(calibration_value[0]))
print("Turbidity after mask: " + str(calibration_value[1]))
print("Absolute pressure after mask: " + str(calibration_value[2]) + " mbar")

# =============================================================================
# Start of measurement
# =============================================================================
input("Press Enter to start measurement...")
transistor_voltage, turbidity, turbidity_ratio, pressure, measurement_time = \
                                        x.liveMeasurement(measurement_duration)

print()
print("Flush device once, remove sample then flush device three times.")

input("Press Enter to finish measurement and show result...")

# =============================================================================
# Evaluate measurement and show result
# =============================================================================
flow_rate, flow_time, start_ind, stop_ind = \
                                x.calculateFlowRate(pressure, measurement_time)
x.markFlowStartStop(start_ind, stop_ind, measurement_time)
total_turbidity = \
    x.integrateTurbidity(turbidity, measurement_time, start_ind, stop_ind)
total_turbidity_ratio = x.calculateTotalTurbidityRatio(total_turbidity)
filtered_percentage, penetration_percentage = \
                                   x.evaluateMeasurement(total_turbidity_ratio)
total_pressure = \
              x.integratePressure(pressure, measurement_time)
breathing_resistance, equivalent_breathing_resistance = \
              x.calculateBreathingResistance(total_pressure)
print()
print("Filter efficiency: " + str(filtered_percentage) + " %")
print("Penetration: " + str(penetration_percentage) + " %")
print("Breathing resistance: " + str(breathing_resistance) + " mbar/l/min")
print("Equivalent breathing resistance: " +
      str(equivalent_breathing_resistance) + " mbar @ 30 l/min")
print("Flow rate: " + str(flow_rate) + " l/min")
print("Flow time: " + str(flow_time) + " s")
print()
print("Measurement finished!")

x.closeSerial()
