
===
ffs
===

Python Filesystem Api helpers

.. image:: https://secure.travis-ci.org/davidmiller/ffs.png?branch=master
   :alt: Build Status
   :target: https://secure.travis-ci.org/davidmiller/ffs

Dealing with the filesystem in Python is clunky. Those of us who have an almost
emotional engagement with the elegance of the APIs we use, feel that it shouldn't
have to be this way. Not in Python.

Rationale
=========

This dance started waaay back. Frist there was Jason Orendorff's path.py, back
in 2004. Then in 05-06 Reinhold Birkenfeld and Björn Lindqvist tweaked it for
PEP 355, which tried to get something like that into the Standard Library. The
attempt failed miserably. Then in 2007 there was Mike Orr's Unipath, which added
a test suite and made it setuptoolsable.

Phew.

Question (short): So why are you doing it again?

Question (by implication): The idea has been solidly rejected by python-dev, with
strong objections from that community, and there's already a 3rd party module that
does a pretty good job of this stuff for those people who like This Kind Of Thing.
Why should I care?

Answer (short): The name is way more fun.

Answer (less facetiously): The name is way more fun. And four less characters to type.
And you know, if you're going to do something that's arguably a Bad Idea (TM) that
goes against the One True Way, you have to at leas market it properly, and in my life
at least, "FFS Python" is already a well established phrase.

Answer (oh, right, I just looked up what facetious means):

This kind of thing is about APIs. And the APIs that are out there, could *still be
better*. In fact, the APIs *were* better before all the operator overloading got taken
out in a misguided attempt to get the thing into the standard library.

Unipath is self-proclaimed stable since 2007, and hasn't even seen a bugfix release
since 2009. It's used in production by Real People's software that does Real Work.
Right now, I'm not even sure what the *right* API even is, yet alone in a position to
attempt to get patches into a package that's had a stable API for 5 years. That's
Stick-A-Fork-In-It-It's-Done-style stability.

The api for the Path class in ffs *Will* change, without depreciation warnings, on
minor point releases. Hell, this thing's only *on* PyPi at this stage so I can pull it
into a CI system without having to maintain my own cheeseshop.

`Docs`_

`Source`_

`Issues`_

.. _Docs: http://www.deadpansincerity.com/docs/ffs
.. _Source: https://github.com/davidmiller/ffs
.. _Issues: https://github.com/davidmiller/ffs/issues
