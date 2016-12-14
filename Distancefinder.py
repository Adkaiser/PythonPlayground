#Script to find collocated groups Swatch, Fossil, and Diesel watch stores.
#Relies on the CoordinateDistance package, found on http://www.johndcook.com/blog/python_longitude_latitude/

from lxml import html, etree
import requests
import time
import json
import math
import sys
from CoordinateDistance import distance_on_unit_sphere
import xml.etree.ElementTree as ET

MAX_DISTANCE = float(sys.argv[1])

#Swatch
payload = {'embeded':'', 'searchinput': 'United States', 'userLocation[countryCode]': 'US', 'userLocation[latitude]':	'37.424999', 'userLocation[longitude]':	'-121.945999'}
page = requests.post('http://www.swatch.com/en/api/storelocator/v2/search?embedded=&searchinput=United%20States&userLocation%5BcountryCode%5D=US&userLocation%5Blatitude%5D=37.424999&userLocation%5Blongitude%5D=-121.945999', payload)
tree = html.fromstring(page.text)

#Pull the stores
stores = tree.xpath('.//div[@id="storeListResults"]')[0][0]

swatch_stores = []
for store in stores:
	
	#Get store info
	storeinfo = html.fromstring(etree.tostring(store)).xpath('//div[@class="storeInfo"]')[0]
	
	#Get Street
	street = storeinfo[1].xpath('//span[@class="street-address"]')[0]
	street_f = "".join(street.xpath("string()").split("\n"))
	street_f = "".join(street_f.split("    "))
	city = storeinfo[1].xpath('//span[@class="locality"]')[0]
	city_f = "".join(city.xpath("string()").split("\n"))
	city_f = "".join(city_f.split("    "))
	
	#Get Lat
	lat = float(storeinfo[1].xpath('//input[@class="latitude"]')[0].value)
	
	
	#write Lon
	lon = float(storeinfo[1].xpath('//input[@class="longitude"]')[0].value)
	
	swatch_stores.append({"address":street_f + ", " + city_f, "lat":lat, "lon":lon})


#Diesel
page = requests.get('http://www.diesel.com/store-locator/get-stores?country=11&city=&type=')
tree = json.loads(page.text)

diesel_stores = []
for store in tree:
	
	#write Street
	street_f = store["address"] + ", " + store["city"]
	
	#write City
	lat = float(store["latitude"])
	
	#write State
	lon = float(store["longitude"])
	
	diesel_stores.append({"address":street_f, "lat":lat, "lon":lon})


#Get each Diesel store
colocated_stores = []
for diesel in diesel_stores:
	diesel_addr = diesel["address"]
	d_lat = diesel["lat"]
	d_lon = diesel["lon"]
	d_close = {"Diesel":diesel_addr, "lat":d_lat, "lon":d_lon, "Swatch":[], "Fossil":[]}
	#compare to each swatch store
	for swatch in swatch_stores:
		swatch_addr = swatch["address"]
		s_lat = swatch["lat"]
		s_lon = swatch["lon"]
		distance = distance_on_unit_sphere(d_lat, d_lon, s_lat, s_lon)
		if (distance < MAX_DISTANCE):
			d_close["Swatch"].append(swatch_addr)
	if (len(d_close["Swatch"]) > 0):
		colocated_stores.append(d_close)

file = open('ColocatedStores.txt', 'w')
for storeset in colocated_stores:
	time.sleep(1)
	addr = storeset["Diesel"]
	page = requests.get("http://hosted.where2getit.com/fossil/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E269B11D6-E81F-11E3-A0C3-A70A0D516365%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E250%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E135+Spring+Street%2C+New+York%3C%2Faddressline%3E%3Clongitude%3E"+str(storeset["lon"])+"%3C%2Flongitude%3E%3Clatitude%3E"+str(storeset["lat"])+"%3C%2Flatitude%3E%3Ccountry%3EUS%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E10%3C%2Fsearchradius%3E%3Cradiusuom%3Emile%3C%2Fradiusuom%3E%3Corder%3EFOSSIL_STORE%3A%3Anumeric%2CFOSSIL_OUTLET%3A%3Anumeric%2CAUTHORIZED_RETAILER%3A%3Anumeric%2C_DISTANCE%3C%2Forder%3E%3Cwhere%3E%3Cor%3E%3Cfossil_store%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ffossil_store%3E%3Cfossil_outlet%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ffossil_outlet%3E%3Cauthorized_retailer%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fauthorized_retailer%3E%3C%2For%3E%3Cwatches%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fwatches%3E%3Chandbags%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fhandbags%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E")
	tree = ET.fromstring(page.text)
	stores = tree[0]
	
	for store in stores:
		if(len(store)>0 and store[0].text == 'Fossil'):
			f_lat = float(store.find('latitude').text)
			f_lon = float(store.find('longitude').text)
			d_lat = storeset["lat"]
			d_lon = storeset["lon"]
			distance = distance_on_unit_sphere(d_lat, d_lon, f_lat, f_lon)
			if(distance < MAX_DISTANCE):
				storeset["Fossil"].append(store.find('address1').text + ", " + store.find('city').text)
	
	if(len(storeset["Swatch"]) < 1 or len(storeset["Fossil"]) < 1):
		continue
	
	file.write(("DIESEL: " + storeset["Diesel"] + "\nSWATCH ").encode('utf-8'))
	
	for store in storeset["Swatch"]:
		file.write((store + "; ").encode('utf-8'))
	file.write("\nFOSSIL:".encode('utf-8'))
	
	for store in storeset["Fossil"]:
		file.write((store + "; ").encode('utf-8'))
	file.write("\n\n".encode('utf-8'))
	
file.close()