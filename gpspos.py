# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  gpspos.py:  Calculate GPS satellite position with ephemeris                                                          +
#                                                                              +
#            Copyright (c) 2021.  by Y.Xie, All rights reserved.               +
#                                                                              +
#   references :                                                               +
#       [1] GPX The GNSS Time transformation https://www.gps.gov/technical/icwg/
#                                                                              +
#   version : $Revision:$ $Date:$                                              +
#   history : 26/11/2020, 12:25  1.0  new                                             +
#             26/01/2021, 16:57  1.1  modify                               +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from math import cos, sin, sqrt, atan, tan, pi
import numpy as np

def gpspos_ecef(eph, transmitTime):
    """
    calculate satellite position
    Based upon http://home-2.worldonline.nl/~samsvl/stdalone.pas
    This fills in the satpos element of the satinfo object
    """
    # WGS 84 value of earth's univ. grav. par.
    mu = 3.986005E+14
    # WGS 84 value of earth's rotation rate
    Wedot = 7.2921151467E-5

    # relativistic correction term constant
    F = -4.442807633E-10

    Crs = eph.Crs
    dn = eph.DeltaN
    M0 = eph.M0
    Cuc = eph.Cuc
    ec = eph.Eccentricity
    Cus = eph.Cus
    A = eph.sqrtA ** 2
    Toe = eph.Toe
    Cic = eph.Cic
    W0 = eph.Omega0
    Cis = eph.Cis
    i0 = eph.Io
    Crc = eph.Crc
    w = eph.omega
    Wdot = eph.OmegaDot
    idot = eph.IDOT

    T = transmitTime - Toe
    if T > 302400:
        T = T - 604800
    if T < -302400:
        T = T + 604800

    n0 = sqrt(mu / (A * A * A))
    n = n0 + dn

    M = M0 + n * T
    E = M
    for ii in range(20):
        Eold = E
        E = M + ec * sin(E)
        if abs(E - Eold) < 1.0e-12:
            break

    snu = sqrt(1 - ec * ec) * sin(E) / (1 - ec * cos(E))
    cnu = (cos(E) - ec) / (1 - ec * cos(E))
    if cnu == 0:
        nu = pi / 2 * snu / abs(snu)
    elif (snu == 0) and (cnu > 0):
        nu = 0
    elif (snu == 0) and (cnu < 0):
        nu = pi
    else:
        nu = atan(snu / cnu)
        if cnu < 0:
            nu += pi * snu / abs(snu)

    phi = nu + w

    du = Cuc * cos(2 * phi) + Cus * sin(2 * phi)
    dr = Crc * cos(2 * phi) + Crs * sin(2 * phi)
    di = Cic * cos(2 * phi) + Cis * sin(2 * phi)

    u = phi + du
    r = A * (1 - ec * cos(E)) + dr
    i = i0 + idot * T + di

    Xdash = r * cos(u)
    Ydash = r * sin(u)

    Wc = W0 + (Wdot - Wedot) * T - Wedot * Toe

    X = Xdash * cos(Wc) - Ydash * cos(i) * sin(Wc)
    Y = Xdash * sin(Wc) + Ydash * cos(i) * cos(Wc)
    Z = Ydash * sin(i)

    satpos = np.array([float(X), float(Y), float(Z)])

    return satpos


def correctPosition(satpos, time_of_flight):
    '''correct the satellite position for the time it took the message to get to the receiver'''
    from math import sin, cos

    # WGS-84 earth rotation rate
    We = 7.292115E-5

    alpha = time_of_flight * We
    X = satpos[0]
    Y = satpos[1]
    satpos[0] = X * cos(alpha) + Y * sin(alpha)
    satpos[1] = -X * sin(alpha) + Y * cos(alpha)
    return satpos


def gpspositionearthfixed_0(obs, t, omega_e_dot=7.2921151467e-5):
    # https://www.gps.gov/technical/icwg/
    # Page 101
    # Cuc, Cus, Crc, Crs, Cic, Cis  >> Correction coefficients
    # DeltaN                        >> Variation of mean angular velocity
    # M0                            >> Mean Anomaly
    # sqrtA                         >> Sqrt(semi-major axis)
    # e                             >> Eccentricity
    # Toe                           >> Time of ephemeris
    # Omega0                        >> Argument of perigee
    # Io                            >> Inclination
    # omega                         >> Right ascension
    # OmegaDot                      >> Rate of right ascension
    # IDOT                          >> Rate of inclination

    # WGS 84 value of the earth's gravitational constant for GPS user
    u = 3.986005e14  # (meters/sec)^3
    # WGS 84 value of the earth's rotation rate
    # omega_e_dot = 7.2921151467e-5  # (rad/sec)
    # Semi-major axis
    A = obs.sqrtA ** 2
    # Computed mean motion (rad/sec)
    n_0 = sqrt(u / (A ** 3))
    # Time from ephemeris reference epoch
    t_k = t - obs.Toe
    if t_k > 302400:
        t_k = t_k - 604800
    if t_k < -302400:
        t_k = t_k + 604800
    # Corrected mean motion
    n = n_0 + obs.DeltaN
    # Mean anomaly
    M_k = obs.M0 + n * t_k
    # Initial Value (radians)
    E_0 = M_k
    # efinedValue,minimumofthreeiterations,(j=1,2,3)
    global E_k
    E_j_minus_1 = E_0
    tol = 1e-5
    max_iter = 50
    for i in range(max_iter):
        E_j = E_j_minus_1 + (M_k - E_j_minus_1 + obs.Eccentricity * sin(E_j_minus_1)) / \
              (1 - obs.Eccentricity * cos(E_j_minus_1))
        E_k = E_j
        if abs(E_j - E_j_minus_1) < tol:
            break
        E_j_minus_1 = E_j
    # True Anomaly (unambiguous quadrant)
    v_k = 2 * atan(sqrt((1 + obs.Eccentricity) / (1 - obs.Eccentricity)) * tan(E_k / 2))

    # Argument of Latitude
    phi_k = v_k + obs.omega
    # Radius Correction
    delta_u_k = obs.Cus * sin(2 * phi_k) + obs.Cuc * cos(2 * phi_k)
    delta_r_k = obs.Crs * sin(2 * phi_k) + obs.Crc * cos(2 * phi_k)
    delta_i_k = obs.Cis * sin(2 * phi_k) + obs.Cic * cos(2 * phi_k)
    # Corrected Argument of Latitude
    u_k = phi_k + delta_u_k
    # Corrected Radius
    r_k = A * (1 - obs.Eccentricity * cos(E_k)) + delta_r_k
    # Corrected Inclination
    i_k = obs.Io + delta_i_k + obs.IDOT * t_k
    # Position in orbital
    x_k_1 = r_k * cos(u_k)
    y_k_1 = r_k * sin(u_k)
    # Corrected longitude of ascending node
    omega_k = obs.Omega0 + (obs.OmegaDot - omega_e_dot) * t_k - omega_e_dot * obs.Toe
    # Earth-fixed Position
    x_k = x_k_1 * cos(omega_k) - y_k_1 * cos(i_k) * sin(omega_k)
    y_k = x_k_1 * sin(omega_k) + y_k_1 * cos(i_k) * cos(omega_k)
    z_k = y_k_1 * sin(i_k)

    position = np.array([float(x_k), float(y_k), float(z_k)])
    return position
    # print('Position in Earth-fixed coordinate:')
    # print('x:', float(x_k))
    # print('y:', float(y_k))
    # print('z:', float(z_k), '\n')
