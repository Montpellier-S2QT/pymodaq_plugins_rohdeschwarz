import pyvisa as visa

from typing import Optional
from math import fabs, log10


class NRP18E_wrapper():
    """
    Wrapper hevily inspired by the example from NRP-Toolkit:
    https://www.rohde-schwarz.com/us/applications/rs-matlab-toolkit-for-rs-nrp-z-sensors_56280-15447.html
    """
    def __init__(self):
        self.sensor = None

    def OpenCommunication(self) -> Optional[visa.Resource]:
        rm = visa.ResourceManager()
        resources = list(rm.list_resources())

        for s in resources:

            # NRPE18 sensor has a USB Product ID of '0x0195'
            # NRPE18 sensor has a USB Product ID of '0x02C9'
            # that's how we'll detect the detector
            # We don't handle several detectors being connected
            if (-1 != s.find("0x02CA")) or (-1 != s.find("0x02C9")):

                print("\nOpening NRPM3 sensor '" + s + "'...")

                self.sensor = rm.open_resource(s)

                if self.sensor != None:
                    self.sensor.timeout = 20000

                    # Setting Aperture Time
                    self.sensor.write("sens:pow:avg:aper 10e-6")

                    # Select free running measurement (un-triggered)
                    self.sensor.write("trig:sour imm")

                    print("Querying *IDN?...")
                    print(self.sensor.query("*idn?"))

                    # Select manual averaging. Otherwise, if auto-
                    # averaging is used (which is ON by default) and
                    # no RF signal has been connected, the sensor will
                    # do a rather long measurement
                    self.sensor.write("SENS:AVER:COUN:AUTO OFF")
                    self.sensor.write("SENS:AVER:COUN 4")
                    self.sensor.write("SENS:AVER:STAT ON")

                    print("SYST:ERR?  --> " + self.sensor.query("SYST:ERR?"))
                    print("SYST:SERR? --> " + self.sensor.query("SYST:SERR?"))

                    return True
                    break

        return False

    def close_communication(self):
        self.sensor.close()

    def get_power(self):
        self.sensor.write("init:imm")
        power_watt = self.sensor.query("fetch?")
        power_dBm = Watt2dBm(float(power_watt))
        return power_dBm

    def change_aperture(self, aperture):
        self.sensor.write(f"sens:pow:avg:aper {aperture:.0e}")

    def change_average_length(self, aver_counts):
        self.sensor.write(f"SENS:AVER:COUN {aver_counts:.0f}")
def Watt2dBm( dW ) -> float:
    if fabs( dW ) < 1.0e-19:
        return -160.0

    return 10.0 * log10( fabs( dW ) ) + 30.0