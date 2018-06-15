#from idleiss.universe import Universe
#from idleiss.ship import ShipLibrary
from idleiss.core import GameEngine

# all calls from Interpreter should be to idleiss.core.GameEngine
# an external program which imports idleiss should also only make calls to GameEngine

class Interpreter(object):
    def __init__(self, universe_filename, library_filename):
        self.engine = GameEngine(universe_filename, library_filename)
    
    def run(self):
        pass
        