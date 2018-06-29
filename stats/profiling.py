import pyprof2calltree
import cProfile
from pyprof2calltree import convert, visualize
sys.path.append('./')
from src.philter.philter import Philter

pr = cProfile.Profile()
pr.enable()


pr.disable()

pr.print_stats(sort='time')