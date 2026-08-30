import numpy as np

# ========================================
# INPUTS
# ========================================

Wpayload = 15       # kg


#Empty fraction
a=0.589 # RAYMER (mks) UAV jet
C=-0.05
W0_assumed=100

We_W0 = a*W0_assumed**C      # ASSUMED EMPTY FRACTION

# Mission parameters
LD = 8
E = 1.5           # h
TSFC = 1.2        # 1/h

# Segment weight ratios
W1_W0 = 0.97
W2_W1 = 0.985
W5_W4 = 0.995

reserve_factor = 1.06

# ========================================
# LOITER (BREGUET)
# ========================================

W4_W3 = np.exp(-(E * TSFC)/(LD))

# ========================================
# MISSION WEIGHT FRACTION
# ========================================

Wx_W0 = W1_W0 * W2_W1 * W4_W3 * W5_W4

# ========================================
# FUEL FRACTION
# ========================================

Wf_W0 = reserve_factor*(1 - Wx_W0)

# ========================================
# DIRECT MTOW CALCULATION
# ========================================

W0 = (Wpayload) / (1 - Wf_W0 - We_W0)

We = We_W0 * W0
Wf = Wf_W0 * W0

# ========================================
# RESULTS
# ========================================

print("========= UAV SIZING =========")
print(f"MTOW (W0):      {W0:.2f} kg")
print(f"Empty weight:   {We:.2f} kg")
print(f"Fuel weight:    {Wf:.2f} kg")
print(f"Payload:        {Wpayload:.2f} kg")

print("\nFractions:")
print(f"We/W0 = {We_W0:.3f}")
print(f"Wf/W0 = {Wf_W0:.3f}")



