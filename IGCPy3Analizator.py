#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IGCPy3Analizator.py
#  

#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import datetime
import gc_math
import math
import simplify
import sys

def main():
	
	return 0

if __name__ == '__main__':
	main()
  

datoteka=sys.argv[1]
listaBZapisa = []
dizanja = []
startTime=10
dnevnikLeta={'Datum':0,'Mjesto_starta':0,'MSL_starta':0,'Vrijeme_starta':0,'Maximalna_visina':0,'Maximalno_dizanje':0,'Ukupno_penjanje':0,'Prelet_km':0,'Trajanje':0,'Krilo':0,'Odometar':0}

#------------------FUNKCIJE--------------------------
def vrijemeSM (sekunde): # konverzija sekundi u sate i minute
	sat=sekunde//3600
	minute=sekunde//60%60
	return [sat,minute]
	
def izracunBzapisa(zapisi): # izracuni nad B zapisima IGC-a
	# <0:time> <1:lat> <2:lon> <3:baro alt><4:GPS alt> ,5:dVrijeme(sec), 6:dPomak(m),7:kurs (°), 8:dVisine(m), 9:brVertikal(m/s), 10:brHorizont(ms)
	for i,vg in enumerate(zapisi):
		dizanje = 0
		
		#proteklo vrijeme od predhodnog zapisa dVrijeme(sec)
		vrijemeOdPredhodne = zapisi[i][0]-zapisi[i-1][0]
		zapisi[i].append(vrijemeOdPredhodne.seconds) 
		
		# horizontalni pomak od predhodne 
		lat1=gc_math.lat_to_degrees(zapisi[i][1])
		lon1=gc_math.lon_to_degrees(zapisi[i][2])
		lat2=gc_math.lat_to_degrees(zapisi[i-1][1])
		lon2=gc_math.lon_to_degrees(zapisi[i-1][2])
		pomak = gc_math.GCdist(lat1,lon1,lat2,lon2)*1000
		zapisi[i].append(pomak)
		
		#kurs
		kurs=gc_math.GCbearing(lat1,lon1,lat2,lon2)
		zapisi[i].append(int(kurs))
		
		# verikalni pomak od predhodne
		dVisina=0
		if i>1:
			dVisina = vg[tipVisine] - zapisi[i-1][tipVisine]
			zapisi[i].append(dVisina)
			#~ print 'dVisina',dVisina
			
		# zbrajanje za ukupno dizanje	
		if dVisina>0 and i>startTime :
			dizanje = dizanje + dVisina
			dizanja.append(brVertikal)
		
		# verikalna brzina brVertikal(m/s)
		brVertikal=float(dVisina) / vrijemeOdPredhodne.seconds
		zapisi[i].append(brVertikal)
		
		# horizontalna brzina brHorizont(ms)
		brHorizont=pomak/vrijemeOdPredhodne.seconds
		zapisi[i].append(brHorizont)
		
		#~ print (i,listaIzracunBZapis[i][0].strftime(" %H:%M"),'hor brzina',brHorizont, 'dizanje',dVisina)
	return zapisi

def poletSlet(zapisi): # traženje polijetanja i slijetanja
	polijetanje = 0
	slijetanje= 0
	for i,vg in enumerate(zapisi):
			poslije=[]
			prije=[]

			if i>startTime :
				for j in range(-4,0):			
					try:
						dod=int(zapisi[i+j][10])
						prije.append(dod)
					except IndexError:
						#~ print 'zašao u prazno'
						pass
				for j in range(4):
					try:
						dod=int(zapisi[i+j][10])
						poslije.append(dod)
					except IndexError:
						#~ print 'zašao u prazno'
						pass	
				#trazenje pocetka leta			
				if (sum(prije)/4)<2 and (sum(poslije)/4)>4 and (sum(poslije)/4)<8 and polijetanje==0:
					polijetanje=i
					#print ('Polijetanje\t',vg[0].strftime("%H:%M"))
					
				#trazenje kraja leta
				if (sum(prije)/4)>5 and (sum(poslije)/4)<1 and slijetanje==0:
					#print ('Slijetanje\t',vg[0].strftime("%H:%M"))
					slijetanje= i
					break
	return(polijetanje,slijetanje)

