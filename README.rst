ToscaWidgets
============

ToscaWidgets is a web widget toolkit for Python to aid in the creation,
packaging and distribution of common view elements normally used in the web.

tw2.devtools contains features for developers, including the widget browser
and widget library quickstart template.

Installation
------------

Install via `pip
<http://pypi.python.org/pypi/pip>`_::

    $ pip install tw2.devtools

Contributing
------------

`git-flow <https://github.com/nvie/gitflow>`_ with default branching convention
is used to develop `tw2.devtools`. To to initialize development environment.
Run::

    $ git clone git://github.com/toscawidgets/tw2.devtools.git
    $ cd tw2.devtools
    $ mkvirtualenv -p python2.7 tw2.devtools
    $ python setup.py develop

Running tests::

    $ python setup.py nosetests
