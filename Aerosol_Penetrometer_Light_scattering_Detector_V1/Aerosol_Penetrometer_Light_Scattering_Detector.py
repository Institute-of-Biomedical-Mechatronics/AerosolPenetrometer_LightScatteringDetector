import numpy as np
import matplotlib.pyplot as plt
import serial
import time
from datetime import date
import csv
import os.path

class Aerosol_Penetrometer_Light_Scattering_Detector:
    """
    A class for using the optical mask tester.
    
    Author
    ------
    Sebastian Lifka
    
    Created
    -------
    Sep 14 2020
    
    Modified
    --------
    Dec 10 2020
    
    Attributes
    ----------
    __led_state : int
        1 --> LED On, 0 --> LED Off (default 1)
    __led_brightness : int
        defines the LED brightness in percent (default 100)
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
    getLedState()
        Returns the state (On/Off) of the LED
    setLedState(led_state,led_position)
        Sets the led state (On/Off) of the LED before or after the mask
    getLedBrightness()
        Returns the LED brightness in percent
    setLedBrightness(led_brightness)
        Sets the LED brightness in percent of both LEDs before and after the
        mask
    getCalibrationValue()
        Returns the calibration value
    setCalibrationValue(calibration_value)
        Sets the calibration value
    readDiodeVoltage()
        Read the analog voltage values of the photo transistor conneceted to
        the analog inputs of the arduino
    liveMeasurement(measurement_duration)
        Starts a measurement and plots the measurement values live into a
        figure
    plotMeasurement(measurement_time,diode_voltage,turbidity,turbidity_ratio)
        Plots the measurement values
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
    saveData(diode_voltage,turbidity,turbidity_ratio,measurement_time)
        Saves the measurement values into a .csv file and the measurement plot
        into .pdf file
    readCSVData(file_name)
        Reads an existing .csv file containing measurement data   
    makeListOfCsvRow(row)
        Creates a list of a string read from .csv file
    """
    
    def __init__(self,led_state = 1,led_brightness = 100,
                 calibration_value = [0.000,0.000],
                 serial_port = '/dev/cu.usbserial-14130',baud_rate = 9600,):
        """
        Parameters
        ----------
        led_state : int
            1 --> LED On, 0 --> LED Off (default 1)
        led_brightness : int
            defines the LED brightness in percent (default 100)
        calibration_value : float
            offset value of the turbidity before and after the mask
            (default [0,0])
        serial_port : str
            serial port of the arduino
        baud_rate : int
            baud rate of the serial port communication (default 9600)
        """
        
        self.__led_state = led_state
        self.__led_brightness = led_brightness
        self.__calibration_value = calibration_value
        self.__serial_port = serial_port
        self.__baud_rate = baud_rate
        self.__arduino = self.initSerial()
        self.setLedState(led_state,'Before')
        self.setLedState(led_state,'After')
        self.setLedBrightness(led_brightness)
              
    def initSerial(self):
        """Initializes the serial communication to the arduino
        
        Returns
        -------
        self.__arduino : serial object
            Serial object of the arduino     
        """
        
        self.__arduino = serial.Serial(self.__serial_port,self.__baud_rate)
        return self.__arduino
    
    def closeSerial(self):
        """Closes the serial communication to the arduino
        """
        
        self.__arduino.close()
        
    def getLedState(self):
        """Returns the state (On/Off) of the LED
        
        Returns
        -------
        self.__led_state : int
            1 --> LED On, 0 --> LED Off (default 1)
        """
        
        if self.__led_state:
            print("LED On")
        else:
            print("LED Off")    
        return self.__led_state
    
    def setLedState(self,led_state,led_position):
        """Sets the led state (On/Off) of the LED before or after the mask
        
        Parameters
        ----------
        led_state : int
            1 --> LED On, 0 --> LED Off (default 1)
        led_position : str
            'Before' --> LED before mask, 'After' --> LED after mask 
        """
        
        outgoing_string = 'LED_' + led_position + '_' + str(led_state)
        self.__arduino.write(outgoing_string.encode())
        print_text = self.__arduino.readline().decode()
        print(print_text.strip())
        self.__led_state = led_state
        
    def getLedBrightness(self):
        """Returns the LED brightness in percent
        
        Returns
        -------
        self.__led_brightness : int
            Defines the LED brightness in percent (default 100)
        """
        
        print("LED brightness: " + str(self.__led_brightness) + "%")
        return self.__led_brightness
    
    def setLedBrightness(self,led_brightness):
        """Sets the LED brightness in percent of both LEDs before and after the
        mask
           
        Parameters
        ----------
        led_brightness : int
            Defines the LED brightness in percent (default 100)
        """
        
        # Convert LED brightness from perscent to an int value between 0 to 254
        outgoing_string = 'BRIGHTNESS' + str(254*led_brightness/100)
        self.__arduino.write(outgoing_string.encode())
        print_text = self.__arduino.readline().decode()
        print_text = print_text.strip()
        print_text = round(int(print_text)*100/254)
        print_text = str(print_text)
        print("LED brightness: " + print_text + "%")
        self.__led_brightness = led_brightness
        
    def getCalibrationValue(self):
        """Returns the calibration value
        
        Returns
        -------
        calibration_value : float
            offset value of the turbidity before and after the mask
            (default [0,0])            
        """
        
        calibration_value = self.__calibration_value
        return calibration_value

    def setCalibrationValue(self,calibration_value):
        """Sets the calibration value
        
        Parameters
        ----------
        calibration_value : float
            offset value of the turbidity before and after the mask
            (default [0,0])
        """
        
        self.__calibration_value = calibration_value
        
    def readDiodeVoltage(self):
        """Read the analog voltage values of the photo transistor conneceted to
        the analog inputs of the arduino
        
        Returns
        -------
        diode_voltage : float
            Voltage values in volts of the photo transistors in order:
            [Before90° Before180° After90° After180°]        
        """
        
        outgoing_string = "READ_DIODE"
        self.__arduino.write(outgoing_string.encode())
        diode_voltage = self.__arduino.readline().decode()
        # Voltage values are split by ';', use .float_ to convert list
        diode_voltage = list(np.float_(diode_voltage.split(';')))
        return diode_voltage
    
    def liveMeasurement(self,measurement_duration):
        """Starts a measurement and plots the measurement values live into a
        figure
        
        Measurement can be interrupted by triggering a KeyboardInterrupt.
        
        Parameters
        ----------
        measurement_duration : int
            Duration time of the measurement in seconds
            
        Returns
        -------
        diode_voltage : float
            Voltage values in volts of the photo transistors in order:
            [Before90° Before180° After90° After180°]
        turbidity : float
            Turbidity value (90°signal/180°signal) before and after the mask in
            order: [Before After]
        turbidity_ratio : float
            Ratio beteween the turbidity before and after the mask
        measurement_time : float
            Measurement time in seconds
        """
        
        diode_voltage = []
        turbidity = []
        turbidity_ratio = []
        measurement_time = []
        t = time.time()
        elapsed_time = 0
        print("Measurement started...")
        # Try until KeybordInterrupt
        try: 
            while elapsed_time < measurement_duration:
                diode_voltage.append(self.readDiodeVoltage())
                # Use diode_voltage[-1] to use only the latest voltage value
                turbidity.append(self.calculateTurbidity(diode_voltage[-1]))
                # Use turbidity[-1] to use only the latest turbidity value
                turbidity_ratio.append(self.calculateTurbidityRatio(
                        turbidity[-1]))
                # Sleep for stability
                time.sleep(0.1)
                elapsed_time = time.time() - t
                measurement_time = list(np.round_(np.linspace(0,elapsed_time,
                                                    len(diode_voltage)),1))
                self.plotMeasurement(measurement_time,diode_voltage,turbidity,
                                     turbidity_ratio)
         # Stop manually before end of measurement duration
        except KeyboardInterrupt:
            # Sleep for stability
            time.sleep(0.1)
            print("Measurement interrupted.")
        # Plot again to ensure the plot is shown in case of manual interruption
        finally: 
            diode_voltage.append(self.readDiodeVoltage())
            # Use diode_voltage[-1] to use only the latest voltage value
            turbidity.append(self.calculateTurbidity(diode_voltage[-1]))
            # Use turbidity[-1] to use only the latest turbidity value
            turbidity_ratio.append(self.calculateTurbidityRatio(
                        turbidity[-1]))
            # Sleep for stability
            time.sleep(0.1)
            elapsed_time = round(time.time() - t,2)
            measurement_time = list(np.round_(np.linspace(0,elapsed_time,
                                                len(diode_voltage)),1))
            self.plotMeasurement(measurement_time,diode_voltage,turbidity,
                                     turbidity_ratio)
            print("Measurement finished.")
        return diode_voltage,turbidity,turbidity_ratio,measurement_time
    
    def plotMeasurement(self,measurement_time,diode_voltage,turbidity,
                        turbidity_ratio):
        """Plots the measurement values
        
        Parameters
        ----------
        diode_voltage : float
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
        
        plt.ion() # Enable plot live update
        plt.clf() # Clear old plot
        plt.subplot(211)
        plt.plot(measurement_time,diode_voltage,'o-')
        plt.grid(True)
        plt.title("Photo transistor voltage")
        plt.xlabel("Time in s")
        plt.ylabel("Photo transistor voltage in V")
        plt.legend(["Before 90°","Before 180°","After 90°","After 180°"])
        plt.subplot(212)
        plt.plot(measurement_time,turbidity,'o-')
        plt.plot(measurement_time,turbidity_ratio,'o-',)
        plt.grid(True)
        if self.__calibration_value == [0.000,0.000]:
            plt.title("Turbidity and turbidity ratio (before/after mask)")
            plt.ylabel("Turbidity, turbidity ratio")
        else:
            plt.title("Corrected turbidity and turbidity ratio " + 
                      "(before/after mask)")
            plt.ylabel("Corrected turbidity, turbidity ratio")
        plt.xlabel("Time in s")
        plt.legend(["Before","After","Ratio"])
        plt.draw_all()
        plt.pause(1e-3) # Some time to draw figure
        plt.tight_layout() # Neccessary to avoid overlaps of title and axis
        
    def calibrate(self,measurement_duration):
        """Measures the trurbidity offset values
        
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
        
        self.__calibration_value = [0.000,0.000]
        diode_voltage,turbidity,turbidity_ratio,measurement_time = \
                                    self.liveMeasurement(measurement_duration)
        # Calculate the mean turbidity before the mask over calibration time
        self.__calibration_value[0] = round(np.mean(
                [i[0] for i in turbidity]),3)
        # Calculate the mean turbidity after the mask over calibration time
        self.__calibration_value[1] = round(np.mean(
                [i[1] for i in turbidity]),3)
        return self.__calibration_value
    
    def calculateTurbidity(self,diode_voltage):
        """Calculates the turbidity values before and after the mask
        
        Parameters
        ----------
        diode_voltage : float
            Voltage values in volts of the photo transistors in order:
            [Before90° Before180° After90° After180°]
            
        Returns
        -------
        turbidity : float
            Turbidity value (90°signal/180°signal) before and after the mask in
            order: [Before After]
        """
        
        turbidity = [0.000,0.000]
        # Correct the turbidity value before the mask by the calibration offset
        turbidity[0] = round(diode_voltage[0]/diode_voltage[1] - 
                 self.__calibration_value[0],3)
        # Correct the turbidity value after the mask by the calibration offset
        turbidity[1] = round(diode_voltage[2]/diode_voltage[3] - 
                 self.__calibration_value[1],3)
        if turbidity[0] < 0:
            turbidity[0] = 0.000
        elif turbidity [1] < 0:
            turbidity[1] = 0.000
        return turbidity
    
    def calculateTurbidityRatio(self,turbidity):
        """Calculates the turbidity ratio of the turbidity before and after the
        mask
        
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
            turbidity_ratio = round(turbidity[1]/turbidity[0],3)
        return turbidity_ratio
    
    def integrateTurbidity(self,turbidity,measurement_time):
        """Integrates the turbidity values before and after the sample over
        time
        
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
        
        total_turbidity = [0.000,0.000]
        total_turbidity[0] = round(np.trapz([i[0] for i in turbidity],
                       measurement_time),3)
        total_turbidity[1] = round(np.trapz([i[1] for i in turbidity],
                       measurement_time),3)
        return total_turbidity
    
    def calculateTotalTurbidityRatio(self,total_turbidity):
        """Calculates the ratio of the total turbidities before and after the
        sample
        
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
        total_turbidity_ratio = round(total_turbidity[1]/total_turbidity[0],3)
        return total_turbidity_ratio
    
    def evaluateMeasurement(self,total_turbidity_ratio):
        """Calculates the filtered particle percentage of the sample
        
        Parameters
        ----------
        total_turbidity_ratio : float
            Ratio of the total, integrated trubidity values before and after
            the sample
            
        Returns
        -------
        filtered_percentage : int
            Filtered particle percentage of the sample
        """
        filtered_percentage = round((1.000 - total_turbidity_ratio)*100)
        return filtered_percentage
    
    def saveData(self,diode_voltage,turbidity,turbidity_ratio,
                 measurement_time,calibration_value,total_turbidity,
                 total_turbidity_ratio,filtered_percentage):
        """Saves the measurement values into a .csv file and the measurement
        plot into .pdf file
        
        Parameters
        ----------
        diode_voltage : float
            Voltage values in volts of the photo transistors in order:
            [Before90° Before180° After90° After180°]
        turbidity : float
            Turbidity value (90°signal/180°signal) before and after the mask in
            order: [Before After]
        turbidity_ratio : float
            Ratio between the turbidity before and after the mask
        measurement_time : float
            Measurement time in seconds
        calibration_value : float
            offset value of the turbidity before and after the mask
            (default [0,0])
        total_turbidity : float
            Integrated turbidity values over time
        total_turbidity_ratio : float
            Ratio of the total, integrated trubidity values before and after
            the sample
        filtered_percentage : int
            Filtered particle percentage of the sample
            
        Raises
        ------
        NameError()
            If answer for overwrite is not 'y' or 'n'
        """
        
        data_name = input("Enter data name: ")
        print("Saving data in " + "Messungen/" + data_name + "/...")
        
        # create directory if doesn't exist, other ask if overwrite
        if not os.path.isdir("Messungen/" + data_name):
            os.mkdir("Messungen/" + data_name)
        elif os.path.isdir("Messungen/" + data_name):
            overwrite = input("Directory already exists, overwrite " + 
                              "it? (y/n)")
            if overwrite == 'y':
                pass
            elif overwrite == 'n':
                print("Enter new name.")
                # Recursion for saving with new name
                self.saveData(diode_voltage,turbidity,turbidity_ratio,
                              measurement_time)
                return
            elif overwrite != 'y' or overwrite != 'n':
                raise NameError()
        plt.savefig("Messungen/" + data_name + "/" + data_name + ".pdf")
        
        # Save data as .csv
        with open("Messungen/" + data_name + "/" + data_name +  ".csv",'w')as\
        data:
            wr = csv.writer(data,quoting = csv.QUOTE_ALL)
            wr.writerow(["Data name: ",data_name])
            wr.writerow(["Created on: ",str(date.today())])
            wr.writerow(["Calibration value: ",str(calibration_value)])
            wr.writerow(["Total turbidity: ",str(total_turbidity)])
            wr.writerow(["Total turbidity ratio: ",str(total_turbidity_ratio)])
            wr.writerow(["Filtered percentage: ",str(filtered_percentage)])
            wr.writerow(" ")
            wr.writerow(["Measurement time in s","Diode voltage in V",
                         "Turbidity","Turbidity ratio"])
            for (i,j,k,l) in zip(measurement_time,diode_voltage,turbidity,
                turbidity_ratio):
                wr.writerow([i,j,k,l])
        print("Saving complete!")
        
    def readCSVData(self,file_name):
        """Reads an existing .csv file containing measurement data
        
        Parameters
        ----------
        file_name : str
            Name of the file to read inclusive complete file path, for example:
            'Messungen/Test/Test.csv'
            
        Returns
        -------
        diode_voltage : float
            Voltage values in volts of the photo transistors in order:
            [Before90° Before180° After90° After180°]
        turbidity : float
            Turbidity value (90°signal/180°signal) before and after the mask in
            order: [Before After]
        turbidity_ratio : float
            Ratio between the turbidity before and after the mask
        measurement_time : float
            Measurement time in second
        calibration_value : float
            offset value of the turbidity before and after the mask
            (default [0,0])
        total_turbidity : float
            Integrated turbidity values over time
        total_turbidity_ratio : float
            Ratio of the total, integrated trubidity values before and after
            the sample
        filtered_percentage : int
            Filtered particle percentage of the sample
            
        Raises
        ------
        TypeError()
            Error if parameter is not a string
        """
        
        diode_voltage = []
        turbidity = []
        turbidity_ratio = []
        measurement_time = []
        if not isinstance(file_name,str):
            raise TypeError("Must be a string")
        with open(file_name) as csvFile:
            read = csv.reader(csvFile,csv.QUOTE_NONNUMERIC)
            line_count = 0
            for row in read:
                if line_count < 2:
                    print(row)
                    line_count += 1
                elif line_count == 2:
                    calibration_value = self.makeListOfCsvRow(row[1])
                    line_count += 1
                elif line_count == 3:
                    total_turbidity = self.makeListOfCsvRow(row[1])
                    line_count += 1
                elif line_count == 4:
                    total_turbidity_ratio = self.makeListOfCsvRow(row[1])
                    line_count += 1
                elif line_count == 5:
                    filtered_percentage = self.makeListOfCsvRow(row[1])
                    line_count += 1
                elif line_count > 7:
                    measurement_time.append(float(row[0]))
                    diode_voltage.append(self.makeListOfCsvRow(row[1]))
                    turbidity.append(self.makeListOfCsvRow(row[2]))
                    turbidity_ratio.append(float(row[3]))             
                    line_count += 1
                else:
                    continue
                             
        return measurement_time,diode_voltage,turbidity,turbidity_ratio,\
                calibration_value,total_turbidity,total_turbidity_ratio,\
                filtered_percentage
    
    def makeListOfCsvRow(self,row):
        """Creates a list of a string read from .csv file
        
        Parameters
        ----------
        row : str
            Part of row string read from .csv file. For example the diode
            voltage string '[0.323, 2.563, 0.562, 3.564]'
            
        Returns
        -------
        row : float
            The row string as a list: [0.323, 2.563, 0.562, 3.564]
        """
        
        row = row.replace('[','')
        row = row.replace(']','')
        row = row.split(',')
        return list(np.float_(row))