def optimOLC(zapisi): # optimizacija OLC
	listaTocaka=[]
	zapis=[]

	for i,vg in enumerate(zapisi):
		#~ print 'optimiz', vg
		lat=gc_math.lat_to_degrees(vg[1])
		lon=gc_math.lon_to_degrees(vg[2])
		if i>= polijetanje and i<=slijetanje:
			#`points`: An array of dictionaries, containing x, y coordinates: `{'x': int/float, 'y': int/float}`
			zapis={'x': lat, 'y': lon}
			listaTocaka.append(zapis)
	optim=simplify.simplify(listaTocaka,0.009,True)	
	parametar=0.018
	while len(optim)>9:
		parametar=parametar-0.0001
		optim=simplify.simplify(listaTocaka,parametar,True)

	prelet=0
	for j, par in enumerate(optim):
		if j>1:		
			# horizontalni pomak od predhodne 
			lat1=par['x']
			lon1=par['y']
			lat2=optim[j-1]['x']
			lon2=optim[j-1]['y']
			pomak = gc_math.GCdist(lat1,lon1,lat2,lon2)*1000
			print ('Dionica\t{0:.2f}km'. format(pomak/1000))
			prelet+=pomak
	return prelet			
	
#------------------KRAJ FUNKCIJA--------------------------


print ('***----  IGC Analizator  ----***\n')
# citanje IGC-a
f = open(datoteka)
print ('Datoteka:\t',datoteka)

# parsiranje IGC zaglavlja
while True:
	line = f.readline()	
	bZapis=[]
	if len(line) == 0:# Zero length indicates EOF
		break

	if (line[0:5]== 'HFDTE'):		
		global datum
		datum = datetime.date(int('20'+line[9:11]),int(line[7:9]),int(line[5:7]))
		dnevnikLeta['Datum']=datum.strftime("%d.%m.%Y")
		print ('Datum:\t',datum.strftime("%d.%m.%Y"))
		
	if (line[0:10]== 'HOPLTPILOT'):
		pilot =  line[12:-1]
		print ('Pilot:\t',pilot)
		
	if (line[0:15]== 'HOGTYGLIDERTYPE'):
		krilo = line[17:-1]
		dnevnikLeta['Krilo']=krilo
		print ('Krilo:\t', krilo)
		
	if (line[0:5]== 'HOSIT'):
		 mjesto = line[11:-1]

		 dnevnikLeta['Mjesto_starta']=mjesto
		 print ('Mjesto:\t', mjesto)
	if (line[0:16]=='HODTM100GPSDATUM'):
		gpsDatum =  line[18:-1]
		print ('GPS datum:', gpsDatum)
		
# parsiranje B zapisa B <time> <lat> <long> <baro alt><GPS alt>
	if (line[0]== 'B'):		
		#~ vrijeme = datetime.time(int(line[1:3]),int(line[3:5]),int(line[5:7]))
		vrijeme = datetime.time(int(line[1:3]),int(line[3:5]),int(line[5:7]))
		vrijemeDatum = datetime.datetime.combine(datum, vrijeme)
		bZapis.append(vrijemeDatum)

		lat=line[7:15]
		bZapis.append(lat)

		lon=line[15:24]
		bZapis.append(lon)
		
		visinaBaro = int(line[25:30])
		bZapis.append(visinaBaro)
		
		visinaGPS = int(line[30:35])
		bZapis.append(visinaGPS)
		
		listaBZapisa.append(bZapis)
		
		#~ print 'vrijeme',vrijemeDatum
		#~ print 'hour  :', vrijeme.hour
		#~ print 'minute:', vrijeme.minute
		#~ print 'second:', vrijeme.second		
		#~ print 'lat',lat
		#~ print 'lon',lon
		#~ print 'baroo {} m'.format(visinaBaro)
		#~ print 'gps {} m'.format(visinaGPS)
		#~ print'--nova--\n'

# close the file
f.close()

print ('Vrijeme GPS zapisa:', listaBZapisa[0][0])

print ('\n----- Analiza leta ------')

