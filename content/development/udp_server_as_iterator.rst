Writing a UDP Broadcast Receiver as Python Iterator
####################################################

:date: 2017-08-19 18:58 +0530
:slug: udp-server-as-generator
:tags: python, iterators, udp server
:author: copyninja
:summary: Post explaining my experiment of writing a UDP Broadcast Receiving
          service as a Python iterator.

I had to write a small Python application to listen for some broadcast message
and process the message. This broadcast messages are actually sort of discovery
messages to find some peers in a network. Writing a simple UDP Server to listen
on a particular port was easy; but while designing an application I was
wondering how can I plugin this server into my main code. There are 2
possibility

1. Use threading module of python to send the server code in back ground and
   give it a callback to communicate the data to main thread.
2. Periodically read some messages from server code and then dispose of server.

I didn't like first approach because I need to pass a callback function and I
some how will end up complicating code. Second approach sounded sane but I did
want to make server more like *iterator*. I searched around to see if some one
has attempted to write something similar, but did not find anything useful (may
be my Googling skills aren't good enough). Anyway so I thought what is wrong in
trying?. If it works then I'll be happy that I did something different :-).

The first thing for making iterator in Python is having function `__iter__` and
`__next__` defined in your class. For Python 2 iterator protocol wanted `next`
to be defined instead of `__next__`. So for portable code you can define a
`next` function which in return calls `__next__`.

So here is my first shot at writing `BroadCastReceiver` class.

.. code-block:: python

   from socket import socket, AF_INET, SOCK_DGRAM


   class BroadCastReceiver:

       def __init__(self, port, msg_len=8192):
           self.sock = socket(AF_INET, SOCK_DGRAM)
           self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
           self.sock.bind(('', port))
           self.msg_len = msg_len

       def __iter__(self):
                return self

       def __next__(self):
                try:
                    addr, data = self.sock.recvfrom(self.msg_len)
                    return addr, data
                except Exception as e:
                    print("Got exception trying to recv %s" % e)
                    raise StopIteration

This version of code can be used in a `for` loop to read from socket UDP
broadcasts. One problem will be that if no packet is received which might be due
to disconnected network the loop will just block forever. So I had to modify the
code slightly to add timeout parameter. So changed portion of code is below.

.. code-block:: python

   ...
       def __init__(self, port, msg_len=8192, timeout=15):
           self.sock = socket(AF_INET, SOCK_DGRAM)
           self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
           self.sock.settimeout(timeout)
           self.sock.msg_len = msg_len
           self.sock.bind(('', port))

    ...

So now if network is disconnected or no packet was received for `timeout` period
we get a `socket.timeout` exception due to which `StopIteration` will be raised
causing the `for` loop using server as iterator to exit. This avoids us just
blocking our periodic code run forever when network is disconnected or no
messages are received for long time. (may be due to connected to wrong network).

Now every thing looks fine but only part is if we create the server object each
time our periodic code is called we will have binding issue as we did not
properly close the socket once iterator has stopped. So I added socket closing
code in `__del__` function for the class. `__del__` will be called when garbage
collector try to recollect object when it goes out of scope.

.. code-block:: python

   ...
       def __del__(self):
           self.sock.close()

So the server can be used in `for` loop or by passing the object of server to
`next` built-in function. Here are 2 examples.

.. code-block:: python

   r = BroadCastReceiver(5000, timeout=10)
   count = 0
   for (address, data) in r:
       print('Got packet from %s: %s' % address, data)
       count += 1
       # do whatever you want with data
       if count > 10:
           break

Here we use an counter variable to track iteration and after some iteration we
exit for loop. Another way is use `for` loop with range of iteration like below.

.. code-block:: python

   r = BroadCastReceiver(5000,  timeout=10)
   for i in range(20):
       try:
           address, data = next(r)
           # do whatever you want with data
       except:
           break

Here an additional try block was needed inside the for loop to card call to
`next`, this is to handle the timeout or other exception and exit the loop. In
first case this is not needed as `StopIteration` is understood by `for`.

Both use cases I described above are mostly useful when it is not critical to
handle each and every packet (mostly peer discovery) and packets will always be
sent. So if we miss some peers in one iteration we will still catch them in next
iteration. We just need to make sure we provide big enough counter to catch most
peers in each iteration.

If its critical to receive each packet we can safely send this iterating logic
to a separate thread which keeps receiving packets and process data as needed.

For now I tried this pattern mostly with UDP protocol but I'm sure with some
modification this can be used with TCP as well. I'll be happy to get feed back
from Pythonistas out there on what you think of this approach. :-)

Update
======

I got a suggestion from *Ryan Nowakowski* to make the server object as `context
manager` and close the socket in `__exit__` as it can't be guaranteed that
`__del__` will be called for objects which exists during interpreter exits. So I slightly modified the class to add `__enter__` and `__exit__` method like below and removed `__del__`

.. code-block:: python

   ...

       def __enter__(self):
           return self

       def __exit__(self, exc_type, exc_value, traceback):
           self.sock.close()


Usage pattern is slightly modified because of this and we need to use `with`
statement while creating object.

.. code-block:: python

   with BroadCastReceiver(2000) as r:
       # use server object as you wish
       ...

It is also possible to cleanly close socket without adding context manager that
is adding `finally` statement to our `try` and `except` block in `__next__`. The
modified code without adding context manager looks like below.

.. code-block:: python

   def __next__(self):
       try:
           addr, data = self.sock.recvfrom(self.msg_len)
           return addr, data
       except Exception as e:
           print("Got exception trying to recv %s" % e)
           raise StopIteration
       finally:
           self.sock.close()

When we raise `StopIteration` again from except block, it will be temporarily
saved and `finally` block is executed which will now close the socket.
