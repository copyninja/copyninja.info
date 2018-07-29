SPAKE2 In Golang: Finite fields of Elliptic Curve
#################################################

:date: 2018-07-29 19:02 +0530
:slug: golang_spake2_3
:tags: go, golang, spake2, cryptography, ecc
:author: copyninja
:status: draft
:summary: Third post in SPAKE2 in Golang. This post is my notes on finite fields
          in elliptic curve group.

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

Couple of difference we see are all operations are now `modulo p` where p is the
order of finite field.Division operations earlier are all now replaced with
multiplication with *multiplication inverse*.

Scalar Multiplication and Cyclic Group
--------------------------------------

Now if we consider scalar multiplication we discussed above with finite fields,
we get some thing called *cyclic subgroups*. Considering a point `P` in the
finite field, if we add 2 multiples of point `P` we get another multiple of
point `P` (i.e. multiples of `P` are closed under addition). Hence set of
multiples of P is a cyclic subgroup.

.. math::

   nP + mP = \underbrace{P + \cdots + P}_{n\ \text{times}} + \underbrace{P +
   \cdots + P}_{m\ \text{times}} = (n + m)P
