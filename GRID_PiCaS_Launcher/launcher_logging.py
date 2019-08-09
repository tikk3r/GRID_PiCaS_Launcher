import logging
import GRID_PiCaS_Launcher

LOG_FILE = "{0}/GRID_PiCaS_Launcher.log".format(
                    GRID_PiCaS_Launcher.__file__.split("__init__")[0])
logging.basicConfig(filename=LOG_FILE, filemode='w+', level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

