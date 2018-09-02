SPAKE2 in Golang: Implementing Groups in Golang
###############################################

:date: 2018-09-02 17:14 +0530
:slug: golang_spake2_5
:tags: go, golang, spake2, cryptography
:author: copyninja
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
SPAKE2 some basic group operations needed are as follows.

* Element Addition for the group
* Scalar Multiplication for the group
* Scalar Multiplication with Base point/Generator of group

Along with this some other functions are needed, these are not exactly group
related operations, but are needed in SPAKE2 calculation. We can call them
helper operations and they are listed as follows.

* Convert password into Scalar of the group (Scalar is nothing but big integer
  in the group)
* Generate a Random scalar for the group.
* Constants M, N and S.
* Converting group element to bytes and creating element from bytes.
* Element Size for the group.
* Order of the subgroup

Now you might be wondering what `S` might be, as I only talked about `M` and `N`
while explaining SPAKE2. This is for a special mode called **Symmetric
Mode**. This special mode created by Brian Warner with help from other
cryptographic folks for **magic-wormhole** use case. This mode removes the
side/identity from the SPAKE2 protocol as we saw in previous post (A, B) and
makes both side identical. This will reduce additional exchanges that had to be
done to setup side/identities for both peers.

Next question was whether SPAKE2 implementation is going to be Ed25519 group
specific or whether I plan to introduce other groups as well?. This was
important decision I had to make, since Python version also has some integer
groups I decided to make groups configurable in Golang as well with Ed25519 as
default group.

Defining Group Interface
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
implementations outside SPAKE2. So I created SPAKE2 as
`salsa.debian.org/vasudev/gospake2` Ed25519 group operations under
`salsa.debian.org/vasudev/ed25519group` and integergroup operations under
`salsa.debian.org/vasudev/integergroup`.

I hit my first road block with this representation. I created a type `Ed25519`
in `ed25519group` package and implemented the `Group` interface above but
instead of function accepting/returning `Group` I used `Ed25519`. This felt
natural to me as `Ed25519` was confimring to `Group` interface but that Go
compiler thought otherwise. Go compiler refused to agree `Ed25519` type
implemented `Group` interface and told the defintion of functions do not match.
For eg. it said for ConstM, **expected return value of Group but found
Ed25519**. I did not yet figure out why this does not work, but as far as I can
understand this happens because when Go compiler scans ConstM line it still does
not know that type `Ed25519` implements `Group` interface. I could have asked in
forums but frankly I did not know how to phrase this question :). If you are a
gopher and know the answer please do let me know :).

Without spending too much time to figure out why its not working, I changed the
interface definition to look like below.

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

So now compiler is happy because `interface{}` means any type. Though I was not
happy because I had to do lot of type assertions in the actual implementation of
group.

After I did first version of ed25519group and successfuly used it in gospake2
0.1.0, I was feeling something was not correct and things needs to be improved.
Then when I started to implement `integergroup` package things started becoming
more clear to me. I finished writing `integergroup` with same interface
definition as above.

After both groups are implemented and integrated into gospake2, I started to
look at python code moe carefully. A pattern started emerging in my mind. Python
code was structured to differentiate Group and its elements, and this seemed
natural separation. Once you separat Elements your interface definition will
become more simpler.

So after struggling a bit I wrote a new interface, now differentiating Elements
and Group itself. The final code as of writing this post is below.

.. code:: go

   // Element represents the operation that needs to be satisfied by Group element.
   type Element interface {
	Add(other Element) Element
	ScalarMult(s *big.Int) Element
	Negate() Element
   }

   // Group defines methods that needs to be implemented by the number / elliptic
   // curve group which is used to implement SPAKE2 algorithm
   type Group interface {
	// These functions are not really group operations but they are needed
	// to get the required group Element's needed for calculation of SPAKE2
	ConstM() Element
	ConstN() Element
	ConstS() Element

	// This operation is needed to get a random integer in the group
	RandomScalar() (*big.Int, error)

	// This operation is for converting user password to a group element
	PasswordToScalar(pw []byte) *big.Int

	// These operations are group operations
	BasePointMult(s *big.Int) Element
	Add(a, b Element) Element
	ScalarMult(a Element, s *big.Int) Element

	ElementToBytes(e Element) []byte
	ElementFromBytes([]byte) (Element, error)

	// This operation should return size of the group
	ElementSize() int

	// This operation returns order of subgroup
	Order() *big.Int
   }


Element interface requires implementer to implement `Add`, `ScalarMult` and
`Negate` function. Group interface also has `Add` and `ScalarMult` operation but
Group functions require you to pass Element as input and returns Element as
output. Though it may be redundant it gives a natural organization to code.

