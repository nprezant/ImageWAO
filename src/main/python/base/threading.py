
import sys
import traceback
from enum import Enum
from multiprocessing import Process, Queue

from PySide2 import QtCore

class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    progress
        `int` indicating % progress
    '''

    finished = QtCore.Signal()
    error = QtCore.Signal(tuple)
    result = QtCore.Signal(object)
    progress = QtCore.Signal(int)

class QWorker(QtCore.QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''

    def __init__(self, fn, args:list, kwargs:dict={}, progress=False):
        super().__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
        # If progress is true, we need to include the progress
        # Signal in the keyword arguments
        if progress is True:
            self.kwargs.update(progress=self.signals.progress)

    @QtCore.Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


# Runner lives on the runner thread

class SignalType(Enum):
    Progress = 1
    Finished = 2
    Result = 3

class RunnerMessage:

    Result = SignalType.Result
    Progress = SignalType.Progress
    Finished = SignalType.Finished

    def __init__(self, t:SignalType, data):
        self.t = t
        self.data = data

class Runner(QtCore.QObject):
    '''
    Runs a job in a separate process and forwards messages from the job to the
    main thread through a Signal.

    The job should accept a python multiprocessing Queue as the first
    parameter, and use that Queue to post messages to be signaled out.
    The Queue messages should be of type RunnerMessage()

    The job must post a message to the Queue noting when it is finished
    with the Result or Finished.
    '''

    finished = QtCore.Signal()
    progress = QtCore.Signal(int)
    result = QtCore.Signal(object)

    def __init__(self, jobFunction, startSignal, *inputs):
        '''
        :param start_signal: the Signal that starts the job
        '''
        super().__init__()
        self.jobFunction = jobFunction
        self.jobInputs = inputs

    def _run(self):
        q = Queue()
        try:
            p = Process(target=self.jobFunction, args=(q, *self.jobInputs))
        except Exception as e:
            print(e)
        p.start()
        while True:

            # block until a new item is posted to the Queue
            msg = q.get()

            if not isinstance(msg, RunnerMessage):
                print('Could not decipher runner message!')
                break

            if msg.t == SignalType.Progress:
                self.progress.emit(msg.data)

            elif msg.t == SignalType.Result:
                self.result.emit(msg.data)
                self.finished.emit()
                break

            elif msg.t == SignalType.Finished:
                self.finished.emit()
                break


# # # Things below live on the main thread

# # def run_job(input):
# #     ''' Call this to start a new job '''
# #     runner.job_input = input
# #     runner_thread.start()


# # def handle_msg(msg):
# #     print(msg)
# #     if msg == 'done':
# #         runner_thread.quit()
# #         runner_thread.wait()


# # # Setup the OQ listener thread and move the OQ runner object to it
# # runner_thread = QtCore.QThread()
# # runner = Runner(start_signal=runner_thread.started)
# # runner.msg_from_job.connect(handle_msg)
# # runner.moveToThread(runner_thread)
