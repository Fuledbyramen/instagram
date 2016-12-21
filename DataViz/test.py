import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
from datetime import datetime
import psycopg2
from cycler import cycler
import scipy



week = {u : {k : [] for k in np.arange(0,24,0.5)} for u in range(7)}
print(week)


