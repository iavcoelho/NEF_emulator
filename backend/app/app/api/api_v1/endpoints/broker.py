import math
import pika
import threading
import logging
import time
from fastapi import APIRouter, UploadFile, File
from app.schemas import SinusoidalParameters
import ast  # Import the ast module
from .qosMonitoring import signal_param_change

router = APIRouter()
background_task = None

class BackgroundTasks(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop_threads = False
        self.amplitude = 10  # Default value
        self.frequency = 0.2  # Default value
        self.phase = 2  # Default value
        self.custom_function = None  # Variable to store the custom function
        self.connection = None
        self.channel = None

    def update_values(self, amplitude, frequency, phase):
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase
        self.custom_function = None

    def execute_custom_function_from_file_content(self, file_content):

        # Parse the file content into an Abstract Syntax Tree (AST)
        parsed_ast = ast.parse(file_content)

        # Find the first function definition in the AST
        custom_function_name = None
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.FunctionDef):
                custom_function_name = node.name
                break

        # Check if a function definition was found
        if custom_function_name is None:
            raise ValueError("No valid function found in the file.")

        # Create a dictionary to hold the global variables for exec()
        global_vars = {}

        # Execute the custom function and get the generated values
        exec(file_content, global_vars)
        self.custom_function = global_vars[custom_function_name]


    def run(self):
        try:
            # Connect to RabbitMQ server
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='my_queue')

            while not self._stop_threads:
                try:
                    if self.custom_function is not None:
                        # Use the custom function to generate numbers
                        values = self.custom_function()
                    else:
                        # Use the default sinusoidal function to generate numbers
                        values = []
                        for i in range(10):
                            value = self.amplitude * math.sin(self.frequency * i + self.phase)
                            values.append(value)

                    # Publish the generated values to the RabbitMQ queue
                    for value in values:
                        message = str(value)
                        self.channel.basic_publish(exchange='', routing_key='my_queue', body=message)
                        # print("Message published:", message)

                except pika.exceptions.AMQPConnectionError:
                    print("Failed to publish message")

                time.sleep(1)

        except Exception as ex:
            logging.critical(ex)

        finally:
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()

    def stop(self):
        self._stop_threads = True

@router.post("/start", status_code=200)
def start_task():
    """
    Start the task.
    """
    global background_task

    # Create a new instance of BackgroundTasks if it doesn't exist
    if background_task is None:
        background_task = BackgroundTasks()

    # Start the background task
    background_task.start()
    return {"msg": "Task started"}

@router.post("/upload_file")
async def upload_custom_function_file(file: UploadFile = File(...)):
    global background_task

    # Read the content of the uploaded file
    file_content = await file.read()

    # Update the function used for generating numbers with the custom function from the file content
    background_task.execute_custom_function_from_file_content(file_content)

    return {"msg": "Read file done"}

@router.post("/update_sinusoidal_parameters")
async def update_sin_function_parameters(msg: SinusoidalParameters):
    global background_task

    if background_task is None:
        return {"msg": "Task is not running. Please start the task first."}

    # Update the parameters in the background task
    background_task.update_values(msg.amplitude, msg.frequency, msg.phase)
    return {"msg": "Parameters updated successfully."}


@router.post("/stop", status_code=200)
def stop_task():
    """
    Stop the task.
    """
    global background_task
    if background_task is not None:
        background_task.stop()
        background_task.join()
        background_task = None
        return {"msg": "Task stopped"}
    else:
        return {"msg": "No task is running"}


@router.post("/trigger_qos", status_code=200)
def trigger_qos(param: str):
    """
    Signals the qos function.
    """
    signal_param_change(True, param)

@router.post("/stop_qos", status_code=200)
def stop_qos():
    """
    Signals the qos function.
    """
    signal_param_change(False, "")
