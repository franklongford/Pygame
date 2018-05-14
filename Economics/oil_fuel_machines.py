import numpy as np
import scipy as sp
import os, sys

import matplotlib.pyplot as plt


def calc_price(av_price, seller_stock, buyer_stock, seller_money, buyer_money):

	price = av_price + 0.1 * (seller_stock - seller_money + buyer_money - buyer_stock)
	return price
	

class Society(object):

	def __init__(self, n_farmers, n_blacksmiths, n_landowners):
		self.farmers = [Farmer(self, 2, 10, 20) for i in range(n_farmers)]
		self.blacksmiths = [Blacksmith(self, 10, 5, 30) for i in range(n_blacksmiths)]
		self.landowners = [Landowner(self, 100, 200) for i in range(n_landowners)]
		self.population = self.farmers + self.blacksmiths + self.landowners


class Farmer(object):

	def __init__(self, society, tools, food, money):
		self.society = society
		self.tools = tools
		self.food = food
		self.money = money

	def make_food(self, conversion):
		tools_needed = int(1. / conversion) + 1
		if self.tools > tools_needed:
			self.food += int(rate * tools_needed)
			self.tools -= tools_needed

	def buy_tools(self, agent, tools):

		price = calc_price(tool_price, agent.tools, self.tools, agent.money, self.money)

		if self.money >= price:
			self.tools += tools
			agent.tools -= tools
			self.money -= price
			agent.money += price

			tool_sales.append(price)


class Blacksmith(object):

	def __init__(self, society, tools, food, money):
		self.society = society
		self.tools = tools
		self.food = food
		self.money = money

	def make_tools(self, rate):
		food_needed = int(1. / rate) + 1
		if self.food > food_needed:
			self.food -= food_needed
			self.tools += int(rate * food_needed)

	def buy_food(self, agent, food):

		price = calc_price(food_price, agent.food, self.food, agent.money, self.money)

		if self.money >= price:

			self.food += food
			agent.food -= food
			self.money -= price
			agent.money += price

			food_sales.append(price)


class Landowner(object):

	def __init__(self, society, food, money):
		self.society = society
		self.food = food
		self.money = money

	def eat_food(self):
		self.food -= 1

	def buy_food(self, agent, food):

		price = calc_price(food_price, agent.food, self.food, agent.money, self.money)

		if self.money >= price:

			self.food += food
			agent.food -= food
			self.money -= price
			agent.money += price

			food_sales.append(price)


food_price = 2
tool_price = 10

food_per_tool = 5
tool_per_food = 0.5

n_farmers = 10
n_blacksmiths = 5
n_landowners = 1

n_turns = 10

order_size = 5

World = Society(n_farmers, n_blacksmiths, n_landowners)

Food_Price = []
Tool_Price = []

for turn in xrange(n_turns):

	food_sales = []
	tool_sales = []

	for farmer in World.farmers:
		farmer.make_food(food_per_tool)
	for blacksmith in World.blacksmiths:
		blacksmith.make_tools(food_per_tool)

	for farmer in World.farmers:
		for blacksmith in World.blacksmiths:
			farmer.buy_tools(blacksmith, order_size)
			blacksmith.buy_food(farmer, order_size)

	for landowner in World.landowners:
		for farmer in World.farmers:
			landowner.buy_food(farmer, order_size)

	Food_Price.append(np.mean(food_sales))
	Tool_Price.append(np.mean(tool_sales))

plt.plot(Food_Price)
plt.plot(Tool_Price)
plt.show()
