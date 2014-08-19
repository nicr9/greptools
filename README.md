# GrepTools

## Installation

```
git clone https://github.com/nicr9/pygt.git
cd pygt
sudo python2.7 setup.py install
```

## About

`greptools` is a collection of CLI search tools similar to `grep` or `ack`. These tools were designed with programmers in mind and each tool is targetted at a different language or file format. Each language specific tool searches files relating to that language and sorts results into a "context tree". The definition of content tree differs from tool to tool but typically it refers to the functions and classes to which each result comes from.

Each tool uses `grep` to perform the actual searching, and for each result it opens the file and reads it to decide which class/function it belongs in based on the indentation of the file.

## Usage

It's simple to use. Here's an example using the tool for python code: `pygt`. Here, we're just looking for usages of the word "traceback" inside a subdirectory of the core Python source code: 

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

These options should apply to all the available greptools so just use the name of the tool you're using in place of `<greptool>` below:

You can use `<greptool> -i <SEARCH_TERM>` to do a case-insensitive search.

If you're experiencing issues, turn on debug output like so: `<greptool> -d <SEARCH_TERM>`.

## Writing a new greptool

Here are the steps to creating a new greptool for whatever language or filetype you can think of:

#.1 Implement a new Reader class.
    * You can inherit from some of the ones in greptools.reader.reader that are generalised for certain language styles (for example: indentation vs. braces).
#.2 Add relative import to greptools/reader/__init__.py
    * Then add the new class name to __all__.
#.3 Copy a script in `bin/` and rename it to `"%sgt" % file_extension`
    * <file_extension>gt is the current convention for all tool names.
#.4 Change a few things in your new script.
    * It will need to import your class and pass it while instantiating a GrepTools object.
#.5 Add the name of that script to the list in setup.py.
#.6 Reinstall.
    * `sudo python2.7 setup.py install`.
    * This will add the tool to your path along with the others.

### P.S.

These steps are just a rough draft for now. I will expand on them in future releases.

## Author

Name: Nic Roland<br>
Twitter: @nicr9_<br>
email: nicroland9@gmail.com
