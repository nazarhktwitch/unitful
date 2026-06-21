"""Physical constants with units"""

from __future__ import annotations

import math

from .units import A, K, kg, m, mol, s

# Speed of light in vacuum
c = 299792458 * (m / s)

# Newtonian constant of gravitation
G = 6.67430e-11 * (m**3 / (kg * s**2))

# Planck constant
h = 6.62607015e-34 * (kg * m**2 / s)
hbar = h / (2 * math.pi)

# Elementary charge
e = 1.602176634e-19 * (A * s)

# Electron mass
m_e = 9.1093837015e-31 * kg

# Proton mass
m_p = 1.67262192369e-27 * kg

# Boltzmann constant
k_B = 1.380649e-23 * (kg * m**2 / (s**2 * K))

# Avogadro constant
N_A = 6.02214076e23 * (1 / mol)

# Molar gas constant
R = N_A * k_B
