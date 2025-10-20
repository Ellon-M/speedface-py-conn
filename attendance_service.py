import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import sys
import os
import logging
from datetime import datetime

# Add the application directory to Python path
sys.path.append('C:\\Users\\Admin\\Documents\\pyzk_tests')

from main_continuous import AttendanceSystem

class AttendanceWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AttendanceSystem"
    _svc_display_name_ = "Attendance System Service"
    _svc_description_ = "Real-time attendance synchronization from HikVision and ZKTeco devices"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.attendance_system = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.attendance_system:
            self.attendance_system.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        # Set up logging to Windows Event Log
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('C:\\Users\\Admin\\Documents\\pyzk_tests\\logs\\attendance_service.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AttendanceService')
        
        try:
            self.logger.info("Starting Attendance System Service")
            self.attendance_system = AttendanceSystem()
            self.attendance_system.run_continuous()
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            servicemanager.LogErrorMsg(f"Attendance Service error: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AttendanceWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AttendanceWindowsService)