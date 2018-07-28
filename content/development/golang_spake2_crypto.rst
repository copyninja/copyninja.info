SPAKE2 In Golang: Journey to Cryptoland begins
##############################################

:date: 2018-07-22 22:07 +0530
:slug:  golang_spake2_1
:tags: go, golang, spake2, cryptography, ecc, magic-wormhole
:author: copyninja
:summary: My notes on SPAKE2 implementation in Golang, my first Golang and
          cryptographic library


..

   This or the series of SPAKE2 related posts are inspired from `Jonathan
   Lange's <https://jml.io>`_ `series on SPAKE2
   <https://jml.io/tag/spake2.html>`_ when he ported it to Haskell, which is
   also the reference I used for my implementation in Golang.


Brief Background
================

Before I can go to detail I should tell why/how I came to implementing SPAKE2 in
Golang. Story starts a couple of month back when I started contributing to
`*magic-wormhole.rs* <https://github.com/warner/magic-wormhole.rs>`_, a Rust port
of original Python project of magic-wormhole. You can read `this LWN article
<https://lwn.net/Articles/692061/>`_ to understand more about what
magic-wormhole is.

During contribution my friend `Ramakrishnan Muthukrishnan
<https://rkrishnan.org/>`_ said to me that I should try to port the
magic-wormhole to Golang. I was not a expert Go programmer but had understanding
of language basics and thought why not use it to improve my language
understanding. And this is where it all started.

What is SPAKE2 why is it used?
==============================

At this point we need to know why SPAKE2 is needed and how magic-wormhole uses
it. `SPAKE2 <http://www.di.ens.fr/~mabdalla/papers/AbPo05a-letter.pdf>`_ is
*Simple Password Authenticated Key Exchange* protocol. It allows 2 parties
having a shared weak password to derive a strong shared key which can then be
used by the parties to setup a encrypted+authenticated channel between them.

*magic-wormhole* uses SPAKE2 to negotiate a shared session key between
communicating parties which is then used by magic-wormhole to derive different
keys needed for different *purpose*.

So I hit my first road block after agreeing to implement the *magic-wormhole* in
Golang, there is no SPAKE2 implementation readily available in Go!.

Enter Cryptography and My knowledge about it
============================================

Ram convinced me that its easy to implement SPAKE2 in Go and I agreed. But my
knowledge on cryptography was limited. I knew Cryptography is

* basically math with big numbers and relies on fact that factoring big prime
  number is hard for computers.
* These big numbers are derived from *Abelian Group* and related concepts from
  number theory, which I have studied in academics but since I've never learnt a
  practical use case for them, its eating dust some where inside my memory.

I've taken some theoretical course on Cryptography but never thought of
implementing one myself. With these weak foundation I set out for a new
adventure.

Python SPAKE2 Implementation
----------------------------

Since magic-wormhole is implemented in python, SPAKE2 implementation in Python
is considered as reference for other language implementation. SPAKE2 paper does
not specify much about where or how the requirement public constants are
defined, so implementer can take liberty at defining those. Python code uses 2
groups one is *Twisted Edwards Curve* group *Ed25519* and others are
multiplicative group over Integer of 1024, 2048 and 3072 bits.

In Python code Warner himself has defined Ed25519 and other Integer group and
related operations. In Rust code though there is only Ed25519 group but its
created using *curve25519-dalek* library. Haskell code also defines the group
operations  by itself instead of depending on any other libraries (possibly
Cryptonite). So as a first step I started for searching any library equivalent
to *curve25519-dalek*  as I've no clue what is an Elliptic curve.(forget groups
I don't know basic itself).

First Try, Bruteforce
---------------------

I've this bad habit of tackling problem with brute force; some times it works but
most time it just exhausts me, taking me nowhere. So with my normal habit I
started looking for Ed25519 curve operations library. (Without actually knowing
what operations are and how it works). I tried to read through
*curve25519-dalek* but invain, nothing entered into my head. I found *ed25519*
package for Go written by *Adam Langley* but eventually it turned out to be
actually a signature package. I found an internal package defined in *ed25519*
package called *edwards25519*, which seem to have some operations defined but I
was unable to understand it nor figure out why its made internal. I later even
took a dig at embedding *edwards25519* as part of my implementation of ed25519
group but finally had to drop it for my own version that story will be part of
another post in this series.

Conclusion
==========

During all these I was constantly in talk with Ram and first thing he told me
was to slow down a bit and go from scratch. And that's what was the learning
point for me. In short I can say the following.

..

  Nothing can be done in single day, before you code understand the basic
  concepts and then build it from there. As they say you can't build a stable
  house on weak foundation.

In the next post in this series I will write about my learning on Elliptic
Curves and Elliptic curve groups, followed by experiment with number groups and
finally learning and decision I had to make in writing *gospake2*.
