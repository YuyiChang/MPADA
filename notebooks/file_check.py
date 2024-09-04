# %%
import pandas as pd

in_csv = '24502519319414-trace-mpada.csv'
df = pd.read_csv(in_csv)

# %%
import numpy as np
aa = df['data'].iloc[0][1:-1].split(' ')

bb = np.array([complex(a) for a in aa])

# %%
import numpy as np 

with open('4304032850060-mpada.npy', 'rb') as f:
    data = np.load(f, allow_pickle=True).item()

