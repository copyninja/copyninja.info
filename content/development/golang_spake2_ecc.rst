SPAKE2 In Golang: Elliptic Curves Primer
########################################

:date: 2018-07-28 13:22 +0530
:slug: golang_spake2_2
:tags: go, golang, spake2, cryptography, ecc
:author: copyninja
:summary: Second post in series SPAKE2 in Golang, my notes on Elliptic curves
          and groups

..

    TLDR; this post is going to be too long and mostly theoretical. If you are
    wondering about where is Go in all these posts, please wait for few more
    posts before I can write about the actual implementation.


In my `previous post <https://copyninja.info/blog/golang_spake2_1.html>`_ I
talked about starting of my new adventure to write a cryptographic library and
how I tried to brute force to solve problem without knowing basics. In this post
I'll talk about my learning of *Elliptic Curves and their Groups*. This post is
just my notes and I'm not trying to explain all basics or mathematics behind the
Elliptic curves.

Ramakrishnan gave me a good article to start with Elliptic curves. Its a series of
posts by *Andrea Corbellini*, which starts with `Elliptic Curve Cryptography: A
Gentle Introduction
<http://andrea.corbellini.name/2015/05/17/elliptic-curve-cryptography-a-gentle-introduction/>`_.
These posts gave me a great deal of understanding about elliptic curves and how
elliptic curve cryptography works, and why its faster. If you want to learn
about elliptic curve I highly recommend you to go through the series.

Elliptic Curves
===============

Elliptic curves are set of points described by equation

.. math::
   y^2 = x^3 + ax + b

where `a` and `b` are the coefficients which needs to satisfy :math:`4a^3 + 27b^2
\neq 0`. This form of equation is called *Weirstrass normal form of elliptic
curves*.

Along with normal point there is also point on curve which is considered ideal
point and is *point at infinity*; it is denoted by symbol 0. So considering
point at infinity we can define elliptic curve as

.. math::

   \{(x,y) \in \mathbb R ^2 | y^2 = x^3 + ax + b, 4a^3 + 27b^2 \neq 0 \} \cup  \{0\}


Groups
======

Before going to Elliptic curve groups we need to know what are groups. I now
remembered my academics where I had studied about groups and number theory in
general. That time never knew where exactly it was useful. And I should really
say learning something without knowing its application is really difficult.
Moving on to the groups,

A group in mathematics is basically a set for which there is a binary operation
which is called as *"addition"* and idicated with + symbol. In order for set
:math:`\mathbb G` the binary operation must be defined so that it has following
properties.

1. **closure**: if `a` and `b` are members of of :math:`\mathbb G` then
   :math:`a + b` is also member of :math:`\mathbb G`.
2. **associativity**: :math:`(a + b) + c = a + (b + c);`
3. there exists an **identity element** 0 such that :math:`a + 0 = 0 + a = a;`
4. Every element has a inverse, that is for every `a` there exists `b` such that
   :math:`a + b = 0`

For a group to be Abelian there is a 5th rule.

5. **commutativity**: :math:`a + b = b + a`

If a group satisfies we get some additional property such that **unique identity
element** and **unique inverse element** which is either directly or indirectly
very important.

Elliptic Curve Groups
---------------------

Similar to number groups we defined above, its possible to have group over
elliptic curves. Following are the property or rule for a Elliptic curve groups.

1. Elements of the groups are point on elliptic curve;
2. the **identity element** is the point at infinity; yes the one we described
   above while defining elliptic curves.
3. the **inverse** of a point :math:`\mathrm R` is the one symmetric on
   `x-axis`. i.e. if point is :math:`(x,y)` then inverse of the point is
   :math:`(x, -y)`

4. **adition** is given by the rules: **given three aligned, non-zero points,**
   :math:`\mathrm P,Q` **and** :math:`\mathrm R` **their sum is**
   :math:`P + Q + R = 0`.
   This means the line through the 3 point passes through the point at infinity.
5. For addition we want 3 points to be aligned and does not require any specific
   order which means
   :math:`P + (Q + R) = Q + (P + R) = R + (P + Q) = ... = 0` that is **our +
   operator is both associative and commutative**

By point 5 we conclude that Elliptic curve groups are *Abelian*.

Algebraic Addition
------------------

