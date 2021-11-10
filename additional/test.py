import pandas as pd
import dataframe_image as dfi

df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': ['A', 'B', 'C', 'D']})
s = '23423234'
dfi.export(df, 'dataframe.png')
