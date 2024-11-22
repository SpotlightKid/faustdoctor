# faustdoctor

**NOTE:** *This is a fork of [faustpp], which is not endorsed by upstream
(since its maintainer is MIA). It is also **not backward compatible** with the
upstream version, since it features breaking changes to the architecture
templates, the template context and the command line interface.*

---

A post-processor for FAUST giving more flexibility at source generation.

This is a source transformation tool based on the [FAUST] compiler.

It permits to arrange the way how faust source is generated with greater
flexibility.

Using a template language known as [Jinja2], it is allowed to manipulate
metadata with iteration and conditional constructs, to easily generate custom
code tailored for the job. Custom metadata can be handled by the template
mechanism.


## Usage

For detailed information, refer to the [documentation].

An example is provided in the `architectures` directory. It is usable and
illustrates many features.

The example is able to create a custom processor class. It has these abilities:

- Can generate a separate (C/C++) header and implementation file.
- Provides direct introspection of the characteristics of the controls.
- Can parse standard and custom UI metadata, for example:
    * `[symbol:]`
    * `[trigger]`
    * `[boolean]`
    * `[integer]`
- Provides named getters and setters for the controls.
- Provides a simplified signature for the processing routine.

The example can be used to generate any file. Pass options to the Faust
compiler using `-X`. In this particular example, you should pass a definition
of `Identifier` in order to name the result class, which is done with the
option `-D`.

```con
faustdr -X-vec -DIdentifier=MyEffect -a generic.cpp effect.dsp > effect.cpp
faustdr -X-vec -DIdentifier=MyEffect -a generic.hpp effect.dsp > effect.hpp
```


## Installation

Assuming you have Python installed (>= 3.9) and [pipx] installed, run this
command:

```con
pipx install faustdoctor
```

## Authors

This software is based on [faustpp], which was created by *Jean Pierre
Cimalando*. The project was forked, renamed to `faustdoctor`, updated, improved
and extended by *Christopher Arndt*, who now maintains this version.


## License

This software is released under the *Boost Software License 1.0*. Please see
the [LICENSE.md](./LICENSE.md) file for details.


## Release notes

**0.1.0**

- Initial release (forked from [faustpp] 1.0.0)


[documentation]: https://spotlightkid.github.io/faustdoctor
[faust]: https://faust.grame.fr/
[jinja2]: https://jinja.palletsprojects.com/
[faustpp]: https://github.com/jpcima/faustpp
[pipx]: https://pipx.pypa.io/