With new interface new group implementations don't have to do too much type
assertions but there will still be some which can't be avoided (eg. Element to
actual type).


Packages, Subpackages and....
=============================

Well there is no such thing called subpackage in Go, this is one of the learning
I had while writing *gospake2* and related *group* implementation. I first
created the *Group* interface in file called `group.go` which was under
`salsa.debian.org/vasudev/gospake2` package. So to refer Group interface I just
need to import gospake2 and refer it as `gospake2.Group`. In the beginning this
seemed correct approach as I did not directly refer the `Group` interface in the
first versions of `ed25519group` and `integergroup`. (The version where I used
`interface{}` extensively). But when I refactored to have 2 interfaces above I
got cyclic dependency error. ed25519group and integergroup both referred
gospake2.Group and gospake2 referred these groups.

So to fix the error I moved the interface declaration from *group.go* to
*groups* folder under gospake2 package, and made it package *groups*. Few
points I learned while doing this is

* Even if the package is inside your package you can't directly use it. i.e.
  there is no such thing as subpackage. gospake2 had to refer groups with its
  full namespace i.e. `salsa.debian.org/vasudev/gospake2/groups`
* Folder structure inside package does not directly relate to each other, its
  just placing them in meaningful path like `crypto/sha256` and `crypto/sha512`
  they do not mean they are related its just that they fall under cryptography.
* Standard library can refer to interface in parent package, for example
  `crypto/ecdsa` can refer to `crypto.SignerOpts` interface which is defined in
  crypto package just by importing "crypto" inside ecdsa package. This works
  because *crypto* is package name in GOPATH, but there is nothing special here.
  For us to refer something in so called parent package we need to use fullpath
  for example `salsa.debian.org/vasudev/gospake2/groups` because that is how
  user packages are namespaced under GOPATH.

So finally I got a proper layout for `Group` and `Element` interfaces, its now
available under `salsa.debian.org/vasudev/gospake2/groups` package. If you
intend to provide a new group implementation for gospake2 you need to implement
these interfaces in your package.

Implementing Ed25519 Group
==========================

Implementing Ed25519 group was a bit of adventurous journey. First I searched
for ready made implementation if any. Only thing I found was
`golang.org/x/crypto/ed25519/internal/edwards25519` which is port of DJB's
original C code to Go by Adam Langley. Problem was this package was
internal to `ed25519` package and Go compiler would refuse to allow you import it
outside the ed25519 package. So I decided to embed *edwards25519* as a internal
package with in `gospake2`. This was prior to second version of `Group` interface
design.

Even with embedding I could not really use it properly. I could get the
BasePointMult operation working but nothing else worked and naively I tried to
use `ScMulAdd` for Scalar multiplication which was really a wrong thing to do.
Later I understood that the module was specifically written for Ed25519
signature scheme. Though it might still be possible to use it now that I've
understood the basics of curve, I will definitely give it a second try at later
point in time.

After the failed attempt with edwards25519 Ramakrishnan suggested me to use big
integer and implement those methods myself and finally that is what I did. I
used `math/big` package to implement the operations required myself. So the
experience of writing this module taught me a lot. Below are few of my
learnings.

Annoyance with big.Int
----------------------

While using big.Int I was annoyed by the specific syntax which invovled invoking
the operation using a big.Int variable which will set the result to same
variable and additionally return same value also. This design felt redundant to
me and also I had to create so many intermediate variables to get operations
like Add or Double implemented. Are you thinking why?. Then look at below
formula for Add to add 2 points `P1 = (X1,Y1,T1,Z1)` and `P2 = (X2, Y2, T2. Z2)`

.. code:: python

   A = (Y1-X1)*(Y2-X2)
   B = (Y1+X1)*(Y2+X2)
   C = T1*k*T2
   D = Z1*2*Z2
   E = B-A
   F = D-C
   G = D+C
   H = B+A
   X3 = E*F
   Y3 = G*H
   T3 = E*H
   Z3 = F*G

With big.Int I had to create every intermediate variable and then calculate
their result, for eg. (Y1-X1) and (Y2 - X2) and then finally calculate A. At
this point I started liking C++ more as it will allow me to override + operator
;-). But at later point I noticed some Go code where people dealt with the
big.Int in following format

.. code:: go

   Y1MX1 := new(big.Int).Sub(Y1, X1)
   Y2MX2 := new(big.Int).Sub(Y2, X2)
   A := new(big.Int).Mul(Y1MX1, Y2MX2)

It reduced intermediate variables to some extent, additionally it avoids
declaring required variables first and then use it. But still its bit of
annoyance :).

Confusions with Pointers
------------------------

