PYGT
====

Installation
----

```
sudo python2.7 setup.py install
```

About
----

Pygt is a simple keyword search cli tool similar to `grep` or `ack`. Where it differs is that it lists resulting lines by the method and/or class they belong to.

Pygt is specifically for searching Python source code and will only look inside .py files. It initially uses `grep` to perform the actual searching, and for each result it opens the file and reads it to decide which class/function it belongs in based on the indentation of the file. From this it builds a tree of the results and which it can either print out or save to a file.

Usage
----

It's simple to use, heres an example looking for usages of the word "traceback" inside a subdirectory of the Python source code: 

```
$ cd Python-2.7.3/Lib/multiprocessing
$ pygt traceback
./reduction.py
    def _serve
         132:^                import traceback$
         135:^                    '-'*79 + '\n' + traceback.format_exc() + '-'*79$

./queues.py
    class Queue
        def _feed
             280:^                    import traceback$
             281:^                    traceback.print_exc()$

./managers.py
     49:^from traceback import format_exc$

    class Server
        def shutdown
             368:^                import traceback$
             369:^                traceback.print_exc()$

./util.py
    def _run_finalizers
         263:^            import traceback$
         264:^            traceback.print_exc()$

./process.py
    class Process
        def _bootstrap
             273:^            import traceback$
             276:^            traceback.print_exc()$
```

An indepth review of pygt's other features is coming soon, until then checkout `pygt -h`

Why?
----

I've found while `grep` can be very useful it sometimes spits out a lot of results which makes it hard to read and discurages me from looking through all of those results for what's relevent at the time. When I found `ack` I thought it's output was much easier to read but alas, it's doesn't save me time because it's still lacking the context that I need to make decisions fast.

Author
----
Name: Nic Roland
Twitter: @nicr9_
email: nicroland9@gmail.com
