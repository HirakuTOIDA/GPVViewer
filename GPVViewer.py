# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import geopy.distance
import sys
import os

args = sys.argv
if len(args) < 3:
    print("Usage: python " + args[0] + 'filename ' + 'time offset')
    exit()
filename = args[1]
filename.replace('/', os.sep)
hours_offset = args[2]

LATL = "34.8"
LATH = "35.8"
LONL = "135.6"
LONH = "136.6"

os.system("bin\wgrib2.exe " + filename + " -match \"VGRD\" -undefine out-box " + LONL + ":" + LONH + " " + LATL + ":" + LATH + " -csv " + filename + "_V.txt")
os.system("bin\wgrib2.exe " + filename + " -match \"UGRD\" -undefine out-box " + LONL + ":" + LONH + " " + LATL + ":" + LATH + " -csv " + filename + "_U.txt")
os.system("bin\wgrib2.exe " + filename + " -match \"PRMSL\" -undefine out-box " + LONL + ":" + LONH + " " + LATL + ":" + LATH + " -csv " + filename + "_P.txt")

## データ読み込み
# +uは西風、+vは南風
dat_V = np.loadtxt(filename + "_V.txt", delimiter = ',', usecols =(4, 5, 6))
dat_U = np.loadtxt(filename + "_U.txt", delimiter = ',', usecols =(4, 5, 6))
dat_P = np.loadtxt(filename + "_P.txt", delimiter = ',', usecols =(4, 5, 6))

polyline_Biwako = np.loadtxt("data/ext_biwako.txt", delimiter = ',')

# データ数の計算
num_x = (dat_V[-1,0]- dat_V[0,0]) / 0.0625 + 1
num_x = np.round(num_x)
num_y = (dat_V[-1,1]- dat_V[0,1]) / 0.05 + 1
num_y = np.round(num_y)

# アスペクト比の計算
y_meter = geopy.distance.great_circle(dat_V[-1,1], dat_V[0,1]).meters
x_meter = geopy.distance.great_circle(dat_V[-1,0], dat_V[0,0]).meters
ar = y_meter / x_meter

#　メッシュ作成
x = np.linspace(dat_V[0,0], dat_V[-1,0], num = num_x, endpoint=True)
y = np.linspace(dat_V[0,1], dat_V[-1,1], num = num_y, endpoint=True)
X, Y = np.meshgrid(x,y)

# データ初期化
data_V = np.zeros([len(y), len(x)])
data_U = np.zeros([len(y), len(x)])
data_P = np.zeros([len(y), len(x)])

hours_offset_index = len(x) * len(y) * int(hours_offset)

# 2次元配列作成
for y_i in range(len(y)):
    for x_i in range(len(x)):
        data_V[y_i, x_i] = dat_V[x_i + y_i * len(x) + hours_offset_index, 2]      
        data_U[y_i, x_i] = dat_U[x_i + y_i * len(x) + hours_offset_index, 2]      
        data_P[y_i, x_i] = dat_P[x_i + y_i * len(x) + hours_offset_index, 2]
data_C = np.sqrt(data_V ** 2 + data_U ** 2)

# Pa -> hPa
data_P /= 100

## プロット
fig = plt.figure(1, figsize=(12,12))
ax = fig.add_subplot(111)
ax.set_aspect(ar)

ax_q = plt.quiver(X, Y, data_U, data_V, data_C, pivot='mid', angles='uv',scale_units='xy',scale=50)
fig.colorbar(ax_q, ticks=np.arange(np.ceil(np.max(data_C)) + 1), label = "Wind speed of 10 m above ground (m/s)")
plt.clim([0, np.ceil(np.max(data_C))])

ax.scatter(X, Y, color='k', s=5)

ax.plot(polyline_Biwako[:,1], polyline_Biwako[:,0], 'k')

cax = ax.contour(X, Y, data_P, colors='k')
ax.clabel(cax, fmt='%2.2f', inline=False)

plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
ax.grid()
plt.title("!!! UTC !!!\n" + filename + '\n+' + hours_offset + " hours")
plt.savefig(filename + '_' + hours_offset + '.png', dpi=200)
plt.show()