When using local variables of type big.Int and returning a pointer to
it, I started to have a doubt that if what I'm doing is correct. Being from C
background where you are not supposed to be returning pointer to a stack
variable, Go's ability to return address of local variable confused me. But it
looks like `Go compiler is smarter in this aspect
<https://stackoverflow.com/questions/38234487/go-returning-a-pointer-on-stack#38234526>`_.
Basically Go compiler does escape analysis to figure out if variable leaves
after function and if so it moves it to garbage collected heap. So basically as
Go programmer I need not bother on where my variables are allocated. Thats a
relief :).


Type Aliasing in Go
-------------------

Type aliasing in languages like Rust or C++ is a handy way to create alternate
name for previously created type. This just creates a new name for existing type
and you can still use the original types methods or variables. But this is not
the same case in Go. Go `language spec
<https://golang.org/ref/spec#Type_declarations>`_. clearly says that new type
does not derive anything from originl type. But compiler allows you to cast
to-and-fro from original to new type and vice versa.

I was bit by this as I did not knew about it. I created a alias for
ExtendedPoint type as Ed25519 to implement Group interface. But when I tried to
access original functions from ExtendedPoint I noticed this behavior. So I had
to write private conversion function just to cast types around.

Implementing Scalar Multiplication and stack exhaustion
-------------------------------------------------------

Implementing scalar multiplication was one of the last adventure I tackled in
the ed25519 group implementation. Scalar multiplication is multiplying a given
elliptic curve point with a large integer (otherwise called as scalar) limited
by subgroup order. Warner's python implementation was as follows

.. code:: python

  def scalarmult_element(pt, n): # extended->extended
    # This form only works properly when given points that are a member of
    # the main 1*L subgroup. It will give incorrect answers when called with
    # the points of order 1/2/4/8, including point Zero. (it will also work
    # properly when given points of order 2*L/4*L/8*L)
    assert n >= 0
    if n==0:
        return xform_affine_to_extended((0,1))
    _ = double_element(scalarmult_element(pt, n>>1))
    return _add_elements_nonunfied(_, pt) if n&1 else _

Though I don't exactly remember first version of my scalar multiplication
function, it was mimicking the python code in Go with big.Int. The code worked
well with small integers but when I gave big numbers generated using
`RandomScalar` function of `Group` interface, code will panic as it will run out
of stack.

Above python code is slightly optimized version, so I looked at Haskell
implementation of SPAKE2 which looked like below

.. code:: haskell

   -- | Scalar multiplication parametrised by addition.
   scalarMultiplyExtendedPoint :: (ExtendedPoint a -> ExtendedPoint a -> ExtendedPoint a) -> Integer -> ExtendedPoint a -> ExtendedPoint a
   scalarMultiplyExtendedPoint _ 0 _    = extendedZero
   scalarMultiplyExtendedPoint add n x
          | even n    = doubleExtendedPoint (scalarMultiplyExtendedPoint add (n `div` 2) x)
          | n == 1    = x
          | n <= 0    = panic $ "Unexpected negative multiplier: " <> show n
          | otherwise = add x (scalarMultiplyExtendedPoint add (n - 1) x)

So algorithm is like this

1. If scalar is 1 return same point
2. If scalar is 0 return identity element for group
3. If scalar is even then recursively call scalarmult by reducing the scalar to
   half and double the result.
4. Otherwise recursively scalarmultiply the point with scalar reduced by 1 and
   add the result to the point.

It might look slightly confusing explanation so I will just show the code below.

.. code:: go

   func (e *ExtendedPoint) ScalarMultSlow(s *big.Int) ExtendedPoint {
	if s.Cmp(big.NewInt(0)) == 0 {
		return Zero
	}

	if s.Cmp(big.NewInt(1)) == 0 {
		return *e
	}

	var result ExtendedPoint
	if IsEven(s) {
		// If scalar is even we recursively call scalarmult with n/2 and
		// then double the result.
		result = e.ScalarMultSlow(new(big.Int).Rsh(s, 1))
		result = result.Double()
	} else {
		// We decrement the scalar and recursively call scalarmult with
		// it then we add the result with point
		result = e.ScalarMultSlow(new(big.Int).Sub(s, big.NewInt(1)))
		result = AddUnified(&result, e)
	}

	return result
   }

So instead of dividing by 2 I just right shift the scalar by 1 which is faster
operation. (AddUnified  is one of the algorithm for point addition which is more
safer but slower alternative, hence the name ScalarMultSlow.)

So this implementation works with every input, except the negative one for which
I modified ScalarMult definition in Group level to reduce input scalar to
subgroup order L. Otherwise Group function just calls function from Element.
Code below.

