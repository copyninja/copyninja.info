SPAKE2 in Golang: ECDH, SPAKE2 and Curve Ed25519
################################################

:date: 2018-08-28 11:38 +0530
:slug: golang_spake2_4
:tags: go, golang, spake2, cryptography, ecc
:author: copyninja
:summary: Fourth post in SPAKE2 in Golang series. This post is my notes on
          ECDH, SPAKE2 and curve Edwards25519 group

In my `previous post <https://copyninja.info/blog/golang_spake2_3.html>`_  I
talked about finite field and how it helps in *Elliptic Curve Cryptography*. In
this post we will see briefly how Diffie-Hellmann key exchange varies with use
of *Elliptic curve* groups, then we will see SPAKE2 original variant followed by
Elliptic curve version and finally we will have a look at curve Ed25519 which is
used as default group in *python-spake2* module.

Elliptic Curve Diffie-Hellman (ECDH)
====================================

In the previous post we defined the domain parameter of elliptic curve
cryptography as :math:`(p, a, b, G, n, h)`. Now we will see how we use this in
Diffie-Hellman Key exchange.

Diffie-Hellman key exchange is a way to securely exchange cryptographic key over
public channel. Original Diffie-Hellman protocol used **multiplicative group of
integers modulo p** where `p` is the a large prime and `g` a generator for
subgroup (as we saw in earlier post). The protocol can be explained as follows

1. Alice and Bob agrees on `p` and `g` belonging to group `G`
2. Alice selects `a` belonging to `G` and calculates :math:`A = g^a \bmod{p}`
3. Bob selects `b` belonging to `G` and calculates :math:`B = g^b \bmod{p}`
4. Alice sends Bob `A`
5. Bob sends Alice `B`
6. Now Alice calculates :math:`s = B^a \bmod{p}`
7. Now Bob calculates :math:`s = A^b \bmod{p}`

Mathematically `s` computed by both Alice and  Bob are same and hence both
share a shared secret now.

.. math::

   s = B^a \bmod{p} = g^{ba} \bmod{p} = A^b \bmod{p} = g^{ab} \bmod{p}


Now in ECC,

1. private key :math:`d` is a random integer choosen from :math:`\{1, \dots, n -
   1\}` where `n` is the order of subgroup
2. public key is the point :math:`H = dG` where `G` is the base point of
   subgroup.

With above now we can write Diffie-Hellman key exchange as

1. Alice selects private key :math:`d_A` and public key :math:`H_A = d_AG` and
   sends it to Bob
2. Bob selects private key :math:`d_B` and public key :math:`H_B = d_BG` and
   sends it to Alice
3. Alice calculates :math:`S = d_AH_B` and Bob calculates :math:`S = d_BH_A`
   which if you see carefully is one and same and Alice and Bob now share a
   secret key!.

.. math::

   S = d_A H_B = d_A (d_B G) = d_B (d_A G) = d_B H_A


In both cases observer only sees the public key and will not be able to find
discrete logarithm (hard problem), given the numbers are large prime.

Advantage of ECDH is its faster as its replacing the costly exponentiation
operation with *scalar multiplication* without reducing hardness of the problem.

SPAKE2 Protocol
===============

Now that we understood Diffie-Hellman exchange and saw how to apply Elliptic
curve in Diffie-Hellman exchange, lets see what is SPAKE2 protocol. This paper
by `Abdalla and Pointcheval
<https://www.di.ens.fr/~pointche/Documents/Papers/2005_rsa.pdf>`_ gives full
explanation of SPAKE2 and proof of its security. I highly recommend reading the
paper as I can only summarize my understadning here.

SPAKE2 is a variation of Diffie-Hellman problem we described above. Domain
parameters for SPAKE2 are :math:`(G, g, p, M, N, H)`

* `G` is the group
* `g` is the generator for group
* `p` is the big prime which is order of group
* :math:`M, N \in G` and are selected by Alice and Bob respectively
* `H` is the hash function used to derive final shared key.

Along with this SPAKE2 both side will have common password :math:`pw \in Z_p`.
Protocol is defined as follows

1. Alice selects a random scalar :math:`x \xleftarrow{R} Z_p` and
   calculates :math:`X \leftarrow g^x`.
2. Alice then computes :math:`X^* \leftarrow X \cdot M^{pw}`
3. Bob selects a random scalar :math:`y \xleftarrow{R} Z_p` and calculates
   :math:`Y \leftarrow g^y`.
4. Bob then computes :math:`Y^* \leftarrow Y \cdot N^{pw}`.
5. :math:`X^*, Y^*` are called pake messages and are sent to other side. i.e.
   Alice sends :math:`X^*` to Bob and Bob sends :math:`Y^*` to Alice.
6. Alice computes :math:`K_A \leftarrow (Y*/N^{pw})^x` and Bob computes :math:`K_B
   \leftarrow (X^*/M^{pw})^y`
7. Shared Key is calculated by Alice as :math:`SK_A \leftarrow
   H(A,B,X^*,Y^*,pw,K_A)` and Bob computes :math:`SK_B \leftarrow H(A,B,X^*,Y^*,
   pw, K_B)`

:math:`SK_A = SK_B` because mathematically value :math:`K_A = K_B` (you can
expand :math:`X^*` and :math:`Y^*` in step `6` aboveand see that they are really
same).

In step `7` we calculate Hash of transcript, where `A` and `B` are identities of
Alice and Bob. and rest is calculated during protocol execution.

