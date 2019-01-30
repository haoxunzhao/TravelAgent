import requests
import json
from bs4 import BeautifulSoup
import sqlite3 as sqlite
from secrets import weatherkey, YelpApiKey, flightstats_appid, flightstats_appkey
import time

class siteinfo:
    def __init__(self, cityname, cityid, countryname, countryid, depcity = None,
    depcountry = None, depmon = None, depday = None, depyear = None):
        self.cityname = cityname
        self.cityid = cityid
        self.countryname = countryname
        self.countryid = countryid
        self.depcity = depcity
        self.depcountry = depcountry
        self.depmon = depmon
        self.depday = depday
        self.depyear = depyear

def get_site_info():
    DBNAME = 'SitesDB.db'
    try:
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)

    f=open('Cities.json','r')
    citydic = json.load(f)
    f.close()
    try:
        cachesites_file = open("CacheSites.json", 'r')
        CACHE_SITES_DICT = json.load(cachesites_file)
        cachesites_file.close()
    except:
        CACHE_SITES_DICT = {}
    for i in citydic:
        cityname = i

        exist = True
        if not cityname in CACHE_SITES_DICT:
            exist = False
            try:
                baseurl = 'https://www.isango.com'
                url = baseurl+'/'+cityname.lower().replace(' ', '-').replace('/','')
                html = requests.get(url).text
                CACHE_SITES_DICT[cityname] = []
                soup = BeautifulSoup(html,'html.parser')
                list = soup.find_all(class_="fl fw ulthingsList productULList")[0].find_all('li')
                for i in list:
                    sitename = i.find(class_="fl fw lihead").string
                    price = i.find(class_="fl fw price").find('em').string[4:]
                    unit = i.find(class_="fl fw pp").string
                    detailpart = i.find("a")['href']
                    detailurl = baseurl+detailpart
                    detailhtml = requests.get(detailurl).text
                    detailsoup = BeautifulSoup(detailhtml,"html.parser")
                    delist = detailsoup.find_all(class_="fl fw accord pinfo")
                    detailinfo=''
                    p = delist[0].find_all('p')
                    for j in p:
                        if j.string != None:
                            detailinfo += j.string
                    # for child in delist[0].children:
                    #     if child.string == None:
                    #         headline = child.find('a').string
                    #         destring = child.find_all('div')
                    #         detailinfo[headline] = []
                    #         for j in destring:
                    #             for child1 in j.children:
                    #                 detailinfo[headline].append(child1.string)
                    CACHE_SITES_DICT[cityname].append([sitename,price,unit,detailinfo])

            except:
                ff = open('CacheSites.json','w', encoding='utf-8')
                ff.write(json.dumps(CACHE_SITES_DICT, indent=4))
                ff.close()
                # print('*******************')
                # print(cityname)
                # print("crawling error")
                # print('********************')
                continue

    ff = open('CacheSites.json','w', encoding='utf-8')
    ff.write(json.dumps(CACHE_SITES_DICT, indent=4))
    ff.close()

def search_site_db(cityname,sortorder='DESC'):
    DBNAME = 'SitesDB.db'
    try:
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)

    statement ='SELECT Id FROM Cities WHERE Name="'
    statement += cityname+'"'
    cityid = cur.execute(statement).fetchall()
    E=False
    if len(cityid) != 0:
        cityid = cityid[0][0]
        statement = 'SELECT Name,Price,PriceUnit,Details FROM Sites WHERE CityId="'
        statement += str(cityid) +'" ORDER BY Price ' + sortorder
        res = cur.execute(statement).fetchall()

        statement='''
        SELECT EnglishName,Alpha2 FROM Cities JOIN Countries
        ON CountryId=Countries.Id WHERE Cities.Name='''
        statement +='"'+cityname+'"'
        country = cur.execute(statement).fetchall()[0]
        countryname = country[0]
        countryid = country[1]

    else:
        E=True
        res, countryname, countryid, cityid = None, None, None, None
    conn.close()
    return E, res, countryname, countryid, cityid