.. code:: go

   // ScalarMult multiples given point with scalar and returns the result
   func (e Ed25519) ScalarMult(a group.Element, s *big.Int) group.Element {
	// First let's reduce s to curve order, this is important in case if we
	// pass negated value
	s.Mod(s, L)
	if s.Cmp(big.NewInt(0)) == 0 {
		return Zero
	}

	extendedPoint := a.(ExtendedPoint)
	result := extendedPoint.ScalarMult(s)
	return result
   }

Probably I shoud move reducing the scalar to subgroup order into scalarmult
inside Element's implementation.

Implementing Integer Group
==========================

Given the problems I faced and things I learnt, implementing Ed25519 group,
implementing integer group was much straight forward. Only some design decisions
had to be made.

How to Represent Group and Elements
-----------------------------------

Unlike Ed25519 where group elements are basically points on the curve, element
in multiplicative integer groups are basically integers. So how do I represent
various integer groups?. Various integer groups are differentiated by bit length
of elements in it, group and subgroup order. Looking at python code I created a
structure called `GroupParameters` which will contain necessary information for
a given group.

.. code:: go

   type GroupParameters struct {
          p, q, g *big.Int
          elementSizeBytes, elementSizeBits, scalarSize int
   }

I did not want to export these fields as they are not useful outside the
package. Python code implemented 3 integer group of 1024,2048 and 3072 bit
integers. All values for above variables were taken from `NIST document
<http://csrc.nist.gov/groups/ST/toolkit/documents/Examples/DSA2_All.pdf>`_.

In first iteration I only had a struct called `IntegerGroup` which had
parameters as member and implemented `Group` interface from gospake2. But when I
refactored Group interface to have Element interface refactoring the code for
integergroup became bit challenging. I introduced `IntegerElement` struct to
hold actual integer value, but since all operations needed access to order of
group I had to modify it to also contain parameters defined above. So final
definition of `IntegerGroup` and `IntegerElement` is as follows

.. code:: go

   type IntegerGroup struct {
          params *GroupParameters
   }

   type IntegerElement {
          params *GroupParameters
          e *big.Int
   }

Operations in `IntegerGroup` were simply calling functions from
`IntegerElement`. So its really redundant but to make sure I can distinguish
between both group and its element I had to use it in this form.

Scalar Multiplication and Addition Operations
---------------------------------------------

Since the integer groups are really multiplicative group, addition operation is
really a multiplication modulo p. Scalar multiplication is just exponentiation
modulo p. Since these operations are readily available in `math/big` I did not
had to do anything much for integer group. These operations in `IntegerElement`
are defined as follows.

.. code:: go

   // Add is actually multiplication mod `p` where `p` is order of the
   // multiplicative group
   func (i IntegerElement) Add(other group.Element) group.Element {
	a := i.e
	b := other.(IntegerElement).e

	if !i.params.equal(other.(IntegerElement).params) {
		panic("You can't add elements of 2 different groups")
	}

	result := new(big.Int).Mul(a, b)

	return group.Element(IntegerElement{params: i.params, e: result.Mod(result, i.params.p)})
   }

   // ScalarMult for multiplicative group is g^s mod p where `g` is group generator
   // and p is order of the group
   func (i IntegerElement) ScalarMult(s *big.Int) group.Element {
	reducedS := new(big.Int).Mod(s, i.params.q)
	return group.Element(IntegerElement{params: i.params, e: new(big.Int).Exp(i.e, reducedS, i.params.p)})
   }

Conclussion
===========

Well its been already a pretty long post, so without extending it more I would
like to say that I had lot of learning experience in writing the Go code to
implement these integer and ed25519 group. Main learnings were

1. There is no definite answer for any questions, may it be how to write a
   library or if I structured my library correctly. Of course there will be some
   best practice available but you have to start at some point and then improve
   it in iteration.
2. Go provides great tooling especially linters and formatters which makes you
   write a clean code. And also document all your exported functions as you
   write (else you will keep seeing warnings in your editor which is annoying).
3. Use your library yourself and you will see how you can improve it. If you are
   feeling uncomfortable with your own written API then that means others will
   too :).
4. Every language is designed for a specific purpose, if I'm feeling discomfort
   using some features of the language (I had problems with verbose error
   handling) then probably I'm less experienced with language and should see how
   others handle such things. There are many good projects which you can refer
   to and lern from.

In the next post which should be last in series I will write about design
decisions I made writing gospake2 package. Code for both ed25519 and integer
groups are now merged into gospake2 as that is the right place for them. You can
find the code for them in my `gospake2 repo
<https://salsa.debian.org/vasudev/gospake2>`_.
