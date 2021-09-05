# -*- coding: utf-8 -*-

import os
import json
from shutil import rmtree
from pathlib import Path
import unittest

from valhalla import Actor
from valhalla import config
from valhalla.utils import decode_polyline

PWD = Path(os.path.dirname(os.path.abspath(__file__)))

class TestBindings(unittest.TestCase):
    """Be a bit lazy: all tests are run in the given order, so that config failure test succeeds."""

    @classmethod
    def setUpClass(cls):
        cls.config_path = Path(os.path.join(PWD, 'valhalla.json'))
        cls.tar_path = Path(os.path.join(PWD, "valhalla_tiles.tar"))

        cls.actor = Actor(str(cls.config_path), str(cls.tar_path))

    @classmethod
    def tearDownClass(cls):
        cls.config_path.unlink()
        del cls.actor

    def test_a_config(self):

        with open(self.config_path) as f:
            config_json = json.load(f)

        self.assertEqual(config_json['mjolnir']['tile_extract'], str(self.tar_path))

        from valhalla.config import _global_config
        self.assertEqual(_global_config['mjolnir']['tile_extract'], str(self.tar_path))

    def test_b_route(self):
        query = {
            "locations": [
                {"lat": 52.08813, "lon": 5.03231},
                {"lat": 52.09987, "lon": 5.14913}
            ],
            "costing": "bicycle",
            "directions_options": {"language": "ru-RU"}
        }
        route = self.actor.route(query)

        self.assertIn('trip',  route)
        self.assertIn('units', route['trip'])
        self.assertEqual(route['trip']['units'], 'kilometers')
        self.assertIn('summary', route['trip'])
        self.assertIn('length', route['trip']['summary'])
        self.assertGreater(route['trip']['summary']['length'], .7)
        self.assertIn('legs', route['trip'])
        self.assertGreater(len(route['trip']['legs']), 0)
        self.assertIn('maneuvers', route['trip']['legs'][0])
        self.assertGreater(len(route['trip']['legs'][0]['maneuvers']), 0)
        self.assertIn('instruction', route['trip']['legs'][0]['maneuvers'][0])

        route_str = self.actor.route(json.dumps(query, ensure_ascii=False))
        self.assertIsInstance(route_str, str)
        # C++ JSON string has no whitespace, so need to make it jsony
        self.assertEqual(json.dumps(route), json.dumps(json.loads(route_str)))

    def test_c_isochrone(self):
        query = {
            "locations": [
                {"lat": 52.08813, "lon": 5.03231}
            ],
            "costing": "pedestrian",
            "contours": [
                    {
                        'time': 1
                    }, {
                        'time': 5
                    }, {
                        'distance': 1
                    }, {
                        'distance': 5
                    }
            ],
            "show_locations": True
        }

        iso = self.actor.isochrone(query)

        self.assertEqual(len(iso['features']), 6)  # 4 isochrones and the 2 point layers

    def test_d_change_config(self):
        c = config.get_default()
        c['service_limits']['bicycle']['max_distance'] = 1
        actor = Actor(str(self.config_path), config=c)

        with self.assertRaises(RuntimeError) as e:
            actor.route(json.dumps({"locations":[{"lat":52.08813,"lon":5.03231},{"lat":52.09987,"lon":5.14913}],"costing":"bicycle","directions_options":{"language":"ru-RU"}}))
            self.assertIn('exceeds the max distance limit', str(e))

    def test_e_decode_polyline(self):
        encoded = 'mpivlAhwadlCxl@jPhj@hOdJ~BnFjAdEf@pIp@bDHhHKrI[~EB|AG|B_@fNuDzC?bCTzAXtFlBhANnADrAKhA]rAi@|A{@fGkE|CuApDuA|Ac@jAm@lAy@xA_C~@iD`@cD\\mAh@cAv@e@v@UrAOjB@~BNjUzBzz@xIndAnK'

        dec6 = decode_polyline(encoded)
        self.assertEqual(len(dec6), 43)
        self.assertEqual(dec6[0], (-74.007941, 40.752407))

        dec6_latlng = decode_polyline(encoded, order='latlng')
        self.assertEqual(len(dec6_latlng), 43)
        self.assertEqual(dec6_latlng[0], tuple(reversed(dec6[0])))
