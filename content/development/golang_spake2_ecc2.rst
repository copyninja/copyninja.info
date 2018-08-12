SPAKE2 In Golang: Finite fields of Elliptic Curve
#################################################

:date: 2018-08-12 22:51 +0530
:slug: golang_spake2_3
:tags: go, golang, spake2, cryptography, ecc
:author: copyninja
:summary: Third post in SPAKE2 in Golang. This post is my notes on finite fields
          in elliptic curve group.


In my `previous post <https://copyninja.info/blog/golang_spake2_2.html>`_ I
talked about elliptic curve basics and how the operations are done on elliptic
curves, including the algebraic representation which is needed for computers.
For usage in cryptography we need a elliptic curve group with some specified
number of elements, that is what we called **Finite Fields**. We limit Elliptic
Curve groups with some big prime number `p`. In this post I will try to briefly
explain *finite fields over elliptic curve*.


Finite Fields
=============

*Finite field* or also called *Galois Field* is a set with finite number of
elements. An example we can give is *integer modulo `p`* where `p` is prime.
Finite fields can be denoted as :math:`\mathbb Z/p, GF(p)` or :math:`\mathbb
F_p`.

Finite fields will have 2 operations addition and multiplications. These
operations are closed, associative and commutative. There exists a unique
identity element and inverse element for every element in the set.

Division operation in finite fields is defined as :math:`x / y = x \cdot y^{-1}`,
that is x multiplied by inverse of y. and substraction :math:`x - y` is defined
in terms of addition as :math:`x + (-y)` which is x added by negation of y.
Multiplicative inverse can be *easily* calculated using `extended Euclidean
algorithm <http://en.wikipedia.org/wiki/Extended_Euclidean_algorithm>`_  which
I've not understood yet myself as there were readily available library functions
which does this for us. But I hear from Ramakrishnan that its very easy one.

Elliptic Curve in :math:`\mathbb F_p`
-------------------------------------

Now we understood what is finite fields we now need to restrict our elliptic
curves to the finite field. So our original definition of elliptic curve becomes
slightly different, that is we will have `modulo p` to restrict the elements.

.. math::

   \begin{array}{rcl}
   \left\{(x, y) \in (\mathbb{F}_p)^2 \right. & \left. | \right. & \left. y^2 \equiv x^3 + ax + b \pmod{p}, \right. \\
   & & \left. 4a^3 + 27b^2 \not\equiv 0 \pmod{p}\right\}\ \cup\ \left\{0\right\}
   \end{array}

All our previous operations can now be written as follows

.. math::

   \begin{array}{rcl}
   x_R & = & (m^2 - x_P - x_Q) \bmod{p} \\
   y_R & = & [y_P + m(x_R - x_P)] \bmod{p} \\
   & = & [y_Q + m(x_R - x_Q)] \bmod{p}
   \end{array}

Where slope, when :math:`P \neq Q`

.. math::

   m = (y_P - y_Q)(x_P - x_Q)^{-1} \bmod{p}

and when :math:`P = Q`

.. math::

   m = (3 x_P^2 + a)(2 y_P)^{-1} \bmod{p}

So now we need to know *order* of this finite field. *Order* of elliptic curve
finite field can be defined as **number of points in the finite field**. Unlike
*integer modulo p* where number of elements are *0 to p-1*, in case of elliptic
curve you need to count points from `x` to `p-1`. This counting will be
:math:`O(p)`. Given large `p` this will be *hard* problem. But there are faster
algorithm to count order of group, which even I don't know much in detail :).
But from my reference its called `Schoof's algorithm
<https://en.wikipedia.org/wiki/Schoof%27s_algorithm>`_.

Scalar Multiplication and Cyclic Group
--------------------------------------

