import numpy as np
import scipy as sp
import os, sys, random

import matplotlib.pyplot as plt

class Trader(object):

	def __init__(self, money, food, expenditure, metabolism, greed, confidence):

		self.money = money
		self.food = food

		self.metabolism = metabolism
		self.expenditure = expenditure

		self.greed = greed
		self.confidence = confidence


	def decide(self, price):

		try: hunger = exp_decision(self.metabolism / self.food, 1)
		except: hunger = 1.

		#print("met = {}, food = {}, hunger = {}".format(self.metabolism, self.food, hunger))

		try: desire = exp_decision(self.expenditure / self.money, 1)
		except: desire = 1.

		#print("frug = {}, money = {}, desperation = {}".format(self.frugality, self.money, desperation))

		barter(hunger, desire, self.greed, self.confidence)

		if price 

		return price

	def update(self):

		self.food -= self.metabolism
		if self.food < 0: self.food = 0
		self.money -= self.expenditure
		if self.money < 0: self.money = 0


def exp_decision(x, a):

	return 1 - np.exp(- x / a)


def barter(hunger, desire, greed, confidence):

	return hunger * greed + desire * confidence


standard_met = 5

start_money = 10
start_food = 5

traders = [Trader(start_money, start_food, 1.0, 1.0, 
			1 + (np.random.rand() - 0.5) * 0.001, 
			1 + (np.random.rand() - 0.5) * 0.001) for i in range(2)]

asking_price = []
selling_price = []

for choice in range(20):

	price = np.random.rand() * 10
	asking_price.append(price)

	trader1_price = 
		amend_price = traders[0].decide(price)
		selling_price.append(amend_price)

	for trader in traders: trader.update()

plt.scatter(asking_price, selling_price)
plt.show()
