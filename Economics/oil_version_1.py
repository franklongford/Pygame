import numpy as np
import scipy as sp
import os, sys

import matplotlib.pyplot as plt

class Oil_Well(object):

	def __init__(self, oil, owner):
		self.oil = oil
		self.cost = oil * oil_price #* (np.random.rand() * 0.1 + 0.9)
		self.status = True
		self.owner = owner

	def extract(self, amount):
		self.oil -= amount
		if self.oil <= 0: 
			amount += self.oil
			self.oil = 0
			self.status = False
		return amount

class Company(object):

	def __init__(self, capital):
		self.capital = capital
		self.wells = []
		self.networth = 0
		self.oil = 0

	def buy_well(self, well):
		if self.capital >= well.cost:
			if well.owner:
				well.owner.capital += well.cost
				well.owner.wells.remove(well)
			self.capital -= well.cost
			self.wells.append(well)
			well.owner = self

	def pump_oil(self):
		for well in self.wells:
			if well.status: self.oil += well.extract(1)

	def sell_oil(self):
		supply = int(0.1 * self.oil)
		self.capital += supply * oil_price
		self.oil -= supply
		return supply

	def evaluate(self):
		new_networth = 0
		for well in self.wells:
			new_networth += well.oil * oil_price #* (np.random.rand() * 0.5 + 0.5)
		new_networth += self.oil * oil_price
		new_networth += self.capital
		self.networth = new_networth



n_wells = 50
n_comp = 5

max_oil = 10000
starting_money = 1000

oil_price = 2
oil_demand = 10

Companies = [Company(starting_money) for i in range(n_comp)]
Wells = [Oil_Well(np.random.randint(max_oil), None) for i in range(n_wells)]

Networths = [[] for i in range(n_comp)]
Capitals = [[] for i in range(n_comp)]
well_check = np.array([Wells[i].oil for i in range(n_wells)])
Oil_Price = []

#plt.ion()

running = True
n_steps = 50

plt.figure(1)
plt.title('Networth')
plt.figure(2)
plt.title('Capital')
plt.figure(3)
plt.title('Price of Oil')

while running:
#for step in range(n_steps):

	oil_supply = 0

	for company in Companies:
		if np.random.randint(10) <= 5:
			well = Wells[np.random.randint(n_wells)]
			company.buy_well(well)

		company.pump_oil()
		oil_supply += company.sell_oil()

	for i, company in enumerate(Companies):
		company.evaluate()
		Networths[i].append(company.networth)
		Capitals[i].append(company.capital)

	for i, well in enumerate(Wells):
		well_check[i] = well.oil

	if np.sum(well_check) == 0: running = False

	oil_price += int((oil_demand - oil_supply) * 0.2)
	Oil_Price.append(oil_price)

	sys.stdout.write('Oil Supplied = {}   Price of oil = {}  Status: {}  \r'.format(oil_supply, oil_price, well_check))
	sys.stdout.flush()


for i, company in enumerate(Companies):
	plt.figure(1)
	plt.plot(Networths[i])
	plt.figure(2)
	plt.plot(Capitals[i])
plt.figure(3)
plt.plot(Oil_Price)
plt.show()
