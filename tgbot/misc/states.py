from os import link
from aiogram.dispatcher.filters.state import StatesGroup, State

class Message(StatesGroup):
    message = State()
    
class Link(StatesGroup):
    link = State()