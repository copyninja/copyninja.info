SPAKE2 in Golang: Implementing Groups in Golang
###############################################

:date: 2018-08-28 14:12 +0530
:slug: golang_spake2_5
:tags: go, golang, spake2, cryptography
:author: copyninja
:status: draft
:summary: Fifth post in "SPAKE2 in Golang" series. This post is my
          implementation notes for groups in Golang

In my `previous post <https://copyninja.info/blog/golang_spake2_4.html>`_ I
talked about SPAKE2 protocol and Ed25519 Curve group. This post is mostly
implementation notes and decisions taken during implementing EC groups and
number groups in Golang.

In the Beginning ...
====================

Like always I had too many question on how to do? what to do? etc. etc. Well
there is no definitive answer, you have to experiment to get the answer. So as a
first step I had to decide what I need. Looking at Python implementation of
SPAKE2 I noticed some basic group operations common for all groups. Some of them
are group operations listed below.

* Element Addition for the group
* Scalar Multiplication for the group
* Scalar Multiplication with Base point/Generator of group

Along with this I noticed some other functions which are needed, these are not
exactly group related operations, but are needed in SPAKE2 calculation.

* Convert password into Scalar of the group (Scalar is nothing but big integer
  in the group)
* Generate a Random scalar for the group.
* Constants M, N and S.
* Converting group element to bytes and creating element from bytes.
* Element Size for the group.

Now you might be wondering what `S` might be, as I only talked about `M` and `N`
while explaining SPAKE2. Brian has created a special mode called **Symmetric
Mode**. This is a special mode created by Brian Warner with help from other
cryptographic folks for **magic-wormhole** use case. This mode removes the
side/identity from the SPAKE2 protocol above (A, B) and makes both side
identical. This will reduce additional exchanges that had to be done to setup
side/identities for both peers.

Next question was whether SPAKE2 implementation is going to be Ed25519 group
specific or whether I plan to introduce other groups as well?. This was
important decision I had to make, since Python version also has some integer
groups I decided to make groups configurable in Golang as well.

Defininig Group Interface
=========================

To make group as configurable in SPAKE2 package I had to define a generic type.
Though Golang does not have generics, we can define *interface type* to get some
flexibility. As a first try I defined **Group** interface as follows

.. code:: go

   type Group interface {
          ConstM() Group
          ConstN() Group
          ConstS() Group

          RandomScalar() (*big.Int, error)
          PasswordToScalar(pw []byte) *big.Int

          ElementToBytes(ele Group) []byte
          ElementFromBytes(b []byte) Group

          BasePointMult(s *big.Int) Group
          Add(other Group) Group
          ScalarMult(s *big.Int) Group

          ElementSize() int
   }


Remember this was not final version which I reached but initial version. I kept
this under `group.go` file. I also thought it would be better to keep group
package outside SPAKE2. So I created SPAKE2 as
`salsa.debian.org/vasudev/gospake2` and Ed25519 group operations under
`salsa.debian.org/vasudev/ed25519group`.

I hit my first road block with this representation. I created a type `Ed25519`
in `ed25519group` package and implemented all above function but definitions
were returning/accepting type `Ed25519` wherever `Group` was needed. My
expectation was this should work because `Ed25519` confirms to `Group` interface
but Go compiler thought otherwise!. Go compiler refused to agree `Ed25519` type
implemented `Group` interface and told the defintion of functions do not match.
It said for ConstM, **expected return value of Group but found Ed25519**. I did
not get why this does not work but from my understanding of compilers, I think
when Go compiler scans ConstM line it still does not know that type `Ed25519`
implements `Group` interface. I could have asked in forums but frankly I did not
know how to phrase this question :). If you are a gopher and know the answer
please do let me know :).

So once I hit the road block I modified definition to look like

.. code:: go

   type Group interface {
          ConstM() interface{}
          ConstN() interface{}
          ConstS() interface{}

          RandomScalar() (*big.Int, error)
          PasswordToScalar(pw []byte) *big.Int

          ElementToBytes(ele interface{}) []byte
          ElementFromBytes(b []byte) interface{}

          BasePointMult(s *big.Int) interface{}
          Add(other interface{}) interface{}
          ScalarMult(s *big.Int) interface{}

          ElementSize() int
   }

So now compiler is happy because `interface{}` means any type.
