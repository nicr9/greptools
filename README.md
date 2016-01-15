# GrepTools

## Installation

From pip (recommended):

```
$ sudo pip install --pre greptools
```

From source (for developers):

```
$ git clone https://github.com/nicr9/greptools.git
$ cd greptools
$ sudo python2.7 setup.py develop
```

## About

`greptools` is a collection of CLI search tools similar to `grep` or `ack`.
These tools were designed with programmers in mind and each tool is targetted
at a different programming language or structured file format.

Each language specific tool recursively searches files relating to that language
in the current directory and sorts results into a context tree (refered to as a
grep tree). The exact format of the grep tree depends on the language in
question but it takes the form of nested datstructure with each level
representing a file, class or function.

Each tool uses `grep` to perform the actual searching, and for each result it
opens the file and reads it to decide which class/function it belongs to.

## Usage

It's simple to use. Here's an example using the tool for python code: `pygt`.

To look for usages of the word "traceback" inside a subdirectory of the core
Python source code:

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

These options should apply to all the available greptools so just use the name
of the tool you're using in place of `<greptool>` below:

### Case-insensitive search

```
$ <greptool> -i <SEARCH_TERM>
```

### Debug information

Turning this on prints out lots of additional information (e.g. raw grep
results) that can be used to diagnose bugs in the logic at various stages.
Useful if you're trying to develop your own greptool or add features to the base
classes.

```
$ <greptool> -d <SEARCH_TERM>
```

### Set operations

One of the really useful features these greptools is that they support treating
the results like sets and quickly filtering results by applying set operations.

Let's look at a simple example.

Let's say you need to quickly look through all the `import`s in your python
project. That's simple: `pygt import`.

Now lets say you want to narrow down those results to those that mention
`os.path`. This can be done by piping the results from our earlier search into
a new search for the new term like so:

```
$ pygt import | pygt os.path
```

This will effectively perform an intersection on both sets of results and so
only provide matches that contain both `import` and `os.path`.

You can perform other set operations too! Let's say you don't want any results
containing `os.path`. You can get the relative complement by piping like we did
before and setting the `-F` (filter) flag on the last search command like
so:

```
$ pygt import | pygt -F os.path
```

You can add both sets of results together with `-U` (union) and only return
results that contain one and not the other by using `-X` (XOR, a.k.a symetric
difference).

### Caveats with using set operations

Both the default (intersection) set op and the filter set op shown above aren't
actually true set operations.

It turns out treating search results like sets and performing these operations
isn't that fast as we hoped so we made a compromise. These two work by
iterating through that first set of results and checking for the second search
term using python's built in regex engine.

You may experience issues from the use of two different engines. For example, if
you are using complicated regular expressions you may find that they behave
differently when using intersection or filter set operations.

You can choose to use the slow intersection (`-N`) and the slow filter (`-E`)
instead which work by building both sets of results and comparing.

In order to use the pipe to pass one set of results to an other pygt process we
had to serialise them first. This means that if you try piping the results to
any other process (like `less` for example) they'll show up in json format. This
will happen even if you use other output formats like the histogram format.

If this causes problems for you, use `-p`. This will force it to pipe out
results in what ever format you've choosen (except the default 'colour' format.
It will be changed to clean because it looks really ugly when it's piped out).

## Writing a new greptool

So you've decided you need a greptool for your favourite language X.

Here are a basic set of instructions to create a new greptool:

### 1) Implement a new Reader class.

Are code blocks in X based on indentation or deliniated by braces?

There are some classes you can inherit from (`IndentReader` and `BraceReader`)
that are generalised for these cases. The docstrings should have details that
tell you what needs to be implemented by subclasses. `PythonReader` and
`JavaReader` are good examples of `IndentReader` and `BraceReader` subclasses
respectively.

If neither of these suit your purposes, you may need to inherit from
`BaseReader`. The logic you need to implement in this case is a little more
abstract, I'm not sure the docstrings are detailed enough. If you can't figure
out what to do from a reading of the code feel free to drop me an email with an
outline of what you're working on, I'd be glad to help!

### 2) Add details to `greptools/reader/__init__.py`

Two things you'll need to do: include a relative import of your new reader class
and add the name of that class to `__all__`.

### 3) Add new script to `bin/`

My advice is to copy a preexisting script. The convention is to base the script
name on the language file extention (e.g. Python files have a `.py` extention so
the Python greptool is called `pygt`).

Don't forget to change the name of the Reader class used in the script.

```
$ cp bin/pygt bin/xgt
$ sed -i "s/PythonReader/XReader/g" bin/xgt
```

### 4) Mention script in setup.py.

There's a `scripts` list in setup.py. Add your new script here so that it's
installed with all the others.

### 5) Reinstall.

```
$ sudo python2.7 setup.py develop
```

## Author

```
Name: Nic Roland
Twitter: @nicr9_
Email: nicroland9@gmail.com
```
