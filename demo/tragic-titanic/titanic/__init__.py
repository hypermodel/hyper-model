import warnings
import logging
import sys
sys.path.append('C:\\Amit\\hypermodel\\hyper-model\\src\\hyper-model')

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

# Kill the annoying Google warnings
warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")