Since we know :math:`P + Q + R = 0` we can say :math:`P + Q = -R`. This means we
draw a line on elliptic curve which passes through point `P` and `Q` it
intersects the curve at 3rd point `R`. Inverse of point `R` is `-R` and is the
result of addition of 2 points `P` and `Q`.  This is easy geometrically but for
computers, we need to represent this with algebraic notation. This is where the
*slope of line* comes to picture, another academic topic which I learnt without
actually knowing its real world application.

So considering point `P` as :math:`(x_P,y_P)` and `Q` as :math:`(x_Q, y_Q)` we
can calculate slope of line going from `P` to `Q` as follows

.. math::

   m = \frac{y_P - y_Q}{x_P - x_Q}

And in a special case where :math:`P = Q` formula is slightly different

.. math::

   m = \frac{3x_P^2 + a}{2y_P}

Intersection of this line with curve is point `R` :math:`(x_R,y_R)` and point
:math:`x_R` and :math:`y_R` are calculated using following formula.

.. math::

   x_R = m^2 - x_P - x_Q

   y_R =
   \begin{cases}
   y_P + m(x_R - x_P), & \text{or} \\
   y_Q + m(x_R - x_Q)
   \end{cases}

I've not mentioned about special cases of elliptic curve additions which is
explained in `Andrea Corbellini
<http://andrea.corbellini.name/2015/05/17/elliptic-curve-cryptography-a-gentle-introduction/>`_
blog. Please refer for more mathematical oriented explanation.

Scalar Multiplication
---------------------

One more important operation we do with elliptic curve group is scalar
multiplication. It allows you to calculate :math:`nP` where `n` is a natural
number. Scalar multiplication can be implemented using addition as follows.

.. math::

   nP = \underbrace{P + P + \cdots + P}_{n\ \text{times}}

This property is what makes elliptic curves attractive and faster than the
normal integer groups where scalar multiplication is actually exponentiation
operation.

If we see scalar multiplication formula above, we see that it requires `n`
addition, which can be :math:`O(n)` operation or, if we consider `n` as `k` bit
integer then algorithm will be :math:`O(2^k)`which looks highly inefficient when
`n` is large prime number.

But there is another algorithm which is much faster for this purpose, its called
**double and add** you can find `wikipedia article on it
<https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication>`_. First I
did not understand this, but after a while of struggling, and trying to
implement it myself it became pretty clear. It works with first taking binary
representation of `n` :math:`n = n_0 + 2n_1 + 2^2_n2 + ...+2^kn_k` where
:math:`[n_0..n_k] \in \{0,1\}`. Below is pseudo code for the recursive version
of algorithm.

.. code:: python

   def scalarmult(P, n):
          if n == 1:
              return P # identity element
          if n & 1:
              # n is odd we add point
              return point_add(P, scalarmult(P, n - 1)
          else:
              return scalarmult(point_double(P), n >> 1) # we double point and multiply by n/2

Let's consider an example to understand what is this algorithm doing. Lets say
we want to caculate `21P`. First thing is we denote `21` as binary string
`10101` now skipping all those 0's and consider only the 1's, so we will have
:math:`2^4 + 2^2 + 2^0`. Now if we multiply P to this representation. So this
algorithm calculates `21P` as :math:`16P + 4P + P`.

If we consider doubling and adding as constant operations i.e. :math:`O(1)` then
this algorithm will be :math:`O(\log n)` (in above 21 can be calculated in 3
operations which is :math:`\log 21`) which is much better than earlier
:math:`O(n)` algorithm.

Given `n` and `P` we can easily cacluate :math:`Q = nP` but given `Q` and `P`
there is no *easy* way to find `n` especially when numbers are big. This is the
*"hard"* problem or the *discrete logarithm problem* which makes cryptography
work.

Conclusion
==========

So I learned now about Elliptic curves, its group and operations like scalar
multiplication and addition. But this is not directly useful, we need to learn
about **Finite Fields** and **Elliptic Curve over Finite Field** and many more
concepts before we can go to actual implementation!. I thought of writing finite
field as part of this post, but then I've already written a lot and there is no
point in expanding this post more. So finite fields, cyclic groups will be part
of next post.

As a closing note, if you are wondering why there is no mention of anything
about Go, you need to wait a bit more for my actual implementation notes in
Golang. I would like to write down entire learning process rather than directly
jumping to implementation. So please bare with me :-).
