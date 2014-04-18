# PYGT

## Installation

```
git clone https://github.com/nicr9/pygt.git
cd pygt
sudo python2.7 setup.py install
```

## About

`pygt` is a  CLI search tool similar to `grep` or `ack`. Where it differs is that it lists resulting lines by the method and/or class they belong to.

`pygt` is specifically for searching Python source code and will only look inside .py files. It initially uses `grep` to perform the actual searching, and for each result it opens the file and reads it to decide which class/function it belongs in based on the indentation of the file.

## Usage

It's simple to use. Here's an example looking for usages of the word "traceback" inside a subdirectory of the core Python source code: 

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

## Command-line options

You can use `pygt -i <SEARCH_TERM>` to do a case-insensitive search.

If you're experiencing issues, turn on debug output like so: `pygt -d <SEARCH_TERM>`.

## Author

Name: Nic Roland<br>
Twitter: @nicr9_<br>
email: nicroland9@gmail.com