def create_db():
    f=open('CacheSites.json','r')
    CACHE_SITES_DICT = json.load(f)
    f.close()

    f1 = open('Cities.json','r')
    citiesdict = json.load(f1)
    f1.close()

    f2 = open("countries.json",'r', encoding='utf-8')
    countries = json.load(f2)
    f2.close()

    f3 = open("airport1.json",'r', encoding='utf-8')
    airports = json.load(f3)
    f3.close()

    f4 = open("Cacherest1.json",'r', encoding='utf-8')
    CACHE_REST_DICT = json.load(f4)
    f4.close()

    f5=open('CacheFlight.json', 'r')
    CACHE_FLIGHT_DICT = json.load(f5)
    f5.close()

    DBNAME = 'SitesDB.db'
    try:
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)

    statement ='DROP TABLE IF EXISTS "Countries"'
    cur.execute(statement)
    conn.commit()

    statement ='DROP TABLE IF EXISTS "Sites"'
    cur.execute(statement)
    conn.commit()

    statement ='DROP TABLE IF EXISTS "Cities"'
    cur.execute(statement)
    conn.commit()

    statement ='DROP TABLE IF EXISTS "Airports"'
    cur.execute(statement)
    conn.commit()

    statement ='DROP TABLE IF EXISTS "Flights"'
    cur.execute(statement)
    conn.commit()

    statement ='DROP TABLE IF EXISTS "Restaurants"'
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Countries' (
       'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
       'Alpha2' TEXT,
       'Alpha3' TEXT,
       'EnglishName' TEXT,
       'Region' TEXT,
       'Subregion' TEXT,
       'Population' INTEGER,
       'Area' REAL)
    '''
    cur.execute(statement)
    conn.commit()

    statement ='''
    CREATE TABLE 'Sites'(
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Name' TEXT,
    'CityId' INTEGER,
    'Price' REAL,
    'PriceUnit' TEXT,
    'Details' TEXT
    )
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
    CREATE TABLE 'Cities'(
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Name' TEXT,
    'CountryId' INTEGER
    )
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
    CREATE TABLE 'Airports'(
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Name' TEXT,
    'Code' TEXT,
    'CityName' TEXT,
    'CountryId' INTEGER
    )
    '''
    cur.execute(statement)
    conn.commit()

    statement ='''
    CREATE TABLE 'Restaurants'(
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'CityId' INTEGER,
    'Name' TEXT,
    'Rating' REAL,
    'Address' TEXT,
    'Phone' TEXT,
    'YelpPage' TEXT
    )
    '''
    cur.execute(statement)
    conn.commit()

    statement ='''
    CREATE TABLE 'Flights'(
    'DepartureCity' TEXT,
    'ArrivalCity' TEXT,
    'FlightNum' TEXT,
    'DepartureAirportCode' TEXT,
    'ArrivalAirportCode' TEXT,
    'Stops' TEXT,
    'DepartureTerminal' TEXT,
    'ArrivalTerminal' TEXT,
    'DepartureTime' TEXT,
    'ArrivalTime' TEXT,
    'DepartureDate' TEXT
    )
    '''
    cur.execute(statement)
    conn.commit()



    items = []
    statement ='''
    INSERT INTO Countries (Id, Alpha2, Alpha3, EnglishName,
    Region, Subregion, Population,Area)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    for i in countries:
        items = (None, i['alpha2Code'], i['alpha3Code'], i['name'],
        i['region'], i['subregion'], i['population'], i['area'])
        cur.execute(statement,items)
        conn.commit()

    statement = 'SELECT Id,EnglishName,Alpha2 FROM Countries'
    res = cur.execute(statement).fetchall()
    dict1 = {}
    dict2 = {}
    for i in res:
        dict1[i[1]]=int(i[0])
        dict2[i[2]]=int(i[0])

    statement = 'INSERT INTO Cities VALUES(?,?,?)'
    for i in citiesdict:
        values = (None,i,dict1[citiesdict[i]])

        cur.execute(statement,values)
        conn.commit()

    statement = 'INSERT INTO Airports VALUES(?,?,?,?,?)'
    for i in airports["airports"]:
        values = (None,i['name'],i['iata'],i['city'],dict2[i["countryCode"]])
        cur.execute(statement,values)
        conn.commit()


    statement = 'SELECT Id,Name FROM Cities'
    res = cur.execute(statement).fetchall()
    dict = {}
    for i in res:
        dict[i[1]]=int(i[0])


    statement = 'INSERT INTO Sites VALUES (?,?,?,?,?,?)'
    for i in CACHE_SITES_DICT:
        for j in CACHE_SITES_DICT[i]:
            sitevalues = (None, j[0], int(dict[i]), j[1], j[2],j[3])

            cur.execute(statement,sitevalues)
            conn.commit()

    statement = 'INSERT INTO Restaurants Values(?,?,?,?,?,?,?)'
    for j in CACHE_REST_DICT:
        cityname = j.split(',')[0]
        try:
            if 'businesses' in CACHE_REST_DICT[j]:
                for i in CACHE_REST_DICT[j]['businesses']:
                    restaddr=''
                    for k in i['location']['display_address']:
                        restaddr += k+'  '

                    vals = (None, dict[cityname], i['name'], i['rating'],
                    restaddr, i['display_phone'], i['url'])
                    cur.execute(statement,vals)
                    conn.commit()
        except:
            print('***********')
            print(j)

    statement = 'INSERT INTO Flights Values(?,?,?,?,?,?,?,?,?,?,?)'
    for j in CACHE_FLIGHT_DICT:
        words = j.split(',')
        date = words[2]+'/'+words[3]+'/'+words[4]
        try:
            for i in CACHE_FLIGHT_DICT[j]:
                vals = (words[0],words[1],i['flnum'],
                i['departureAirportFsCode'],i['arrivalAirportFsCode'],
                i['stops'],i['departureTerminal'],i['arrivalTerminal'],
                i['departureTime'],i['arrivalTime'],date)
                cur.execute(statement,vals)
                conn.commit()
        except:
            print('***********')
            print(j)

    conn.close()

