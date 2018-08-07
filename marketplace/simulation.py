import numpy as np
import matplotlib.pyplot as plt

import sys, os

from agents import reproduce, citizen, miller, farmer, marketplace

Marketplace = marketplace(10, 2, 1)
n_days = 500

field_cost = 50
mill_cost = 100
citizen_cost = 25 

tot_crops = [Marketplace.tot_crops]
tot_food = [Marketplace.tot_food]

prod_crops = [Marketplace.tot_prod_crops]
prod_food = [Marketplace.tot_prod_food]

con_crops = [Marketplace.tot_con_crops]
con_food = [Marketplace.tot_con_food]

crop_prices = [Marketplace.crops_price]
food_prices = [Marketplace.food_price]

citizens_pop = [len(Marketplace.citizens)]

citizens_money = [np.sum([agent.money for agent in Marketplace.citizens])]
farmers_money = [np.sum([agent.money for agent in Marketplace.farmers])]
millers_money = [np.sum([agent.money for agent in Marketplace.millers])]

food_traded = [0]
crops_traded = [0]
employment_farm = [0]
employment_mill = [0]

for n in range(n_days):

	for farmer in Marketplace.farmers:
		farmer.check_status()
		farmer.employ_workers()
		farmer.buy_fields(field_cost)

	for miller in Marketplace.millers:
		miller.check_status()
		miller.employ_workers()
		miller.buy_mills(mill_cost)

	Marketplace.trade()

	for agent in Marketplace.citizens: 
		agent.consume_food()
		agent.check_status(citizen_cost)

	if len(Marketplace.citizens) == 0: break

	#Marketplace.assess_prices()
	Marketplace.assess_totals()
	Marketplace.assess_workforce()

	tot_crops.append(Marketplace.tot_crops)
	tot_food.append(Marketplace.tot_food)

	prod_crops.append(Marketplace.tot_prod_crops)
	prod_food.append(Marketplace.tot_prod_food)

	con_crops.append(Marketplace.tot_con_crops)
	con_food.append(Marketplace.tot_con_food)

	crop_prices.append(Marketplace.crops_price)
	food_prices.append(Marketplace.food_price)

	citizens_pop.append(len(Marketplace.citizens))

	citizens_money.append(np.mean([agent.money for agent in Marketplace.citizens]))
	farmers_money.append(np.mean([agent.money for agent in Marketplace.farmers]))
	millers_money.append(np.mean([agent.money for agent in Marketplace.millers]))

	food_traded.append(Marketplace.food_traded)
	crops_traded.append(Marketplace.crops_traded)
	employment_farm.append(len(np.argwhere(Marketplace.job_list == 'farm')) / len(Marketplace.citizens))
	employment_mill.append(len(np.argwhere(Marketplace.job_list == 'mill'))  / len(Marketplace.citizens))

plt.figure(0)
plt.plot(crop_prices, label='crops')
plt.plot(food_prices, label='food')
plt.legend()
plt.savefig('prices.png')

plt.figure(1)
plt.plot(tot_crops, label='crops')
plt.plot(tot_food, label='food')
plt.legend()
plt.savefig('totals.png')

plt.figure(2)
plt.plot(prod_crops, label='crops')
plt.plot(prod_food, label='food')
plt.legend()
plt.savefig('production.png')

plt.figure(3)
plt.plot(con_crops, label='crops')
plt.plot(con_food, label='food')
plt.legend()
plt.savefig('consumption.png')

plt.figure(4)
plt.plot(citizens_pop)
plt.savefig('population.png')

plt.figure(5)
plt.plot(employment_farm, label='farm')
plt.plot(employment_mill, label='mill')
plt.legend()
plt.savefig('employment.png')

plt.figure(6)
plt.plot(food_traded)
plt.plot(crops_traded)
plt.savefig('trade.png')

plt.figure(7)
plt.plot(citizens_money, label='citizens')
plt.plot(farmers_money, label='farmers')
plt.plot(millers_money, label='millers')
plt.legend()
plt.savefig('money.png')