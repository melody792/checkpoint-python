import pandas as pd
import numpy as np
from numpy import nan as NaN
df1=pd.DataFrame([[1,2,3],[NaN,NaN,2],[NaN,NaN,NaN],[8,8,NaN]])

print(df1)
df1.dropna(subset=[1], axis=0)
print(df1)