One thing to note here is paper does not define what are identities or which
hash function is used. This allows some creativity from implementer side to
choose things. For *python-spake2* interoperability *Brian* has written a
`detailed blog post <http://www.lothar.com/blog/57-SPAKE2-Interoperability/>`_
describing decision he has taken for all these points which are not defined in
original paper.


Curve Ed25519 Group
===================

Now that we have seen the SPAKE2 protocol, we will next see the use of Elliptic
Curve groups in it and see how it varies.

SPAKE2 uses *Abelian Group* with large number of "elements". `Brian Warner
<http://lothar.com/blog/>`_ has choosen elliptic curve group *Ed25519* (some
times also referred as X25519) as default group in *python-spake2*
implementation. This is the same group which is used in *Ed25519 signature
scheme*. The difference between multiplicative integer group modulo p and
elliptic curve group is that, element in integer group is just a number but in
elliptic curve group its a point. (represented by 2 co-ordinates).

Curve Ed25519 is a *twisted Edwards curve*, defined in affine form as
:math:`ax^2 + y^2 = 1 + dx^2y^2` where :math:`d \in k\{0,1\}`.

* :math:`q = 2^{255} - 19` is the order of curve group
* :math:`l = 2^{252} + 27742317777372353535851937790883648493` is the order of
  curve subgroup.
* :math:`a = -1`
* :math:`d = \frac{-121665}{121666}`
* Base point :math:`B` is unique and has y-co-ordinate `:math:4/5` and x
  co-ordinate is positive.

Curve itself is given as :math:`E/\mathbb F_q`

.. math::

   -x^2 + y^2 = 1 - \frac{121665}{121666} x^2y^2

This curve is birationally equivalaent to the Montgomery curve known as
*Curve25519*. If you are wondering what *25519* is?, well its in the order of
group i.e. :math:`2^{255} - 19`.

Till now we were working with elliptic curves with affine co-ordinates, i.e.
each point is represented as :math:`(x,y)`. But for fast operation twisted
edwards curve introduces new type of co-ordinates called *Extended Co-ordinates*
where *x, y* is represented as *X,Y,T and Z*, and affine co-ordinates are
represented using the extended co-ordinates as follows

.. math::

   x = X/Z \\
   y = Y/Z \\
   x*y = T/Z \\

Initial base point is converted to extended co-ordinate using `Z` as 1. In all
above case the operations are :math:`mod q`. Additionally all division
operations are actually multiplication with inverse of element.

We also noted above, Base point represented using only y co-ordinate. This is
because x co-ordinate can be recovered from y, using twisted edwards curve
equation we defined above. In most of libraries you will see that this
compressed notation of representing a point as just `y` co-ordinate is used.
(Its called *CompressedEdwardsY* in Rust's *curve25519-dalek* crate.)

In all above case the operations are :math:`mod q`. Additionally all division
operations are actually multiplication with inverse of element.Inverse of a
element is calculated as point raised to power `q-2` modulo `q`. I could not
find the technical/mathematical reason behind this. If some one knows please let
me know. So the inverse operation can be mathematically defined as follows.

.. math::

   x^{-1} = x^{q - 2} \bmod{q}

The addition and doubling operations are as per algorithms defined in
`hyperelliptic.org post
<http://www.hyperelliptic.org/EFD/g1p/auto-twisted-extended-1.html>`_. We have
seen scalar multiplication in `second post of this series
<https://copyninja.info/blog/golang_spake2_2.html>`_, which depends on addition
and doubling operation.


SPAKE2 using Ed25519 group
--------------------------

Unlike normal elliptic curve here the domain parameters are slightly different.
Ed25519 domain parameters are defined as :math:`(q, d, B, l)` where `q` gives
the order of elliptic curve group and `l` is the order of subgroup. `B` is the
base point of the group.

Now lets rewrite original SPAKE2 protocol using elliptic curve groups

1. Alice selects a random scalar :math:`x \xleftarrow{R} E/\mathbb F_q` and calculates
   :math:`X \leftarrow B \cdot x` and computes :math:`X^* \leftarrow X + M \cdot
   pw`. Alice sends :math:`X^*` to Bob.
2. Bob selects random scalar :math:`y \xleftarrow{R} E/\mathbb F_q` and
   calculates :math:`Y \leftarrow B \cdot y` and computes :math:`Y^* \leftarrow
   Y + N \cdot pw`. Bob sends :math:`Y^*` to Alice.
3. Alice now calculates :math:`K_A \leftarrow (Y^* - N \cdot pw) \cdot x`
4. Bob now calculates :math:`K_B \leftarrow (X^* - M \cdot pw) \cdot y`
5. Shared key is calculated by Alice :math:`SK_A \leftarrow H(A, B, X^*, Y^*,
   pw, K_A)` and by Bob :math:`SK_B \leftarrow H(A,B, X^*, Y^*, pw, K_B)`

In 3 and 4 if you expand :math:`X^*` and :math:`Y^*` you will see that
:math:`K_A = K_B`. And given password used by both sides are same we will arrive
at same shared key.

As you see above protocol for SPAKE2 remains same only things what changed from
earlier is operations, exponentiation is changed to multiplication and division
to substraction. Since we do not explicitly define substraction what we do is
negate the password and do addition instead.

Conclusion
==========

So we now have seen all the basics needed to start writing the actual Go code to
implement SPAKE2 library. It was bit long I know but if you know the basics
writing code is a cake walk!. (quoting from Ramakrishnan). So in the next post I
will start writing implementation notes.
