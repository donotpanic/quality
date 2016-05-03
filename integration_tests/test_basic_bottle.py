import unittest
import requests

root_url = 'http://localhost:8080'

class helloWorldTest(unittest.TestCase):
    def testHelloWorld(self):
        resp = requests.get(root_url + '/hello')
        self.assertEqual(resp.text, "Hello World!", "Hello world works")

class usersTest(unittest.TestCase):
    def testUserList(self):
        resp = requests.get(root_url + '/users')
        self.assertEqual(resp.text, "Users List", "User list returned")

    def testGetUser(self):
        resp = requests.get(root_url + '/users/1')
        self.assertEqual(resp.text, "User + 1", "User returned")

    def testGetUserInvalidType(self):
        resp = requests.get(root_url + '/users/one')
        self.assertEqual(resp.status_code, 404, "Error when string passed in for user")

        resp = requests.get(root_url + '/users/_')
        self.assertEqual(resp.status_code, 404, "Error when special character passed in for user")