def get_restaurants():
    try:
        cacherest_file = open("Cacherest1.json", 'r')
        CACHE_REST_DICT = json.load(cacherest_file)
        cacherest_file.close()
    except:
        CACHE_REST_DICT = {}
    try:
        cachecity_file = open("Cities.json", 'r')
        CACHE_CITY_DICT = json.load(cachecity_file)
        cachecity_file.close()
    except:
        CACHE_CITY_DICT = {}

    for i in CACHE_CITY_DICT:
        title = i+" "+CACHE_CITY_DICT[i]
        if not title in CACHE_REST_DICT:
            try:
                headers={"Authorization":"Bearer "+YelpApiKey}
                baseurl = "https://api.yelp.com/v3/businesses/search"
                para = {"term":"restaurants","location":title}
                res = json.loads(requests.get(baseurl,para,headers=headers).text)
                CACHE_REST_DICT[title] = res
                time.sleep(1)

            except:
                print('Error')
                print(title)
                print('*****************')
                continue

    f=open("Cacherest1.json", 'w', encoding = "utf-8")
    f.write(json.dumps(CACHE_REST_DICT, indent=4))
    f.close()
    # DBNAME = 'SitesDB.db'
    #
    # try:
    #     conn = sqlite.connect(DBNAME)
    #     cur = conn.cursor()
    # except Error as e:
    #     print(e)
    # for i in CACHE_REST_DICT[j]['businesses']:
    #     restaddr=''
    #     for k in i['location']['display_address']:
    #         restaddr += k+'  '
    #
    #     vals = (None, dict[cityname], i['name'], i['rating'],
    #     restaddr, i['display_phone'], i['url'])
    #     cur.execute(statement,vals)
    #     conn.commit()
    # conn.close()

def search_restaurants(cityid, sortorder='DESC'):
    DBNAME = 'SitesDB.db'
    try:
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)
    statement = 'SELECT Name,Rating,Address,Phone,YelpPage FROM Restaurants '
    statement += 'WHERE CityId="' + str(cityid) +'" ORDER BY Rating '+ sortorder
    restlist = cur.execute(statement).fetchall()
    conn.close()
    return restlist

