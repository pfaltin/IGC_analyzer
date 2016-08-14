# Great Circle math
# ulazni parametri su koordinate dvije tocke
#daljina = GCdist(latr1,lonr1,latr2,lonr2)
#kut = GCbearing(latr1,lonr1,latr2,lonr2)
#s_tocka = GCmid(latr1,lonr1,latr2,lonr2)
#latM3 = s_tocka[0]
#lonM3 = s_tocka[1]

#print('Udaljenost je:{0:.2f}'.format(daljina) )
#print('Kurs je :{0:.2f}'.format(kut))
#print('Srednja tocka je {0:.2f} N i {1:.2f}E'.format(latM3, lonM3))


import math

R = 6371


def GCdist(latd1,lond1,latd2,lond2):
	lat1 = math.radians(latd1)
	lon1 = math.radians(lond1)
	lat2 = math.radians(latd2)
	lon2 = math.radians(lond2)
	
	global R
	dlat = (lat2-lat1)
	dlon = (lon2-lon1)
	a = math.sin(dlat/2) * math.sin(dlat/2) + math.sin(dlon/2) * math.sin(dlon/2) * math.cos(lat1) * math.cos(lat2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = R * c
	return d

def GCbearing(latd1,lond1,latd2,lond2):
	lat1 = math.radians(latd1)
	lon1 = math.radians(lond1)
	lat2 = math.radians(latd2)
	lon2 = math.radians(lond2)
	dlat = (lat2-lat1)
	dlon = (lon2-lon1)
	y = math.sin(dlon) * math.cos(lat2)
	x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
	brng = math.atan2(y, x)
	math.degrees(brng)
	math.degrees(brng)
	return math.degrees(brng)

def GCmid(latd1,lond1,latd2,lond2):
	lat1 = math.radians(latd1)
	lon1 = math.radians(lond1)
	lat2 = math.radians(latd2)
	lon2 = math.radians(lond2)
	dlat = (lat2-lat1)
	dlon = (lon2-lon1)
	bx = math.cos(lat2) * math.cos(dlon)
	by = math.cos(lat2) * math.sin(dlon)
	lat3 = math.atan2(math.sin(lat1)+math.sin(lat2),math.sqrt( (math.cos(lat1)+bx)*(math.cos(lat1)+bx) + by*by) )
	lon3 = lon1 + math.atan2(by, math.cos(lat1) + bx)
	return math.degrees(lat3), math.degrees(lon3)


# IGC files store longitude as DDDMMmmmN
def lon_to_degrees(lon):
	direction = {'E': 1, 'W':-1}
	degrees = int(lon[0:3])
	minutes = int(lon[3:8])
	minutes /= 1000.
	directionmod = direction[lon[8]]
	return (degrees + minutes/60.) * directionmod
# IGC files store latitude as DDMMmmmN
def lat_to_degrees(lat):
  direction = {'N':1, 'S':-1}
  degrees = int(lat[0:2])
  minutes = int(lat[2:7])
  minutes /= 1000.
  directionmod = direction[lat[7]]
  return (degrees + minutes/60.) * directionmod
