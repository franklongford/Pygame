import numpy as np
import scipy as sp
import os, sys, random

import matplotlib.pyplot as plt

class Buyer(object):

	def __init__(self, money, food, greed, confidence, frugality, metabolism):

		self.money = money
		self.food = food
		self.greed = greed
		self.confidence = confidence
		self.frugality = frugality
		self.metabolism = standard_met * metabolism

	def decide(self, price):

		try: hunger = exp_decision(self.metabolism / self.food, 5)
		except: hunger = 1.

		print "met = {}, food = {}, hunger = {}".format(self.metabolism, self.food, hunger)

		try: desperation = exp_decision(self.frugality / self.money, 5)
		except: desperation = 1.

		print "frug = {}, money = {}, desperation = {}".format(self.frugality, self.money, desperation)

		print hunger, desperation, self.greed, self.confidence

		barter = hunger * desperation / (self.greed * self.confidence)
		price *= barter

		return price


def exp_decision(x, a):

	return 1 - np.exp(- x / a)


standard_met = 5

buyer = Buyer(10, 5, 0.9, 0.7, 0.2, 1.0)

for choice in xrange(1):

	price = np.random.rand() * 10
	amend_price = buyer.decide(price)
	print price, amend_price
