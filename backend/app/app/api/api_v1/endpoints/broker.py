import math
import pika
import threading
import logging
import time
from fastapi import APIRouter
from app.schemas import SinusoidalParameters

router = APIRouter()
background_task = None

class BackgroundTasks(threading.Thread):
    def __init__(self, amplitude, frequency, phase):
        super().__init__()
        self._stop_threads = False
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase
        self.connection = None
        self.channel = None

    def run(self):
        try:
            # Connect to RabbitMQ server
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='my_queue')

            while not self._stop_threads:
                try:
                    value = self.amplitude * math.sin(self.frequency * time.time() + self.phase)
                    message = str(value)
                    # Publish the message
                    self.channel.basic_publish(exchange='', routing_key='my_queue', body=message)
                    print("Message published:", message)
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
def start_task(msg: SinusoidalParameters):
    """
    Start the task.
    """
    global background_task
    background_task = BackgroundTasks(msg.amplitude, msg.frequency, msg.phase)
    background_task.start()
    return {"msg": "Task started"}

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