.. include:: ../links.inc

.. _design_philosophy:

Design philosophy
=================

Interactive versus scripted analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

AVNI has some great interactive plotting abilities that can help you
explore your data, and there are a few GUI-like interactive plotting commands
(like browsing through the raw data and clicking to mark bad channels, or
click-and-dragging to annotate bad temporal spans). But in general it is not
possible to use AVNI to mouse-click your way to a finished, publishable
analysis. AVNI works best when you assemble your analysis pipeline into
one or more Python scripts. On the plus side, your scripts act as a record of
everything you did in your analysis, making it easy to tweak your analysis
later and/or share it with others (including your future self).


Integration with the scientific python stack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

AVNI also integrates well with other standard scientific Python
libraries. For example, AVNI objects underlyingly store their data in
NumPy arrays, making it easy to apply custom algorithms or pass your data into
one of `scikit-learn's <scikit-learn_>`_ machine learning pipelines.
AVNI's 2-D plotting functions also return `matplotlib`_
:class:`~matplotlib.figure.Figure` objects, and the 3D plotting functions
return :class:`avni.viz.Figure3D` classes with a ``.plotter`` attribute
pointing to :class:`avni.Plotter` instances,
so you can customize your AVNI plots using any
of matplotlib or AVNI's plotting commands. The intent is that AVNI
will get most geoscientist 90% of the way to their desired analysis goal,
and other packages can get them over the finish line.


Submodule-based organization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A useful-to-know organizing principle is that AVNI objects and functions
are separated into submodules. This can help you discover related functions if
you're using an editor that supports tab-completion. For example, you can type
:samp:`avni.preprocessing.{<TAB>}` to see all the functions in the preprocessing
submodule; similarly for visualization functions (:mod:`avni.viz`), functions
for reading and writing data (:mod:`avni.io`), statistics (:mod:`avni.stats`),
etc.  This also helps save keystrokes — instead of::

    import avni
    avni.preprocessing.eog.peak_finder(...)
    avni.preprocessing.eog.find_eog_events(...)
    avni.preprocessing.eog.create_eog_epochs(...)

you can import submodules directly, and use just the submodule name to access
its functions::

    from avni.preprocessing import eog
    eog.peak_finder(...)
    eog.find_eog_events(...)
    eog.create_eog_epochs(...)


(Mostly) unified API
^^^^^^^^^^^^^^^^^^^^

Whenever possible, we've tried to provide a unified API for the different data
classes. For example, the :class:`~avni.io.Raw`, :class:`~avni.Epochs`,
:class:`~avni.Evoked`, and :class:`~avni.SourceEstimate` classes all have a
``plot()`` method that can typically be called with no parameters specified and
still yield an informative plot of the data. Similarly, they all have the
methods ``copy()``, ``crop()``, ``resample()`` and ``save()`` with similar or
identical method signatures. The sensor-level classes also all have an ``info``
attribute containing an :class:`~avni.Info` object, which keeps track of channel
names and types, applied filters, projectors, etc.

.. _sect-meth-chain:

In-place operation
^^^^^^^^^^^^^^^^^^

Because neuroimaging datasets can be quite large, AVNI tries very hard to
avoid making unnecessary copies of your data behind-the-scenes. To further
improve memory efficiency, many object methods operate in-place (and silently
return their object to allow `method chaining`_). In-place operation may lead
you to frequent use of the ``copy()`` method during interactive, exploratory
analysis — so you can try out different preprocessing approaches or parameter
settings without having to re-load the data each time — but it can also be a
big memory-saver when applying a finished script to dozens of subjects' worth
of data.



.. LINKS

.. _`method chaining`: https://en.wikipedia.org/wiki/Method_chaining
