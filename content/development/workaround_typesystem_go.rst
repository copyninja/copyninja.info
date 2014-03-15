Working around type system of Go with unsafe
############################################

:date: 2014-03-12 22:22
:slug: workaround-gotypesystems
:tags: golang, go, programming	      
:author: copyninja
:summary: Working around Go type system and converting Go type to byte
	  slice and interacting with C types in  using unsafe package.

Go language has a strong type system unlike C, and some times this
will be head ache when we want to interact with C data types with Cgo
or just to convert a Go type to lets say byte slice. I recently faced
the same problem and after poking around things, I learned the Go
provides *unsafe* package which can be used to work around the Go's
type system. 

Problem
-------

Recently I started using *Cgo* to use some C library I had to write
some tools for development and testing. The reason I chose *Go* for
this was prototyping and writing some quick tools is much easier in Go
than done in C.

The C library had some function which takes pointer to array types and
fills it with some values. The problem I was facing here was how to
create a C array in Go. Go does have array but its largely used as
internal representation for much efficient type called *slice* and I
can't directly cast a byte slice into an C array.

Second problem I had was I had to store arbitrary Go types like float
(float32,float64) and int (int32, int64) etc. into C array.

So in brief, the problems that needed to solve are

1. Find a way to convert byte slice from Go into C array and vice
   versa.
2. Find a way to convert and store Go types into a C array.

Solution
--------

Basically C array are sequence of memory location which can be
statically or dynamically allocated. In *Cgo* its possible to access C
standard library functions for memory allocation, so why not use
it. The memory allocation function then returns the pointer to
starting of allocated memory, we can use this pointer to write Go's
bytes into the memory location and bytes from memory location into
Go's slice.

The pointer returned by C allocation functions are not directly usable
for memory dereferencing in Go, here is where *unsafe* package kicks
in. We will cast the return of C allocation function as
*unsafe.Pointer* type and from the documentation of unsafe package,

  1. A pointer value of any type can be converted to a Pointer.
  2. A Pointer can be converted to a pointer value of any type.
  3. A uintptr can be converted to a Pointer.
  4. A Pointer can be converted to a uintptr.

So we can then cast unsafe.Pointer to *uintptr* which is the Go type
which is large enough to hold any memory address in Go and can be used
for pointer arithmetic just like we do in C (of course with some more
castings).

Below I'm pasting a simplified code in C which I wrote for this
post.

.. code-block:: C

   #ifndef __BYTETEST_H__
   #define __BYTETEST_H__

   typedef unsigned char UBYTE;

   extern void ArrayReadFunc(UBYTE *arrayout);
   extern void ArrayWriteFunc(UBYTE *arrayin);

   #endif

.. code-block:: C

   #include "bytetest.h"
   #include <stdio.h>
   #include <string.h>

   void ArrayReadFunc(UBYTE *arrayout)
   {
        UBYTE array[20] = {1, 2, 3, 4,5, 6, 7, 8, 9, 10,
			   11, 12, 13, 14, 15, 16, 17,
			   18, 19, 20};
	memcpy(arrayout, array, 20);
   }

   void ArrayWriteFunc(UBYTE *arrayin)
   {
	UBYTE array[20];

	memcpy(array, arrayin, 20);

	printf("Byte slice array received from Go:\n");
	for(int i = 0; i < 20; i ++){
		printf("%d ", array[i]);
	}

	printf("\n");
   }

Functions are written just for this post and they don't really do
anything. As you can see `ArrayReadFunc` takes a pointer to array and
fills it with content of another array using `memcpy`. Function
`ArrayWriteFunc` on other hand takes pointer to array and copies its
content to internal array. I've added print logic to `ArrayWriteFunc`
just to show that values passed from *Go* are making it here.

Below is the Go code which uses the above C files passes byte slice to
get value out of C code and array made of byte slice to C function to
send values in.

.. code-block:: go

   package main

   /*
   #cgo CFLAGS: -std=c99
   
   #include "bytetest.h"
   #include <stdlib.h>
   */
   import "C"
   
   import (
        "fmt"
	"unsafe"
   )
	 
   func ReadArray() unsafe.Pointer {
          var outArray = unsafe.Pointer (C.calloc(20,1))
          C.ArrayReadFunc((*C.UBYTE)(outArray))
   
	  return outArray
   } 
	 
   func WriteArray(inArray unsafe.Pointer) {
          C.ArrayWriteFunc((*C.UBYTE)(inArray))
   }
	 
   func CArrayToByteSlice(array unsafe.Pointer, size int) []byte {
          var arrayptr = uintptr(array)
	  var byteSlice = make([]byte, size)
	 
	  for i := 0; i < len(byteSlice); i ++ {
	          byteSlice[i] = byte(*(*C.UBYTE)(unsafe.Pointer(arrayptr)))
	 	  arrayptr ++
	  }
	 
	  return byteSlice
   }
	 
   func ByteSliceToCArray (byteSlice []byte) unsafe.Pointer {
          var array = unsafe.Pointer(C.calloc(C.size_t(len(byteSlice)), 1))
	  var arrayptr = uintptr(array)
	 
	  for i := 0; i < len(byteSlice); i ++ {
	         *(*C.UBYTE)(unsafe.Pointer(arrayptr)) = C.UBYTE(byteSlice[i])
	 	 arrayptr ++
	  }
	 
	  return array
   }
	 
   func main(){
           carray := ReadArray()
	   defer C.free(carray)
   
	   carraybytes := CArrayToByteSlice(carray, 20)
	 
	   fmt.Println("C array converted to byte slice:")
	   for i := 0; i < len(carraybytes); i ++ {
	           fmt.Printf("%d ", carraybytes[i])
	   }
	 
	   fmt.Println()
	 
	   gobytes := []byte{21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
	           31, 32, 33, 34, 35, 36, 37, 38, 39, 40}
	   gobytesarray := ByteSliceToCArray(gobytes)
	   defer C.free(gobytesarray)
   
	   WriteArray(gobytesarray)
   }

