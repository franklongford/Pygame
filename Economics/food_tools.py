import numpy as np
import scipy as sp
import os, sys, random

import matplotlib.pyplot as plt


def calc_price(av_price, seller_stock, buyer_stock, seller_money, buyer_money):

	stock_factor = (buyer_stock - seller_stock) / (buyer_stock + seller_stock)
	money_factor = (buyer_money - seller_money) / (buyer_money + seller_money)

	stock_factor = buyer_stock / seller_stock
	money_factor = buyer_money / seller_money

	print (stock_factor + money_factor)

	price = av_price * (1 + 0.1 * (stock_factor + money_factor))

	return price


class Society(object):

	def __init__(self, n_farmers, n_blacksmiths, n_landowners, food_price, tool_price):
		self.landowners = [Landowner(self, 20, 200, 0.2) for i in range(n_landowners)]
		self.farmers = [Farmer(self, random.choice(self.landowners), 10, 5, 20) for i in range(n_farmers)]
		self.blacksmiths = [Blacksmith(self, random.choice(self.landowners), 10, 5, 50) for i in range(n_blacksmiths)]
		self.population = self.farmers + self.blacksmiths + self.landowners
		self.food_price = food_price
		self.tool_price = tool_price
		self.calc_totals()
		self.food_sales = []
		self.tool_sales = []

	def update_status(self):

		self.calc_totals()
		self.calc_prices()

	def calc_totals(self):

		self.total_food = 0
		self.total_tools = 0

		self.supply_food = 0
		self.supply_tools = 0

		self.demand_food = 0
		self.demand_tools = 0

		for farmer in self.farmers:
			self.total_food += farmer.food
			self.total_tools += farmer.tools
			self.supply_food += farmer.food
			self.demand_tools += farmer.tools_needed
		for blacksmith in self.blacksmiths:
			self.total_food += blacksmith.food
			self.total_tools += blacksmith.tools
			self.supply_tools += blacksmith.tools
			self.demand_food += blacksmith.food_needed
		for landowner in self.landowners:
			self.total_food += landowner.food
			self.demand_food += landowner.food_needed


	def calc_prices(self):

		#if len(self.food_sales) > 0: self.food_price += np.mean(self.food_sales) - self.food_price
		#if len(self.tool_sales) > 0: self.tool_price += np.mean(self.tool_sales) - self.tool_price

		if self.supply_food > 0: self.food_price = self.demand_food / self.supply_food
		if self.supply_tools > 0: self.tool_price = self.demand_tools / self.supply_tools


class Farmer(object):

	def __init__(self, society, landowner, food, tools, money):
		self.society = society
		self.landowner = landowner
		self.tools = tools
		self.food = food
		self.money = money
		self.tools_needed = int(1. / food_per_tool + 0.5)
		if self.tools_needed == 0: self.tools_needed = 1

	def make_food(self, conversion):
	
		food_made = int(conversion * self.tools_needed)
		if self.tools > self.tools_needed:
			self.food += food_made
			self.tools -= self.tools_needed

	def buy_tools(self, agent, order):

		if agent.tools > 0:
			price = calc_price(self.society.tool_price, agent.tools, self.tools, agent.money, self.money)
			tools = order
			#tools = int(order * (0.9 + 0.1 * self.society.tool_price / price))
			if self.money >= price:

				self.tools += tools
				agent.tools -= tools

				taxes = agent.landowner.tax * price
				self.money -= price 
				agent.money += price - taxes
				agent.landowner.money += taxes

				self.society.tool_sales.append(price)


