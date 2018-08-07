import numpy as np
from numpy.random import rand, randint

def reproduce(agent, citizen_cost):
	if agent.food > citizen_cost:
		agent.market.citizens.append(citizen(agent.market, agent.money / 2, citizen_cost, agent.food_rate))

		agent.money /= 2
		agent.food -= citizen_cost


class citizen:

	def __init__(self, market, money, food, food_rate):

		self.agent_type = 'citizen'
		self.market = market
		self.money = money
		self.food = food
		self.days_starving = 0

		self.food_rate = food_rate
		self.employment = False
		self.employer = None
		self.role = 'unemployed'

	def consume_food(self):
		food_eaten = np.min([self.food, self.food_rate])
		if food_eaten == 0: self.days_starving += 1
		self.food -= food_eaten

	def check_status(self, citizen_cost):
		if (self.employment) and (self.food > citizen_cost): self.reproduce(citizen_cost)
		if self.days_starving > 5: self.die()

	def reproduce(self, citizen_cost):
		self.market.citizens.append(citizen(self.market, self.money / 2, citizen_cost, self.food_rate))
		self.money /= 2
		self.food -= citizen_cost

	def die(self):
		self.market.citizens.remove(self)
		if self.employment: self.employer.employees.remove(self)


class farmer:

	def __init__(self, market, money, n_field, crops=50):

		self.agent_type = 'farmer'
		self.market = market
		self.money = money
		self.n_field = n_field

		self.crops = crops
		self.field_prod = 1
		self.field_max = 5

		self.employees = []
		self.wage = 1

		self.prod = len(self.employees) * self.field_prod

	def grow_crops(self):

		new_crops = self.prod
		self.crops += new_crops

	def pay_employees(self):

		agent_wage = np.min([self.wage, self.money / len(self.employees)])

		for agent in self.employees:
			agent.money += agent_wage
			self.money -= agent_wage

	def check_status(self):

		self.prod = len(self.employees) * self.field_prod
		if self.prod > 0:
			self.grow_crops()
			self.pay_employees()

	def employ_workers(self):

		employees_needed = (self.n_field * self.field_max) - len(self.employees)
		employment_pool = np.where(self.market.employment_status == False)[0]

		if (employees_needed > 0) and (len(employment_pool) > 0):
			worker = np.random.choice(employment_pool)

			self.employees.append(self.market.citizens[worker])
			self.market.citizens[worker].employment = True
			self.market.employment_status[worker] = True
			self.employees[-1].employer = self
			self.employees[-1].role = 'farm'

	def buy_fields(self, field_cost):

		employees_needed = (self.n_field * self.field_max) - len(self.employees)

		if employees_needed == 0 and self.money > field_cost:
			self.n_field += 1
			self.money -= field_cost


class miller:

	def __init__(self, market, money, n_mill, food=20, crops=5):

		self.agent_type = 'miller'
		self.market = market
		self.money = money
		#self.factories = [factory(np.random.randint(100), np.random.randint(20), np.random.randint(10)) for n in range(n_factory)]
		self.n_mill = n_mill
		self.mill_prod = 5
		self.mill_max = 20
		self.crops_to_food = 0.5

		self.food = food
		self.crops = crops

		self.employees = []
		self.wage = 4

		self.prod = np.min([self.mill_prod * len(self.employees), self.crops * self.crops_to_food])

	def make_food(self):
		crops_used = np.min([self.crops, self.prod / self.crops_to_food])
		new_food = self.prod

		self.crops -= crops_used
		self.food += new_food

	def pay_employees(self):

		agent_wage = np.min([self.wage, self.money / len(self.employees)])

		for agent in self.employees:
			agent.money += agent_wage
			self.money -= agent_wage

	def check_status(self):

		self.prod = np.min([self.mill_prod * len(self.employees), self.crops * self.crops_to_food])

		if self.prod > 0:
			self.make_food()
			self.pay_employees()

	def employ_workers(self):

		employees_needed = (self.n_mill * self.mill_max) - len(self.employees)
		employment_pool = np.where(self.market.employment_status == False)[0]

		if (employees_needed > 0) and len(employment_pool) > 0:
			worker = np.random.choice(np.where(self.market.employment_status == False)[0])

			self.employees.append(self.market.citizens[worker])
			self.employees[-1].employment = True
			self.market.employment_status[worker] = True
			self.employees[-1].employer = self
			self.employees[-1].role = 'mill'


	def buy_mills(self, mill_cost):

		employees_needed = (self.n_mill * self.mill_max) - len(self.employees)

		if employees_needed == 0 and self.money > mill_cost:
			self.n_mill += 1
			self.money -= mill_cost


class marketplace:

	def __init__(self, n_citizen, n_farmer, n_miller):

		self.citizens = [citizen(self, randint(50), randint(50), 2 * rand()) for n in range(n_citizen)]
		self.farmers = [farmer(self, randint(200), randint(5)) for n in range(n_farmer)]
		self.millers = [miller(self, randint(1000), randint(2)) for n in range(n_miller)]

		self.population = n_citizen + n_farmer + n_miller

		self.crops_price = 1
		self.food_price = 5

		self.assess_totals()
		self.assess_workforce()

	def assess_totals(self):

		self.tot_crops = np.sum([agent.crops for agent in self.millers + self.farmers])
		self.tot_food = np.sum([agent.food for agent in self.citizens + self.millers])
		self.tot_money = np.sum([agent.money for agent in self.citizens + self.millers + self.farmers])

		self.tot_prod_crops = np.sum([agent.prod for agent in self.farmers])
		self.tot_prod_food = np.sum([agent.prod for agent in self.millers])

		self.tot_con_crops = np.sum([np.min([agent.crops, agent.prod / agent.crops_to_food]) for agent in self.millers])
		self.tot_con_food = np.sum([np.min([agent.food, agent.food_rate]) for agent in self.citizens])

		self.population = len(self.citizens + self.farmers + self.millers)

	def assess_prices(self):

		food_needed = np.sum([agent.food_rate for agent in self.citizens])
		crops_needed = np.sum([(agent.prod / agent.crops_to_food) for agent in self.millers])

		self.crops_price = 10 / (np.exp(- crops_needed / self.tot_crops + 1) + 1)
		self.food_price = 10 / (np.exp(- food_needed / self.tot_food + 1) + 1)

	def assess_workforce(self):

		self.employment_status = np.array([agent.employment for agent in self.citizens])
		self.job_list = np.array([agent.role for agent in self.citizens])

	def trade(self):

		self.food_traded = 0
		self.crops_traded = 0
		n_trade = self.population

		for n in range(self.population):
			citizen = np.random.choice(self.citizens)
			miller = np.random.choice(self.millers)

			max_food =  np.floor(citizen.money / self.food_price)
			food_sold = np.min([miller.food, max_food])

			citizen.food += food_sold
			miller.food -= food_sold

			miller.money += food_sold * self.food_price
			citizen.money -= food_sold * self.food_price

			self.food_traded += food_sold

		for n in range(len(self.millers + self.farmers)):
			farmer = np.random.choice(self.farmers)
			miller = np.random.choice(self.millers)

			max_crops =  int(miller.money / self.crops_price)
			crops_sold = np.min([farmer.crops, max_crops])

			farmer.crops -= crops_sold
			miller.crops += crops_sold

			miller.money -= crops_sold * self.crops_price
			farmer.money += crops_sold * self.crops_price

			self.crops_traded += crops_sold
