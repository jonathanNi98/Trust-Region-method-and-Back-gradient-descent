# -*- coding: utf-8 -*-


Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VlmCu-qPkRS-tZ7y5PoZZw7bs0Ma10NJ
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import cvxpy as cp

import matplotlib.pyplot as plt

# %matplotlib inline

from pdb import set_trace

from numpy.lib.function_base import gradient
# Backtracking line search for GD 
def backtrack(z, f, grad, mu, alp = 2, beta = 0.5):    
    '''
    Input: 
        z:     Current location
        f:     Objective function 
        grad:  Gradient 
        alp:   Warm start parameter
        beta:  Step size decay parameter 
        mu:    Step size from previous iteration

    Output: 
        mu: step size 
    '''    
    mu = alp*mu 
    flag = 1
    while( flag == 1):
      temp1 = f( z - mu * grad )
      temp2 = f(z) - 0.5 * mu * np.linalg.norm(grad)**2
      if(temp1 < temp2):
        flag = 0
        break
      mu = beta * mu
    ##TODO: Implement Backtrack line search 
    ## 
    ## 
        
    return mu

# Implementation of Gradient Descent with backtracking line search
def BGD(x0, gradf, fun=lambda z: 0, niter=1000,eps=1e-6):    
    '''
    Input: 
        x0:  intilalization 
        gradf:  gradient function takes position argument 
        fun: objective function
        niter: Number of iterations 

    Itermediate: 
        grad: Gradient
        mu:   Step size, initialized as 1       
    Output: 
        z: final solution 
        out: objective values per iterations 
    '''
    out = np.empty(niter + 1)
    z = x0.copy() 
    out[0] = fun(z)
    mu = 1
    for itr in range(niter):
    ##TODO: Implment proximal gradient descent with backtracking line search
    ## 
    ## 
      grad = gradf(z)
      mu = backtrack(z, fun, grad, mu)
      z = z - mu * grad
      out[itr + 1] = fun(z)

      if np.abs(out[itr + 1] - out[itr]) <= eps:
        break

    return z, out[:itr+1]

# Implementation of Power method for eigen vector computation
def PM(A, ninner=1000, eps=1e-6):
    '''
    Input: 
        A0:     Matrix of interest (N by N)
        niter: Maximum number of iterations
        eps:   Tolerance 
    Intermediate: 
        N:     Number of columns of A
    Output: 
        u1:  leading eigen vector (unique up to sign) 
    '''   
    N = A.shape[1]
    M = A.shape[0]
    A2 = (A.T).dot(A)
    X2 = np.random.uniform(size = (N,1), low = 0, high = 1)
    X2_prev = X2

    for itr in range(ninner):
      X2 = np.dot(A2,X2_prev)/np.linalg.norm(np.dot(A2,X2),2)
      if np.linalg.norm(X2 - X2_prev , 2)/ np.linalg.norm(X2_prev,2) < eps:
        break
      X2_prev= X2

    ##TODO: Implement Power method to find leading eigen vector
    ## 
    ## 
    return X2

#Trusted Region Subproblem
def TRM_sub(f_q, block_m, delta):
    '''
    Input:
        f_q:     qudratic approximation to the objective function, takes direction -> approximation
        delta:   Trust region radius 
        block_m: The block matrix used for SDP
    Intermediate: 
        X:       CVX variable 
    Output: 
        dr:      Direction vector 
    '''
    X = cp.Variable(block_m.shape,symmetric=True)
    constraints = [X >> 0,X[-1,-1] == 1,cp.trace(X) <= delta**2 + 1]

    prob = cp.Problem(cp.Minimize(cp.trace(block_m.T @ X)),constraints)
    prob.solve()
  
    v1 = PM(X.value)
    dr = v1[:-1]/ v1[-1,0]
    if(f_q(-dr) < f_q(dr)):
      dr = -dr
  

    ##TODO: Solving the TRM subproblem is SDP and cvx solver 
    ##Note: There is a sign ambiguity for the leading eigen vector    
    ##            choose the sign with smaller f_q value (i.e bigger descent)
    return dr

