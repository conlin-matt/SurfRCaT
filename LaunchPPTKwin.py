# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 13:09:17 2019

@author: conli
"""

import pickle
import pptk
import sys
import time
import numpy as np

f = open('lidarPC.pkl','rb')
pc = pickle.load(f)
v = pptk.viewer(pc,pc.iloc[:,2])
v.set(point_size=0.1,theta=-25,phi=0,lookat=[0,0,20],color_map_scale=[-1,3],r=0)

aa = np.empty([0,1])
while 1<2: # Continuously test to see if viewer window is open #
    try:
        test = v.get('curr_attribute_id')
        a = v.get('selected')
        if a:
            a = int(a)
        else:
            a = 0
        aa = np.vstack([aa,a])
        del a
        time.sleep(.5)
    except ConnectionRefusedError:
        break
    
##    a = v.get('selected')
##    sys.stdout = open('Testing.txt', 'w')
##    print(a)
##    time.sleep(1)

aa = aa[np.nonzero(aa)]
au = []
for i in aa:
    if int(i) not in au:
        au.append(int(i))
    else:
        pass

sys.stdout = open('Testing.txt', 'w')
print(au)
exit()


        


