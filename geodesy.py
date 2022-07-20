
import math
import numpy as np

# WGS84 ellipsoid Earth parameters
WGS84_A = 6378137.0
WGS84_F = 1.0/298.257223563
WGS84_B = WGS84_A * (1 - WGS84_F)
WGS84_ECC_SQ = 1 - WGS84_B * WGS84_B / (WGS84_A * WGS84_A)
WGS84_ECC = math.sqrt(WGS84_ECC_SQ)

# degrees to radians
DTOR = math.pi / 180.0
# radians to degrees
RTOD = 180.0 / math.pi

# Average radius for a spherical Earth
SPHERICAL_R = 6371e3

# Some derived values
_wgs84_ep = math.sqrt((WGS84_A**2 - WGS84_B**2) / WGS84_B**2)
_wgs84_ep2_b = _wgs84_ep**2 * WGS84_B
_wgs84_e2_a = WGS84_ECC_SQ * WGS84_A


def llh2ecef(llh):
    """Converts from WGS84 lat/lon/height to ellipsoid-earth ECEF"""

    lat = llh[0] * DTOR
    lng = llh[1] * DTOR
    alt = llh[2]

    slat = math.sin(lat)
    slng = math.sin(lng)
    clat = math.cos(lat)
    clng = math.cos(lng)

    d = math.sqrt(1 - (slat * slat * WGS84_ECC_SQ))
    rn = WGS84_A / d

    x = (rn + alt) * clat * clng
    y = (rn + alt) * clat * slng
    z = (rn * (1 - WGS84_ECC_SQ) + alt) * slat

    return (x, y, z)


def ecef2llh(ecef):
    "Converts from ECEF to WGS84 lat/lon/height"

    x, y, z = ecef

    lon = math.atan2(y, x)

    p = math.sqrt(x**2 + y**2)
    th = math.atan2(WGS84_A * z, WGS84_B * p)
    lat = math.atan2(z + _wgs84_ep2_b * math.sin(th)**3,
                     p - _wgs84_e2_a * math.cos(th)**3)

    N = WGS84_A / math.sqrt(1 - WGS84_ECC_SQ * math.sin(lat)**2)
    alt = p / math.cos(lat) - N

    return (lat * RTOD, lon * RTOD, alt)


def greatcircle(p0, p1):
    """Returns a great-circle distance in metres between two LLH points,
    _assuming spherical earth_ and _ignoring altitude_. Don't use this if you
    need a distance accurate to better than 1%."""

    lat0 = p0[0] * DTOR
    lon0 = p0[1] * DTOR
    lat1 = p1[0] * DTOR
    lon1 = p1[1] * DTOR
    return SPHERICAL_R * math.acos(
        math.sin(lat0) * math.sin(lat1) +
        math.cos(lat0) * math.cos(lat1) * math.cos(abs(lon0 - lon1)))


# direct implementation here turns out to be _much_ faster (10-20x) compared to
# scipy.spatial.distance.euclidean or numpy-based approaches
def ecef_distance(p0, p1):
    """Returns the straight-line distance in metres between two ECEF points."""
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2 + (p0[2] - p1[2])**2)

def ECEF2ENU(x, y, z, x_0, y_0, z_0):
	lamda = np.arctan(y_0/x_0) 
	first_matrix = np.matrix([[x - x_0,y - y_0,z - z_0]])
	r = math.sqrt(math.pow(x, 2.0) + math.pow(y, 2.0) + math.pow(z, 2.0))
	phi = np.arcsin(z/r)
	cos_lamda = math.cos(lamda)
	sin_lamda = math.sin(lamda)
	cos_phi = math.cos(phi)
	sin_phi = math.sin(phi)	
	second_matrix = np.matrix([[-sin_lamda, cos_lamda, 0], 
			[-sin_phi*cos_lamda, -sin_phi*sin_lamda, cos_phi],
			[cos_phi * cos_lamda, cos_phi * sin_lamda, sin_phi ]])

	enu = first_matrix.dot(second_matrix)
	enu = (enu[0,0],enu[0,1],enu[0,2])
	return enu

def ENU2EA(enu):
    (e,n,u) = enu
    E = math.acos(math.sqrt((n**2+e**2)/(n**2+e**2+u**2)))
    A = math.atan(e/n)
    return (E * RTOD,A * RTOD)