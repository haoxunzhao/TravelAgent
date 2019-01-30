from model import *
import unittest

# class TestDatabase(unittest.TestCase):
#     def test_database(self):
#         try:
#             create_db()
#         except:
#             self.fail()
#         DBNAME = 'SitesDB.db'
#         try:
#             conn = sqlite.connect(DBNAME)
#             cur = conn.cursor()
#         except Error as e:
#             print(e)
#             self.fail()
#
#         q = '''
#         SELECT * FROM Cities
#         '''
#         res = cur.execute(q).description
#         self.assertEqual(res[0][0], 'Id')
#         self.assertEqual(res[1][0], 'Name')
#         self.assertEqual(res[2][0], 'CountryId')
#         conn.close()


class TestSites(unittest.TestCase):
    def test_sites(self):
        cityname = 'Granada'
        sortorder = 'ASC'

        E, res, countryname, countryid, cityid = search_site_db(cityname,sortorder)
        self.assertEqual(E, False)
        self.assertEqual(len(res),15)
        self.assertEqual(countryname, 'Spain')
        self.assertEqual(countryid, 'ES')
        self.assertEqual(cityid, 7)
        self.assertEqual(res[0][1], 24.74)

class TestRestaurants(unittest.TestCase):
    def test_restaurants(self):
        cityid = 12
        sortorder = 'ASC'
        restlist = search_restaurants(cityid, sortorder)
        self.assertEqual(restlist[0][0],'Trattoria Zà Zà')
        self.assertEqual(restlist[0][1], 4.0)
        self.assertEqual(restlist[3][3], '+39 055 230 2987')

class TestFlights(unittest.TestCase):
    def test_flights(self):
        inputinfo = siteinfo('Tokyo','115','Japan','JP','Chicago','American',
        '06', '02', '2018')
        get_flight(inputinfo)
        res = search_flight(inputinfo)
        self.assertEqual(res[0][0], 'NH111')
        self.assertEqual(res[1][0], 'TG6177')
        self.assertEqual(res[0][2], 'HND')
        self.assertEqual(res[3][1], 'ORD')



unittest.main()
