import numpy as np 
import scipy as sp
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt

inf = np.inf


class model(object):

	def __init__(self, reward, transfunc, discount):
		self.reward = reward
		self.transfunc = transfunc
		self.discount = discount


def backwards_recursion(f, P, delta, T, v_T1):

	for t in xrange(T):
		vt = np.max(f + delta * P * v_T1)
		xt = np.argmax(f + delta * P * v_T1)

		v_T1 = vt

	return vt, xt


def func_iteration(f, P, delta, tau, v):

	dv = tau

	while np.abs(dv) >= tau
		v_new = np.max(f + delta * P * v)
		dv = v_new - v
		v = v_new
	
	x = np.argmax(f + delta * P * v)

	return v, x


def policy_iteration(f, P, delta, v):

	x = np.argmax(f + delta * P * v)
	v = (np.identity(P.shape[0]) - delta * P[x]) * f[x]

	while np.abs(dv) >= tau
		v_new = np.max(f + delta * P * v)
		dv = v_new - v
		v = v_new
	
	x = np.argmax(f + delta * P * v)

	return v, x

def extraction(s, x):

	c = x**2 / (1 + s)
	return c


def get_index(s, S):

	try:
		return np.where(S == s)[0][0]
	except:
		return -inf


price = 1
sbar = 10
delta = 0.9

S = np.arange(sbar)
X = np.arange(sbar)

n = len(S)
m = len(X)

f = np.zeros((n, m))

print S
print X

for i in xrange(n):
	for k in xrange(m):
		if X[k] <= S[i]:
			f[i][k] = price * X[k] - extraction(S[i], X[k])
		else:
			f[i][k] = -inf

print f

g = np.zeros((n,m))

for i in xrange(n):
	for k in xrange(m):
		snext = S[i] - X[k]
		g[i][k] = get_index(snext, S)

print g