# određivanje zapisa visine - baro ili GPS
tipVisine = 4
if int(listaBZapisa[15][4])==0:
	tipVisine=3

# izracuni nad B zapisima
listaIzracunBZapis=izracunBzapisa(listaBZapisa)
print('Pronadjeno {} zapisa'.format(len(listaIzracunBZapis)))
	
# pocetak i kraj
polijetanje=5
slijetanje=len(listaIzracunBZapis)-3
if 	tipVisine==3: # zbog loših zapisa iz XCTrenera ne radi logika
	pass

else:
	poslet=poletSlet(listaIzracunBZapis)
	polijetanje=poslet[0]
	slijetanje=poslet[1]
	# ako logika ne detektira
	if (poslet[0]==0):
		polijetanje=5
		
	if (poslet[1]==0):	
		slijetanje=len(listaIzracunBZapis)-3
		
print ('Polijetanje\t',listaIzracunBZapis[polijetanje][0].strftime("%H:%M"))
print ('Slijetanje\t',listaIzracunBZapis[slijetanje][0].strftime("%H:%M"))	
print ('Visina starta:\t{}m'.format(listaIzracunBZapis[polijetanje][tipVisine]))
dnevnikLeta['MSL_starta']=listaIzracunBZapis[polijetanje][tipVisine]
dnevnikLeta['Vrijeme_starta']=	listaIzracunBZapis[polijetanje][0].strftime("%H:%M")	

# najveća visina leta
najTocke=sorted(listaBZapisa[polijetanje:slijetanje], key=lambda par: par[tipVisine])
print ('Visina max:\t', najTocke[-1][tipVisine])
dnevnikLeta['Maximalna_visina']=najTocke[-1][tipVisine]

# trazenje max dizanja
najTocke=sorted(listaBZapisa[polijetanje:slijetanje], key=lambda par: par[9])
print ("Max dizanje:\t{0:.2f}". format(najTocke[-1][9]))
dnevnikLeta['Maximalno_dizanje']= str('{0:.2f}'. format(najTocke[-1][9]))

# zbrajanje svih dizanja u letu
dizanja=0
for i,vg in enumerate(listaBZapisa[polijetanje:slijetanje]):
	if vg[8]>0:
		dizanja=dizanja+vg[8]
print ("Ukupno dizanje:\t", dizanja)
dnevnikLeta['Ukupno_penjanje']=dizanja

# odometar leta
odo=0
for i,vg in enumerate(listaBZapisa[polijetanje:slijetanje]):
	odo=odo+vg[6]
print ("Predjeni put:\t{0:.2f}km".format(int(odo)/1000))
dnevnikLeta['Odometar']=odo

# trajanje leta		
trajanjeS = listaIzracunBZapis[slijetanje][0]-listaIzracunBZapis[polijetanje][0]
trajanje=vrijemeSM(trajanjeS.seconds)
print ('Trajanje leta\t',trajanje[0],'h',trajanje[1],'min')
dnevnikLeta['Trajanje']='{}:{}'.format(trajanje[0],trajanje[1])

# optimizacija OLC
print('---- OLC ----')
prelet=optimOLC(listaBZapisa)
print ('Ukupno:\t{0:.2f}km'. format(prelet/1000))
dnevnikLeta['Prelet_km']=str('{0:.2f}'. format(prelet/1000))

#formatiranje za CSV zapis
csv= '{},{},{},{},{},{},{},{},{},{}'.format(dnevnikLeta['Datum'],dnevnikLeta['Mjesto_starta'],dnevnikLeta['MSL_starta'],dnevnikLeta['Vrijeme_starta'],dnevnikLeta['Maximalna_visina'],dnevnikLeta['Maximalno_dizanje'],dnevnikLeta['Ukupno_penjanje'],dnevnikLeta['Prelet_km'],dnevnikLeta['Trajanje'],dnevnikLeta['Krilo'])
print ('\nCSV:',csv)

#zapisivanje u csv sa imenom igc-a
izlazDat='{}_igc.csv'.format(datoteka)
fizlaz = open(izlazDat,'w')
fizlaz.write(csv)
fizlaz.close()