def get_flight(siteinfo):
    para={'appId':flightstats_appid,'appKey':flightstats_appkey}
    DBNAME = 'SitesDB.db'
    try:
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)
    try:
        f=open('CacheFlight.json', 'r')
        CACHE_FLIGHT_DICT = json.load(f)
        f.close()
    except:
        CACHE_FLIGHT_DICT = {}

    title = siteinfo.depcity+','+siteinfo.cityname+','+siteinfo.depmon+','
    title += siteinfo.depday+','+siteinfo.depyear+','
    if not title in CACHE_FLIGHT_DICT:
        baseurl = "https://api.flightstats.com/flex/schedules/rest/v1/json/from/"
        statement = 'SELECT  Code FROM Airports WHERE CityName='
        statement += '"'+siteinfo.depcity +'" AND CountryId in (SELECT Id FROM Countries '
        statement +='WHERE EnglishName like "%'+siteinfo.depcountry +'%")'
        departure = cur.execute(statement).fetchall()
        deparcode = []
        for i in departure:
            deparcode.append(i[0])

        statement = 'SELECT  Code FROM Airports WHERE CityName='
        statement += '"'+siteinfo.cityname +'" AND CountryId=(SELECT Id FROM Countries WHERE EnglishName='
        statement +='"'+siteinfo.countryname +'")'
        arrival = cur.execute(statement).fetchall()
        arrcode = []
        for i in arrival:
            arrcode.append(i[0])
        route=[]
        for i in deparcode:
            for j in arrcode:
                url = baseurl+i+"/to/"+j+"/departing/"+siteinfo.depyear+"/"+siteinfo.depmon+"/"+siteinfo.depday
                routeres = json.loads(requests.get(url,para).text)
                route.append(routeres)

        flightlist=[]
        for i in route:
            if i["scheduledFlights"] !=[]:
                for j in i["scheduledFlights"]:
                    try:
                        flightdict={}
                        flightdict['flnum']=j["carrierFsCode"]+j["flightNumber"]
                        flightdict["departureAirportFsCode"]=j['departureAirportFsCode']
                        flightdict["arrivalAirportFsCode"]=j['arrivalAirportFsCode']
                        flightdict["stops"]=j['stops']
                        flightdict["departureTerminal"]=j['departureTerminal']
                        flightdict["arrivalTerminal"]=j['arrivalTerminal']
                        flightdict["departureTime"]=j['departureTime']
                        flightdict["arrivalTime"]=j['arrivalTime']
                        flightlist.append(flightdict)
                    except:
                        pass
        CACHE_FLIGHT_DICT[title] = flightlist

        f=open('CacheFlight.json','w',encoding='utf-8')
        f.write(json.dumps(CACHE_FLIGHT_DICT,indent=4))
        f.close()

        statement = 'INSERT INTO Flights VALUES(?,?,?,?,?,?,?,?,?,?,?)'
        for i in CACHE_FLIGHT_DICT[title]:
            vals = (siteinfo.depcity,siteinfo.cityname,i['flnum'],
            i['departureAirportFsCode'],i['arrivalAirportFsCode'],
            i['stops'],i['departureTerminal'],i['arrivalTerminal'],
            i['departureTime'],i['arrivalTime'],
            siteinfo.depmon+'/'+siteinfo.depday+'/'+siteinfo.depyear)
            cur.execute(statement,vals)
            conn.commit()

        conn.close()

    return CACHE_FLIGHT_DICT[title]

    # res = requests.get(baseurl,para).text
    # dict = json.loads(res)
    # f = open("airport.json",'w', encoding='utf-8')
    # f.write(json.dumps(dict,indent=4))
    # f.close()

def search_flight(siteinfo):
    DBNAME = 'SitesDB.db'
    try:
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)

    statement = 'SELECT FlightNum,DepartureAirportCode,ArrivalAirportCode,'
    statement += 'Stops,DepartureTerminal,ArrivalTerminal,DepartureTime,'
    statement += 'ArrivalTime FROM Flights WHERE DepartureCity="'
    statement += siteinfo.depcity +'" AND ArrivalCity="'
    statement += siteinfo.cityname +'" AND DepartureDate="'
    statement += siteinfo.depmon+'/'+siteinfo.depday+'/'+siteinfo.depyear+'"'
    res = cur.execute(statement).fetchall()
    return res
def get_city():
    DBNAME = 'SitesDB.db'

    try:
        conn = sqlite.connect(DBNAME)
        cur = conn.cursor()
    except Error as e:
        print(e)

    statement = '''
    SELECT Name,EnglishName FROM Cities JOIN Countries
    ON CountryId=Countries.Id
    '''
    citylist = cur.execute(statement).fetchall()
    conn.close()
    return citylist

def get_weather(cityname,counid):

    baseurl= "http://api.openweathermap.org/data/2.5/forecast"
    param = {'q':(cityname,counid), 'mode':"json", 'APPID':weatherkey}
    wethinfo = requests.get(baseurl, param).text
    wethinfo = json.loads(wethinfo)
    wethlist=[]
    try:
        for i in wethinfo["list"]:
            wethdict={}
            wethdict['time'] = i['dt_txt']
            wethdict['weather'] = i['weather'][0]['main']
            wethdict['tempf'] = round(9*(float(i['main']["temp"])-273.15)/5+32,1)
            wethdict['tempc'] = round(float(i['main']["temp"])-273.15,1)
            wethdict['wind'] = i['wind']['speed']
            wethdict['humidity'] = i['main']['humidity']
            wethdict['cloudiness'] = i['clouds']['all']
            wethdict['pressure'] = i['main']['pressure']
            wethlist.append(wethdict)
    except:
        pass

    return wethlist

# create_db()