#Trusted Region Method 
def TRM(x0, gradf, hessf, fun = lambda z:0, niter=1000, delta=0.1, eta_s = 0.2, eta_vs = 0.8, gamma_i=2, gamma_d=0.5, eps=1e-6): 
    '''
    Input:
        x0:      Intilalization         
        gradf:    Gradient function of objective function: takes location -> Gradient Vector
        hessf:    Hessian function of Objective function:  takes location -> Hessian Matrix
        fun:     Objective function
        niter:   maximum umber of iterations
        rho:     quality of reduction 
        delta:   Trust region radius 
        eta_vs:  Threshold if rho>eta_vs fun approximation is considered very successful
        eta_s:   Threshold if rho<eta_s fun approximation is considered unsuccessful 
        gamma_i: Parameter increases delta
        gamma_d: Parameter decreases delta 
        
    Intermediate:
        grad :   Gradient for current iterate 
        hess :   Hessian Matrix for current iterate
        block_m: The block matrix used for SDP
        dr:      moving direction 
        fun_q:   qudratic approximation to the objective function, takes direction -> approximation
        
    Output: 
         out: objective values per iterations 
         x:      Estimated parameter 
    '''
    x = x0.copy()
    out = np.empty(niter+1)
    out[0] = fun(x)
    for itr in range(niter):

      grad = gradf(x)
      hess = hessf(x)

      block_m = np.block([[ hess,grad],[ grad.T, 2* fun(x)]])
      f_q = lambda z: fun(x) + np.dot(z.T, grad) + 0.5 * np.dot(z.T, np.dot(hess,z))

      d = TRM_sub(f_q, block_m, delta)
      rho = (fun(x) - fun(x+d))/(fun(x) - f_q(d))
      if rho > eta_vs:
        x = x + d
        delta = gamma_i * delta
      elif rho > eta_s:
        x = x + d
      else:
        delta = gamma_d * delta
      save = fun(x)
      save = save.reshape(-1)
  
      out[itr+1] = save

      if np.abs(out[itr+1] - out[itr]) <= eps:
        break


    ##TODO: Solving the TRM subproblem is SDP and cvx solver 
    ## 
    ##Note: You may find np.block function useful 
    ## 
    return x, out[:itr+1]

np.random.seed(0)

n = 5
m = 50
x_true = np.random.randn(n,1)

A = np.random.randn(n,m)

y = (A.T@x_true)**2

# print(y.shape)
# print(A.shape)
# print(x_true.shape)

# Obj  = lambda x: 1/(4*m) * np.sum( np.square(   y -  np.square(x.T.dot(A))) )      #TODO: Fill in the Objective function, parameter -> hessian matrix at the position
# Grad = lambda x: 1/m * A.dot ( np.power(x.T.dot(A) , 3) - y * x.T.dot(A) )#TODO: Fill in the Gradient function, parameter -> hessian matrix at the position
Obj  = lambda z: 1/ (4*m) * np.sum(np.square(y - np.square(A.T.dot(z))))
Grad = lambda z: 1/m * A.dot(np.power(A.T.dot(z), 3) - y*(A.T.dot(z)))
Hess = lambda z: 1/m * (A*(3*np.square(A.T.dot(z))-y).T).dot(A.T)


x_grad, out_BGD = BGD(np.ones((n,1)), gradf = Grad, fun = Obj)
x_TRM, out_TRM = TRM(np.ones((n,1)), gradf = Grad,  hessf = Hess, fun = Obj)

print(out_TRM)
print(len(out_TRM))
print(out_BGD)
print(len(out_BGD))


# Converence to the optimal value 
plt.plot(np.arange(len(out_TRM)-1),np.log10(np.array(out_TRM[:-1]-out_TRM[-1])),'b')
plt.plot(np.arange(len(out_BGD)-1),np.log10(np.array(out_BGD[:-1]-out_BGD[-1])),'r')

plt.legend((r'TRM', r'BGD'), loc = 'upper right')
plt.show()
print(1)
