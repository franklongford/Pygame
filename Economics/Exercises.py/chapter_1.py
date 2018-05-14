import numpy as np 
import scipy as sp
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt


"Question 1.1"

def function(x): return 1 - np.exp(2 * x)

x = np.linspace(-1, 1, 200)
y = function(x)

plt.figure(1)
plt.title("Question 1.1")
plt.plot(x, y)
plt.show()

"Question 1.2"

A = np.array([[0, -1, 2], [-2, -1, 4], [2, 7, -3]])
B = np.array([[-7, 1, 1], [7, -3, -2], [3, 5, 0]])
y = np.array([3, -1, 2])

C = np.dot(A, B)
x = np.dot(y, np.linalg.inv(C))

print C, x
assert np.sum(np.dot(C, x) - y) <= 1E-5

C = A * B
x = np.dot(y, np.linalg.inv(C))

print C, x
assert np.sum(np.dot(C, x) - y) <= 1E-5

"Question 1.3"

def linear(x, m, c):

	return m * x + c

def function_t(t):

	ep_t = np.random.normal(0, 0.2)
	return 5 + 0.05 * t + ep_t

time = np.arange(100)
y_t = [function_t(t) for t in time]

popt, pcov = curve_fit(linear, time, y_t)

print popt

y_fit = linear(time, popt[0], popt[1])

plt.figure(2)
plt.title("Question 1.3")
plt.scatter(time, y_t)
plt.plot(time, y_fit)


"Question 1.4"

def yield_():

	if np.random.rand() >= 0.5 : return 0.7
	else: return 1.3


def function_market(p):

	return 3 - 2 * (0.5 + 0.5 * p) * yield_()

def function_market_sup(p):

	return 3 - 2 * (0.5 + 0.5 * np.max([p, 1.])) * yield_()


max_time = 500
time = np.arange(max_time)

prices = np.zeros(max_time)
prices[0] = 20
for i in xrange(max_time-1):
	prices[i+1] = function_market(prices[i])

plt.figure(3)
plt.title("Question 1.3 a")
plt.scatter(time, prices)

print np.mean(prices), np.var(prices)

for i in xrange(max_time-1):
	prices[i+1] = function_market_sup(prices[i])

plt.figure(4)
plt.title("Question 1.3 b")
plt.scatter(time, prices)

print np.mean(prices), np.var(prices)

plt.show()