When we consider scalar multiplication over elliptic curve finite fields, we
discover a special property. Taking example from `Andrea Corbellini's post
<http://andrea.corbellini.name/2015/05/23/elliptic-curve-cryptography-finite-fields-and-discrete-logarithms/>`_,
consider curve :math:`y^2 \equiv x^3 + 2x + 3 ( mod 97)` and point :math:`P =
(3,6)`. If we try calculating multiples of `P`

.. math::

  0P = 0 \\
  1P = (3,6) \\
  2P = (80,10) \\
  3P = (80,87) \\
  4P = (3, 91) \\
  5P = 0 \\
  6P = (3,6) \\
  7P = (80, 10) \\
  8P = (80, 87) \\
  9P = (3, 91) \\
  ...

If you are wondering how to calculate above (I did at first). You need to use
point addition formula from earlier post where `P = Q` with `mod 97`. So we
observe that there are only 5 multiples of P and they are repeating cyclicly. we
can write above points as

- :math:`5kP = 0P`
- :math:`(5k + 1)P = 1P`
- :math:`(5k + 2)P = 2P`
- :math:`(5k + 3)P = 3P`
- :math:`(5k + 4)P = 4P`

Or simply we can write these as :math:`kP = (k mod 5)P`. We also note that all
these 5 Points are closed under addition. This means **adding two multiples of P,
we obtain a multiple of P and the set of multiples of P form cyclic subgroup**


.. math::

   nP + mP = \underbrace{P + \cdots + P}_{n\ \text{times}} + \underbrace{P +
   \cdots + P}_{m\ \text{times}} = (n + m)P

Cyclic subgroups are foundation of Elliptic Curve Cryptography (ECC).

Subgroup Order
--------------

Subgroup order tells how many points are really there in the subgroup. We can
redefine the *order of group* in subgroup context as **order of P is the
smallest positive integer such that nP = 0**. In above case if you see we have
smallest `n` as `5` since `5P = 0`. So order of subgroup above is 5, it contains
5 element.

Order of subgroup is linked to order of elliptic curve by `Lagrange's Theorem
<https://en.wikipedia.org/wiki/Lagrange%27s_theorem_(group_theory)>`_ which says
**the order of subgroup is divisor of order of parent group**. Lagrange is
another name which I had read in my college, but the algorithms were different.

From this we have following steps to find out the order of subgroup with base
point `P`

1. Calculate the elliptic curve's order `N` using Schoof's algorithm.
2. Find out all divisors of `N`.
3. For every divisor of `n`, compute `nP`.
4. The smallest `n` such that `nP = 0` is the order of subgroup `N`.

Note that its important to choose smallest divisor, not a random one. In above
examples 5P, 10P, 15P all satisfy condition but order of subgroup is 5.

Finding Base Point
------------------

Far all above which is used in ECC, i.e. Group, subgroup and order we need a
base point `P` to work with. So base point calculation is not done at the
beginning but in the end i.e. first choose a order which looks good then look
for subgroup order and finally find the suitable base point.

We learnt above that subgroup order is divisor of group order which is derived
from *Lagrange's Theorem*.  This term :math:`h = N/n` is actually called
**co-factor of the subgroup**. Now why is this term co-factor important?.
Without going into details, this co-factor is used to find generator for the
subgroup as :math:`G = hP`.

Conclusion
===========

So now are you wondering why I went on such length to describe all these?. Well
one thing I wanted to make some notes for myself because you can't find all
these information in single place, another these topics we talked in my previous
post and this point forms the domain parameters of *Elliptic Curve
Cryptography*.

Domain parameters in ECC are the parameters which are known publicly to every
one. Following are 6 parameters

* Prime `p` which is order of Finite field
* Co-efficients of curve `a` and `b`
* Base point :math:`\mathbb G` the generator which is the base point of curve
  that generates subgroup
* Order of subgroup `n`
* Co-factor `h`

So in short following is the domain parameters of ECC :math:`(p, a, b, G, n, h)`

In my next post I will try to talk about the specific curve group which is used
in SPAKE2 implementation called **twisted Edwards curve** and give a brief
overview of SPAKE2 protocol.
