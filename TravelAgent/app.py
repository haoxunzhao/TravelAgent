from flask import Flask, render_template, request
import requests
import model
app = Flask(__name__)


@app.route('/home')
def input_des():
    citylist = model.get_city()
    num = len(citylist)
    totallist = []
    k=5
    i=1
    while k*i <len(citylist)+5:
        if k*i > len(citylist):
            totallist.append(citylist[k*i-5:len(citylist)])
        else:
            totallist.append(citylist[k*i-5:k*i])
        i += 1

    return render_template('home.html',citylist=totallist, num=num,
    url='http://127.0.0.1:5000/Paris')

@app.route('/sites', methods=['GET','POST'])
def sites_lists():
    global inputcity
    sortorder = 'DESC'
    if request.method == 'POST':
        des = request.form['des']
        E,sitesdict,descountry,descouid,cityid = model.search_site_db(des)
        if E == False:
            inputcity = model.siteinfo(des,cityid,descountry,descouid)
            num = len(sitesdict)
        else:
            num = None
    else:
        sitesdict,descouid,descountry = model.get_site_info('Paris')
        num = len(sitesdict)

    return render_template('sitelist.html', num=num, siteslist=sitesdict,
    cityname=inputcity.cityname, E=E)

@app.route('/sites/sortby', methods=['GET','POST'])
def sites_lists_sortby():
    sortorder = request.form['sortorder']
    E,sitesdict,descountry,descouid,cityid = model.search_site_db(inputcity.cityname
    ,sortorder)
    num = len(sitesdict)

    return render_template('sitelist.html', num=num, siteslist=sitesdict,
    cityname=inputcity.cityname, E=E)

@app.route('/weather', methods=['GET','POST'])
def weather():
    wethlist = model.get_weather(inputcity.cityname,inputcity.countryid)
    return render_template('weather.html',des=inputcity.cityname,wethlist=wethlist)

@app.route('/restaurants', methods=['GET','POST'])
def restaurants():
    sortorder = 'DESC'
    if request.method == 'POST':
        sortorder = request.form['sortorder']
    restlist = model.search_restaurants(inputcity.cityid,sortorder)
    return render_template('restaurants.html', des=inputcity.cityname,
    restlist=restlist)


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    return render_template('booking.html')

@app.route('/flight', methods=['GET','POST'])
def flight():
    global depcity
    global depcountry
    if request.method == 'POST':
        inputcity.depcity = request.form['depcity']
        inputcity.depcountry = request.form['depcountry']
        inputcity.depmon = request.form['mon']
        inputcity.depday = request.form['day']
        inputcity.depyear = request.form['year']
        model.get_flight(inputcity)
        flightlist = model.search_flight(inputcity)
    return render_template('flight.html',flightlist=flightlist,
    des=inputcity.cityname, depcity=inputcity.depcity)


if __name__ == '__main__':
    # model.create_db()
    app.run(debug=True)