class Blacksmith(object):

	def __init__(self, society, landowner, food, tools, money):
		self.society = society
		self.landowner = landowner
		self.tools = tools
		self.food = food
		self.money = money
		self.food_needed = int(1. / tool_per_food + 0.5)
		if self.food_needed == 0: self.food_needed = 1

	def make_tools(self, conversion):
		
		tools_made = int(conversion * self.food_needed)
		if self.food > self.food_needed:
			self.food -= self.food_needed
			self.tools += tools_made

	def buy_food(self, agent, order):

		if agent.food > 0:
			price = calc_price(self.society.food_price, agent.food, self.food, agent.money, self.money)
			food = order
			#food = int(order * (0.9 + 0.1 * self.society.food_price / price))
			if self.money >= price:

				self.food += food
				agent.food -= food

				taxes = agent.landowner.tax * price
				self.money -= price
				agent.money += price
				agent.landowner.money += taxes

				self.society.food_sales.append(price)


class Landowner(object):

	def __init__(self, society, food, money, tax):
		self.society = society
		self.food = food
		self.money = money
		self.tax = tax
		self.food_needed = int(1. / tool_per_food + 0.5)
		if self.food_needed == 0: self.food_needed = 1

	def eat_food(self):
		self.food -= 5
		if self.food < 0:
			self.food = 0

	def buy_food(self, agent, order):

		if agent.food > 0:
			price = calc_price(self.society.food_price, agent.food, self.food, agent.money, self.money)
			food = order
			#food = int(order * (0.9 + 0.1 * self.society.food_price / price))
			if self.money >= price:

				self.food += food
				agent.food -= food

				taxes = agent.landowner.tax * price
				self.money -= price
				agent.landowner.money += taxes

				self.society.food_sales.append(price)


food_per_tool = 5
tool_per_food = 1

n_farmers = 1
n_blacksmiths = 1
n_landowners = 1

n_turns = 100

order_size = 1

World = Society(n_farmers, n_blacksmiths, n_landowners, 5, 5)

Food_Price = [World.food_price]
Tool_Price = [World.tool_price]

Total_Food = [World.total_food]
Total_Tools = [World.total_tools]

Farmer_Money = [[farmer.money] for farmer in World.farmers]
Blacksmith_Money = [[blacksmith.money] for blacksmith in World.blacksmiths]
Landowner_Money = [[landowner.money] for landowner in World.landowners]

for turn in xrange(n_turns):

	World.food_sales = []
	World.tool_sales = []

	for farmer in World.farmers:
		farmer.make_food(food_per_tool)
	for blacksmith in World.blacksmiths:
		blacksmith.make_tools(tool_per_food)
	for landowner in World.landowners:
		landowner.eat_food()

	for farmer in World.farmers:
		for blacksmith in World.blacksmiths:
			farmer.buy_tools(blacksmith, 1)
			blacksmith.buy_food(farmer, 2)

	for landowner in World.landowners:
		for farmer in World.farmers:
			landowner.buy_food(farmer, 5)

	World.update_status()

	Food_Price.append(World.food_price)
	Tool_Price.append(World.tool_price)
	Total_Food.append(World.total_food)
	Total_Tools.append(World.total_tools)

	for i, farmer in enumerate(World.farmers):
		Farmer_Money[i].append(farmer.money)
	for i, blacksmith in enumerate(World.blacksmiths):
		Blacksmith_Money[i].append(blacksmith.money)
	for i, landowner in enumerate(World.landowners):
		Landowner_Money[i].append(landowner.money)


plt.figure(1)
plt.title('Prices')
plt.plot(Food_Price, label='food')
plt.plot(Tool_Price, label='tools')
plt.legend()
plt.figure(2)
plt.title('Totals')
plt.plot(Total_Food, label='food')
plt.plot(Total_Tools, label='tools')
plt.legend()
plt.figure(3)
plt.title('Farmer Money')
for i, farmer in enumerate(World.farmers):
	plt.plot(Farmer_Money[i])
plt.figure(4)
plt.title('Blacksmith Money')
for i, blacksmith in enumerate(World.blacksmiths):
	plt.plot(Blacksmith_Money[i])
plt.figure(5)
plt.title('Landowner Money')
for i, landowner in enumerate(World.landowners):
	plt.plot(Landowner_Money[i])
plt.show()
