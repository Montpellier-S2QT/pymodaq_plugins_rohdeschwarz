import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins
from pymodaq_plugins_rohdeschwarz.hardware.NRP18E import NRP18E_wrapper


class DAQ_0DViewer_NRPx(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.

    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    Tested for NRP18E
    Should work with NRP8E as well
    Tested with PyMoDAQ 5.1.11 on Windows 11
    R&S NRP toolkit needs to be installed (drivers)


    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
    """
    params = comon_parameters + [
        {'title': 'Aperture:', 'name': 'aperture', 'type': 'float',
         'value': 10e-6},
        {'title': 'Averaging Count:', 'name': 'aver_count', 'type': 'list',
         'limits': [int(2**i) for i in range(17)]},
    ]

    def ini_attributes(self):
        self.controller: NRP18E_wrapper = None
        pass

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "aperture":
            self.controller.change_aperture(param.value())
        elif param.name() == "aver_count":
            self.controller.change_average_length(param.value())

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        if self.is_master:
            self.controller = NRP18E_wrapper()  # instantiate you driver with whatever arguments are needed
            initialized = self.controller.OpenCommunication()  # call eventual methods
        else:
            self.controller = controller
            initialized = True


        info = "Whatever info you want to log"
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.close_communication()

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        data_tot = np.array([self.controller.get_power()])
        self.dte_signal.emit(DataToExport(name='Power',
                                               data=[DataFromPlugins(name='power', data=[data_tot],
                                                                     dim='Data0D', labels=['Power'])]))

    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        return ''



if __name__ == '__main__':
    main(__file__)