Functions `ReadArray` and `WriteArray` are just wrapper to the calls
to C counter parts `ArrayReadFunc` and `ArrayWriteFunc`. `ReadArray`
returns `unsafe.Pointer` which is allocated C array and should be
freed by caller. `WriteArray` takes `unsafe.Pointer` which is pointing
to memory location containing C array.

Now the functions of interest are `CArrayToByteSlice` and
`ByteSliceToCArray`. It should be pretty clear from the above code to
understand what is happening in these functions. Still I will just put
explain them briefly.

`ByteSliceToCArray` allocates a C array using `calloc` from C standard
library. It then creates a `uintptr`, a pointer type in Go which is
used to dereference the each memory location and store bytes from the
input byte slice in them.

`CArrayToByteSlice` on other hands creates a `uintptr` type by casting
input unsafe.Pointer type and then uses this pointer type to
dereference values from memoy and store it in byte slice with suitable
casting.

So lets build the code and run it and see the output::

  C array converted to byte slice:
  1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 
  Byte slice array received from Go:
  21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40

So yes it actually works and values are moving across C and Go. This
solves first problem in hand next is converting arbitrary Go types
into byte slices.

There are many cases where we would like to convert an arbitrary Go
types like (int, float) into bytes. One such use case I found was when
writing a TCP client for communicating with a Server written using C
speaking custom protocol. Here I'm just going to show how to convert
types like float, int to byte slice, I've not tried converting
structures but it is certainly possible.

Below is the function which can convert int32,float32 into byte slice
it can also be extended for other types.

.. code-block:: go

   func CopyValueToByte(value interface{}) []byte {
	var valptr uintptr
	var slice []byte

	switch t := value.(type) {
	case int32:
		i := value.(int32)
		valptr = uintptr(unsafe.Pointer(&i))
		slice = make([]byte, unsafe.Sizeof(i))
	case float32:
		f := value.(float32)	
		valptr = uintptr(unsafe.Pointer(&f))
		slice = make([]byte, unsafe.Sizeof(f))
	default:
		fmt.Fprintf(os.Stderr,"Unsupported type: %T\n", t)
		os.Exit(1)
	}

	for i := 0; i < len(slice); i++ {
		slice[i] = byte(*(*byte)(unsafe.Pointer(valptr)))
		valptr++
	}

	return slice
   }


This function is generic which can take various types of value. First
we will use Go's type assertion to determine the type and creates a
`uintptr` pointer for the value and allocates byte slice depending on
the size of the value as calculated using `unsafe.Sizeof`. Later it
uses the pointer to dereference value from memory location and copies
each byte into byte slice. *The idea used here is every type is
represented as certain number of bytes in the memory.*  Below is the
entire program.

.. code-block:: go

   package main

   import (
        "fmt"
	"unsafe"
	"os"
   )

   func CopyValueToByte(value interface{}) []byte {
	var valptr uintptr
	var slice []byte

	switch t := value.(type) {
	case int32:
		i := value.(int32)
		valptr = uintptr(unsafe.Pointer(&i))
		slice = make([]byte, unsafe.Sizeof(i))
	case float32:
		f := value.(float32)	
		valptr = uintptr(unsafe.Pointer(&f))
		slice = make([]byte, unsafe.Sizeof(f))
	default:
		fmt.Fprintf(os.Stderr,"Unsupported type: %T\n", t)
		os.Exit(1)
	}

	for i := 0; i < len(slice); i++ {
		slice[i] = byte(*(*byte)(unsafe.Pointer(valptr)))
		valptr++
	}

	return slice
   }

   func main() {
	a := float32(-10.3)

	floatbytes := CopyValueToByte(a)
	
	fmt.Println("Float value as byte slice:")
	for i := 0; i < len(floatbytes); i++ {
		fmt.Printf("%x ", floatbytes[i])
	}

	fmt.Println()

	b := new(float32)
	bptr := uintptr(unsafe.Pointer(b))

	for i := 0; i < len(floatbytes); i++ {
		*(*byte)(unsafe.Pointer(bptr)) = floatbytes[i]
		bptr++
	}
	
	fmt.Printf("Byte value copied to float var: %f\n", *b)
	
   }

The above conversion can also be achieved using `encoding/binary`
package provided by Go. But `its been told to me
<https://twitter.com/dgryski/status/441514574307921920>`_ that it
makes things pretty slow.

Conclusion
----------

So goes `unsafe.Pointer` is really powerful thing which allows us to
work around the Go's type system but as package documentation says
**it should be used with care**

  PS: I'm not really sure if its recommended to use allocation
  functions from C standard library, I will wait for expert gophers to
  comment on that.
