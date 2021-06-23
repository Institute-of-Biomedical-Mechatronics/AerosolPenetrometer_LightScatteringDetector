"""Class file for the Aerosol_Penetrometer_Light_Scattering_Detector_V2."""
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import glob
import warnings


class Aerosol_Penetrometer_Light_Scattering_Detector_V2:
    """
    A class for using the Aerosol_Penetrometer_Light_Scattering_Detector_V2.

    Author
    ------
    Sebastian Lifka

    Created
    -------
    Jan 22 2021

    Modified
    --------
    Jun 23 2021

    Attributes
    ----------
    measurement_volume : int
        Total measurement volume sucked up with the syringe in liter
    total_turbidity_ratio_idle : float
        Total turbidity ratio without mask. Typically it is grater than one,
        because in the measurement chamber after the mask an additional hole
        to measure the pressure is present opposite to the 90° sensor.
        Therefore, the detected intensity of the 90° sensor after the mask is
        lower.
    __calibration_value : float
        offset value of the turbidity before and after the mask (default [0,0])
    __serial_port : str
        serial port of the arduino
    __baud_rate : int
        baud rate of the serial port communication (default 9600)
    __arduino : serial object
        serial object of the arduino

    Methods
    -------
    initSerial()
        Initializes the serial communication to the arduino
    closeSerial()
        Closes the serial communication to the arduino
    getCalibrationValue()
        Returns the calibration value
    getMeasurementVolume
        Get measurement volume
    setMeasurementVolume
        Set measurement volume
    getTotalTurbidityRatioIdle
        Get total turbidity ratio without mask
    setTotalTurbidityRatioIdle
        Set total turbidity ratio without mask
    readData()
        Read the analog voltage values of the photo transistor conneceted to
        the analog inputs of the arduino
    liveMeasurement(measurement_duration)
        Starts a measurement and plots the measurement values live into a
        figure
    plotMeasurement(measurement_time,diode_voltage,turbidity,turbidity_ratio)
        Plots the measurement values
    markFlowStartStop(tart_ind, stop_ind, measurement_time)
        Mark start and stop of the flow in the live measurement.
    calibrate(measurement_duration)
        Measures the trurbidity offset values
    calculateTurbidity(diode_voltage)
        Calculates the turbidity values before and after the mask
    calculateTurbidityRatio(turbidity)
        Calculates the turbidity ratio of the turbidity before and after the
        mask
    integrateTurbidity(turbidity,measurement_time)
        Integrates the turbidity values before and after the sample over time
    calculateTotalTurbidityRatio(total_turbidity)
        Calculates the ratio of the total turbidities before and after the
        sample
    evaluateMeasurement(total_turbidity_ratio)
        Calculates the filtered particle percentage of the sample
    integratePressure(pressure, measurement_time, *args)
        Integrate the relative pressure time
    calculateBreathingResistance(total_pressure):
        Calculate the breathing resistance in mbar/l/min
    calculateFlowRate(pressure, measurement_time):
        Calculate the flow rate in l/min and the flow time in seconds
    """

    def __init__(self, measurement_volume, total_turbidity_ratio_idle,
                 calibration_value=[0.000, 0.000, 0.00], baud_rate=9600):
        """Init function.

        Parameters
        ----------
        measurement_volume : int
            Total measurement volume sucked up with the syringe in liter
        total_turbidity_ratio_idle : float
            Total turbidity ratio without mask.
        calibration_value : float
            offset value of the turbidity before and after the mask and the
            absolute pressure value in mbar
            (default [0,0,0])
        serial_port : str
            serial port of the arduino
        baud_rate : int
            baud rate of the serial port communication (default 9600)
        """
        self.measurement_volume = measurement_volume
        self.total_turbidity_ratio_idle = total_turbidity_ratio_idle
        self.__calibration_value = calibration_value
        serial_port = glob.glob('/dev/cu.usbserial-*')
        if np.size(serial_port) == 0:
            raise ValueError("No device connected!")
        self.__serial_port = serial_port[0]
        self.__baud_rate = baud_rate
        self.__arduino = self.initSerial()

    def initSerial(self):
        """Initialize the serial communication to the arduino.

        Returns
        -------
        self.__arduino : serial object
            Serial object of the arduino
        """
        self.__arduino = serial.Serial(self.__serial_port, self.__baud_rate)
        plt.close(2)
        return self.__arduino

    def closeSerial(self):
        """Close the serial communication to the arduino."""
        self.__arduino.close()

    def getCalibrationValue(self):
        """Return the calibration value.

        Returns
        -------
        calibration_value : float
            Offset value of the turbidity before and after the mask
            (default [0,0])
        """
        calibration_value = self.__calibration_value
        return calibration_value

    def getMeasurementVolume(self):
        """Return the measurement volume.

        Returns
        -------
        measurement_volume : int
            Measurement volume of the syringe in liter
        """
        measurement_volume = self.measurement_volume
        return measurement_volume

    def setMeasurementVolume(self, measurement_volume):
        """Set the measurement volume.

        Parameters
        ----------
        measurement_volume : int
            Measurement volume of the syringe in liter
        """
        self.measurement_volume = measurement_volume

    def getTotalTurbidityRatioIdle(self):
        """Return the total turbidity ratio without mask.

        Returns
        -------
        total_turbidity_ratio_idle : float
            Total turbidity ratio without mask.
        """
        total_turbidity_ratio_idle = self.total_turbidity_ratio_idle
        return total_turbidity_ratio_idle

    def setTotalTurbidityRatioIdle(self, total_turbidity_ratio_idle):
        """Set the total turbidity ratio without mask.

        Parameters
        ----------
        total_turbidity_ratio_idle : float
            Total turbidity ratio without mask
        """
        self.total_turbidity_ratio_idle = total_turbidity_ratio_idle

    def readData(self):
        """Read analog sensor data.

        Read the analog voltage values of the photo transistor connected to
        the analog inputs of the arduino and the pressure value from the
        pressure sensor.

        Returns
        -------
        transistor_voltage : float
            Voltage values in volts of the photo transistors and pressure
            values in mbar in order:
            [Before90° Before180° After90° After180° Pressure]
        """
        outgoing_string = "1"
        self.__arduino.write(outgoing_string.encode())
        while (self.__arduino.inWaiting() < 0):
            time.sleep(0.1)
        data = self.__arduino.readline().decode()
        # Voltage values are split by ';', use .float_ to convert list
        data = list(np.float_(data.split(';')))
        return data

    def liveMeasurement(self, measurement_duration):
        """Live plot of measurement.

        Starts a measurement and plots the measurement values live into a
        figure. Measurement can be interrupted by triggering a
        KeyboardInterrupt.

        Parameters
        ----------
        measurement_duration : int
            Duration time of the measurement in seconds

        Returns
        -------
        transistor_voltage : float
            Voltage values in volts of the photo transistors and pressure
            values in mbar in order:
            [Before90° Before180° After90° After180° Pressure]
        turbidity : float
            Turbidity value (90°signal/180°signal) before and after the mask in
            order: [Before After]
        turbidity_ratio : float
            Ratio beteween the turbidity before and after the mask
        measurement_time : float
            Measurement time in seconds
        """
        data = []
        transistor_voltage = []
        turbidity = []
        turbidity_ratio = []
        pressure = []
        measurement_time = []
        t = time.time()
        elapsed_time = 0
        time.sleep(1)
        print("Measurement started...")
        # Try until KeybordInterrup
        try:
            while elapsed_time < measurement_duration:
                for i in range(10):
                    data.append(self.readData())
                    transistor_voltage.append(data[-1][0:4])
                    # Use transistor_voltage[-1] to use only the latest voltage
                    # value
                    turbidity.append(self.calculateTurbidity(
                        transistor_voltage[-1]))
                    # Use turbidity[-1] to use only the latest turbidity value
                    turbidity_ratio.append(self.calculateTurbidityRatio(
                            turbidity[-1]))
                    pressure.append(round(data[-1][-1] -
                                          self.__calibration_value[-1], 1))
                    elapsed_time = time.time() - t
                    measurement_time = list(np.round_(
                        np.linspace(0, elapsed_time, len(transistor_voltage)),
                        1))
                self.plotMeasurement(measurement_time, transistor_voltage,
                                     turbidity, turbidity_ratio, pressure)
        # Stop manually before end of measurement duration
        except KeyboardInterrupt:
            print("Measurement interrupted.")
        # Plot again to ensure the plot is shown in case of manual interruption
        finally:
            for i in range(10):
                data.append(self.readData())
                transistor_voltage.append(data[-1][0:4])
                # Use transistor_voltage[-1] to use only the latest voltage
                # value
                turbidity.append(self.calculateTurbidity(
                    transistor_voltage[-1]))
                # Use turbidity[-1] to use only the latest turbidity value
                turbidity_ratio.append(self.calculateTurbidityRatio(
                            turbidity[-1]))
                pressure.append(round(data[-1][-1] -
                                      self.__calibration_value[-1], 1))
                elapsed_time = round(time.time() - t, 2)
                measurement_time = list(np.round_(
                    np.linspace(0, elapsed_time, len(transistor_voltage)), 1))
            self.plotMeasurement(measurement_time, transistor_voltage,
                                 turbidity, turbidity_ratio, pressure)
            print("Measurement finished.")
        return (transistor_voltage, turbidity, turbidity_ratio, pressure,
                measurement_time)

    def plotMeasurement(self, measurement_time, transistor_voltage, turbidity,
                        turbidity_ratio, pressure):
        """Plot the measurement values.

        Parameters
        ----------
        transistor_voltage : float
            Voltage values in volts of the photo transistors in order:
            [Before90° Before180° After90° After180°]
        turbidity : float
            Turbidity value (90°signal/180°signal) before and after the mask in
            order: [Before After]
        turbidity_ratio : float
            Ratio between the turbidity before and after the mask
        measurement_time : float
            Measurement time in seconds
        """
        plt.ion()  # Enable plot live update
        plt.clf()  # Clear old plot
        plt.subplot(311)
        plt.plot(measurement_time, pressure)
        plt.grid(True)
        if self.__calibration_value == [0.000, 0.000, 0.0]:
            plt.title("Absolute pressure after mask")
            plt.ylabel("Absolute pressure in mbar")
        else:
            plt.title("Relative pressure after mask")
            plt.ylabel("Relative pressure in mbar")
        plt.xlabel("Time in s")
        plt.subplot(312)
        plt.plot(measurement_time, transistor_voltage)
        plt.grid(True)
        plt.title("Photo transistor voltage")
        plt.xlabel("Time in s")
        plt.ylabel("Photo transistor voltage in V")
        plt.legend(["Before 90°", "Before 180°", "After 90°", "After 180°"])
        plt.subplot(313)
        plt.plot(measurement_time, turbidity)
        plt.plot(measurement_time, turbidity_ratio)
        plt.grid(True)
        if self.__calibration_value == [0.000, 0.000, 0.0]:
            plt.title("Turbidity and turbidity ratio (before/after mask)")
            plt.ylabel("Turbidity, turbidity ratio")
        else:
            plt.title("Corrected turbidity and turbidity ratio " +
                      "(before/after mask)")
            plt.ylabel("Corrected turbidity, turbidity ratio")
        plt.xlabel("Time in s")
        plt.legend(["Before", "After", "Ratio"])
        plt.draw_all()
        plt.pause(1e-3)  # Some time to draw figure
        plt.tight_layout()

    def markFlowStartStop(self, start_ind, stop_ind, measurement_time):
        """Mark start and stop of the flow in the live measurement.

        Parameters
        ----------
        start_ind : TYPE
            DESCRIPTION.
        stop_ind : TYPE
            DESCRIPTION.
        measurement_time : TYPE
            DESCRIPTION.

        Returns
        -------
        None.
        """
        # warnings.filterwarnings("ignore")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            plt.ion()
            fig = plt.figure(1)
            fig.add_subplot(3, 1, 1)
            plt.axvline(x=measurement_time[start_ind], color='k',
                        linestyle='--')
            plt.axvline(x=measurement_time[stop_ind], color='k',
                        linestyle='--')
            plt.text(measurement_time[start_ind]+0.05, 0, 'Start')
            plt.text(measurement_time[stop_ind]+0.05, 0, 'Stop')
            fig.add_subplot(3, 1, 2)
            plt.axvline(x=measurement_time[start_ind], color='k',
                        linestyle='--')
            plt.axvline(x=measurement_time[stop_ind], color='k',
                        linestyle='--')
            fig.add_subplot(3, 1, 3)
            plt.axvline(x=measurement_time[start_ind], color='k',
                        linestyle='--')
            plt.axvline(x=measurement_time[stop_ind], color='k',
                        linestyle='--')
            plt.draw_all()
            plt.pause(1e-1)  # Some time to draw figure

        # warnings.filterwarnings("default")

    def calibrate(self, measurement_duration):
        """Measure the trurbidity offset values.

        Parameters
        ----------
        measurement_duration : int
            Duration time of the measurement in seconds

        Returns
        -------
        self.__calibration_value : float
            offset value of the turbidity before and after the mask
            (default [0,0])
        """
        self.__calibration_value = [0.000, 0.000, 0.0]
        (transistor_voltage, turbidity, turbidity_ratio, pressure,
         measurement_time) = self.liveMeasurement(measurement_duration)
        # Calculate the mean turbidity before the mask over calibration time
        self.__calibration_value[0] = round(np.mean(
                [i[0] for i in turbidity]), 3)
        # Calculate the mean turbidity after the mask over calibration time
        self.__calibration_value[1] = round(np.mean(
                [i[1] for i in turbidity]), 3)
        self.__calibration_value[2] = round(np.mean(pressure), 1)
        return self.__calibration_value

    def calculateTurbidity(self, transistor_voltage):
        """Calculate the turbidity values before and after the mask.

        Parameters
        ----------
        transistor_voltage : float
            Voltage values in volts of the photo transistors in order:
            [Before90° Before180° After90° After180°]

        Returns
        -------
        turbidity : float
            Turbidity value (90°signal/180°signal) before and after the mask in
            order: [Before After]
        """
        turbidity = [0.000, 0.000]
        # Correct the turbidity value before the mask by the calibration offset
        turbidity[0] = round(transistor_voltage[0]/transistor_voltage[1] -
                             self.__calibration_value[0], 3)
        # Correct the turbidity value after the mask by the calibration offset
        turbidity[1] = round(transistor_voltage[2]/transistor_voltage[3] -
                             self.__calibration_value[1], 3)
        if turbidity[0] < 0:
            turbidity[0] = 0.000
        elif turbidity[1] < 0:
            turbidity[1] = 0.000
        return turbidity

    def calculateTurbidityRatio(self, turbidity):
        """Calculate the turbidity ratio before and after the mask.

        Parameters
        ----------
        turbidity : float
            Turbidity value (90°signal/180°signal) before and after the mask in
            order: [Before After]

        Returns
        -------
        turbidity_ratio : float
            Ratio between the turbidity before and after the mask
        """
        # If the two turbidity values are samller than epsilon, which means
        # both turbiditys are nearly equal set the turbidity ratio to 1 to
        # avoid devide by zero and excessive fluctuations of the ratio
        epsilon = 5e-3
        if turbidity[0] < epsilon and turbidity[1] < epsilon:
            turbidity_ratio = 1.000
        else:
            turbidity_ratio = round(turbidity[1]/turbidity[0], 3)
        return turbidity_ratio

    def integrateTurbidity(self, turbidity, measurement_time, *args):
        """Integrate turbidity values before and after the sample over time.

        Integration is done by using the trapezoidal rule.

        Parameters
        ----------
        turbidity : float
            Turbidity value (90°signal/180°signal) before and after the mask in
            order: [Before After]
        measurement_time : float
            Measurement time in seconds

        Returns
        -------
        total_turbidity : float
            Integrated turbidity values over time
        """
        total_turbidity = [0.000, 0.000]
        if np.size(args) == 0:
            start_ind = 0
            stop_ind = np.size(measurement_time)
        elif np.size(args) != 0:
            start_ind = args[0]
            stop_ind = args[1]
        total_turbidity[0] = round(
            np.trapz([i[0] for i in turbidity[start_ind:stop_ind]],
                     measurement_time[start_ind:stop_ind]), 3)
        total_turbidity[1] = round(
            np.trapz([i[1] for i in turbidity[start_ind:stop_ind]],
                     measurement_time[start_ind:stop_ind]), 3)
        return total_turbidity

    def calculateTotalTurbidityRatio(self, total_turbidity):
        """Calculate ratio of total turbidities before and after the sample.

        Parameters
        ----------
        total_turbidity : float
            Integrated turbidity values over time

        Returns
        -------
        total_turbidity_ratio : float
            Ratio of the total, integrated trubidity values before and after
            the sample
        """
        total_turbidity_ratio = round(total_turbidity[1]/total_turbidity[0], 3)
        return total_turbidity_ratio

    def evaluateMeasurement(self, total_turbidity_ratio):
        """Calculate the filtered particle percentage of the sample.

        Parameters
        ----------
        total_turbidity_ratio : float
            Ratio of the total, integrated trubidity values before and after
            the sample

        Returns
        -------
        filtered_percentage : float
            Filtered particle percentage
        penetration_percentage : float
            Particle penetration percentage
        """
        filtered_percentage = round(
            (1.000-total_turbidity_ratio/self.total_turbidity_ratio_idle)*100,
            1)
        penetration_percentage = round(
                total_turbidity_ratio/self.total_turbidity_ratio_idle*100, 1)
        return filtered_percentage, penetration_percentage

    def integratePressure(self, pressure, measurement_time, *args):
        """Integrate the relative pressure time.

        Parameters
        ----------
        pressure : float
            Relative pressure after the mask in mbar
        measurement_time : float
            Measurement time in seconds

        Returns
        -------
        total_pressure : float
            Relative pressure integrated over time in mbar s
        """
        total_pressure = 0.000
        if np.size(args) == 0:
            start_ind = 0
            stop_ind = np.size(measurement_time)
        elif np.size(args) != 0:
            start_ind = args[0]
            stop_ind = args[1]
        total_pressure = round(np.trapz(pressure[start_ind:stop_ind],
                                        measurement_time[start_ind:stop_ind]),
                               3)*-1
        return total_pressure

    def calculateBreathingResistance(self, total_pressure):
        """Calculate the breathing resistance in mbar/l/min.

        Parameters
        ----------
        total_pressure : float
            Relative pressure integrated over time in mbar s

        Returns
        -------
        breathing_resistance : float
            Breathing resistance of the mask in mbar/l/min
        equivalent_breathing_resistance : float
            Aquivalent breathing resistance in mbar @ 30 l/min as it is
            specified in EN149
        """
        breathing_resistance = round(
            (total_pressure/60)/self.measurement_volume, 3)
        # Equivalent br. res. with smoke
        equivalent_breathing_resistance = round(breathing_resistance/6 - 1, 3)
        return breathing_resistance, equivalent_breathing_resistance

    def calculateFlowRate(self, pressure, measurement_time):
        """Calculate the flow rate in l/min and the flow time in seconds.

        Parameters
        ----------
        pressure : float
            Relative pressure after the mask in mbar
        measurement_time : float
            Measurement time in seconds

        Returns
        -------
        flow_rate : float
            Flow rate in l/min
        flow_time : float
            Duration of the flow in seconds
        start_ind : int
            Array index of flow start
        stop_ind : int
            Array index of flow stop
        """
        pressure_derivation = np.diff(pressure)
        # Typical pressure derivation due to noise
        pressure_noise_derivation = 0.1
        ind = np.where(abs(pressure_derivation) > pressure_noise_derivation)
        if np.size(ind[0]) == 0:
            flow_rate = 0.000
            flow_time = 0.000
            start_ind = 0
            stop_ind = np.size(measurement_time)
            return flow_rate, flow_time, start_ind, stop_ind
        start_ind = ind[0][0]
        # start_ind_t = np.where(pressure_derivation ==
        #   min(pressure_derivation))
        # start_ind = start_ind_t[0][0]
        stop_ind_t = np.where(pressure_derivation == max(pressure_derivation))
        stop_ind = stop_ind_t[0][0] + 1
        flow_time = measurement_time[stop_ind] - measurement_time[start_ind]
        flow_rate = round(self.measurement_volume/flow_time*60, 3)
        return flow_rate, round(flow_time, 2), start_ind, stop_ind
