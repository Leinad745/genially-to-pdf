from enum import Enum

class TaskStatus(str, Enum):
    QUEUED = 'queued'
    CAPTURING_SLIDES = 'capturing_slides'
    CONVERTING_TO_PDF = 'converting_to_pdf'
    FINISHED = 'finished'
    ERROR = 'error'