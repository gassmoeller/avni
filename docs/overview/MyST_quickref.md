---
orphan: true
---
(sec:myst-quickref)=
# MyST Quick reference

:::{note}
Everything in this file will look like garbage in a regular markdown viewer, like if you're viewing this on github. Viewing it on readthedocs will render everything properly.

Also: numref will not work in this file since its not part of the main filetree. But it will work in anything thats a part of a toctree.
:::

## Text

````md
Put single asterisks around text you *want to italicize*, but double asterisks around text you **want to bold**.
````

Put single asterisks around text you *want to italicize*, but double asterisks around text you **want to bold**.

## Headings

```md
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```
becomes:

# Heading 1
## Heading 2
### Heading 3
#### Heading 4

All standalone .md files must start with a level 1 header, regardless of whether it is a chapter, section, or subsection. Subheaders within the same file can start with ## and so on.

For a section to be referenced, it must have a header tag like so:

```md
(sec:myst-quickref)=
# MyST Quick reference
```

To refer to the section:

```md
Include a section reference to {ref}`sec:myst-quickref` in a sentence like so.
```

Include a section reference to {ref}`sec:myst-quickref` in a sentence like so.

## Admonitions

```md
:::{admonition} General admonition as warning
:class: warning

Text goes here.
:::

:::{attention}
This is an `attention` admonition.
:::

:::{danger}
This is a `danger` admonition.
:::

:::{error}
This is an `error` admonition.
:::

:::{important}
This is an `important` admonition.
:::

:::{note}
This is a `note` admonition.
:::

:::{tip}
This is a `tip` admonition.
:::

:::{warning}
This is a `warning` admonition.
:::

:::{seealso}
This is a `seealso` admonition.
:::

:::{admonition} TODO
:class: error

This is a custom `TODO` admonition.
:::
```

Becomes:

:::{admonition} General admonition as warning
:class: warning

Text goes here.
:::

:::{attention}
This is an `attention` admonition.
:::

:::{danger}
This is a `danger` admonition.
:::

:::{error}
This is an `error` admonition.
:::

:::{important}
This is an `important` admonition.
:::

:::{note}
This is a `note` admonition.
:::

:::{tip}
This is a `tip` admonition.
:::

:::{warning}
This is a `warning` admonition.
:::

:::{seealso}
This is a `seealso` admonition.
:::

:::{admonition} TODO
:class: error

This is a custom `TODO` admonition.
:::

## Lists

### Itemized lists

```md
* Level 1
  * Level 2
    * Level 3
```

* Level 1
  * Level 2
    * Level 3

### Definition lists

```md
Term 1
: Definition of term 1

Term 2
: Definition of term 2
```

becomes:

Term 1
: Definition of term 1

Term 2
: Definition of term 2

(sec:quickref:code-blocks)=
## Code blocks

### C++

````markdown
```{code-block} c++
---
caption: C++ code block.
emphasize-lines: 3-4
---
int
main(int argc, char* argv[]) {
    // Emphasized lines corresponding to body of main().
    return 0;
}
```
````

becomes:

```{code-block} c++
---
caption: C++ code block.
emphasize-lines: 3-4
---
int
main(int argc, char* argv[]) {
    // Emphasized lines corresponding to body of main().
    return 0;
}
```

### python

````markdown
```{code-block} python
---
caption: Python code block.
---
def square(x):
    return x**2
```
````

becomes:

```{code-block} python
---
caption: Python code block.
---
def square(x):
    return x**2
```

### Console

````md
```{code-block} console
---
caption: Interactive shell.
---
$ ls
a b c
```
````
becomes:
```{code-block} console
---
caption: Interactive shell.
---
$ ls
a b c
```

### Bash

````md
```{code-block} bash
---
caption: Bash code block.
---
# Comment
for i in "a b c"; do
  print $i
done
```
````
becomes:
```{code-block} bash
---
caption: Bash code block.
---
# Comment
for i in "a b c"; do
  print $i
done
```

### cfg

````md
```{code-block} cfg
---
caption: Config code block.
---
# Comment
[pylithapp]
journal.info.problem = 1

[pylithapp.petsc]
ksp_rtol = 1.0e-3
```
````

```{code-block} cfg
---
caption: Config code block.
---
# Comment
[pylithapp]
journal.info.problem = 1

[pylithapp.petsc]
ksp_rtol = 1.0e-3
```


Captions are optional.


## Tables

````md
```{table} Table caption
:name: tab:quickref
|             Header 1 |   Header 2    | Header 3       |
| -------------------: | :-----------: | :------------- |
|        right aligned |   centered    | left aligned   |
| more data, more data | yet more data | even more data |
```
````

becomes:

```{table} Table caption
:name: tab:quickref
|             Header 1 |   Header 2    | Header 3       |
| -------------------: | :-----------: | :------------- |
|        right aligned |   centered    | left aligned   |
| more data, more data | yet more data | even more data |
```

Refer to it with the numref tag, like so:
```md
Please see {numref}`tab:quickref`.
```

Please see {numref}`tab:quickref`.

Figure labels cannot contain more than one dash, so we use colons instead.
This is likely a bug.

:::{note}
The numref command doesn't work in this particular file because its not a part of the main file structure. It does work in the manual, as long as the file is in a toctree.
:::

## Figures

Format a figure like this:
````md
```{figure-md} fig:quickref
<img src="../_static/logos/logo_avni_color_withname.svg" alt="Screenshot"  width="100%"/>

This is the figure caption.
```
````
to get this:

```{figure-md} fig:quickref
<img src="../_static/logos/logo_avni_color_withname.svg" alt="Screenshot"  width="100%"/>

This is the figure caption.
```
Put the filename and relative path in "img src", but leave the file extension as `.*` instead of .png or whatever. Allowable formats for figures include SVGs, PNGs, and JPGs, but not PDFs unfortunately.

Refer to it like:

```md
Please see {numref}`fig:quickref`.
```
Please see {numref}`fig:quickref`.


Figure labels cannot contain more than one dash, so we use colons instead.
This is likely a bug.

Sphinx does not support the use of subfigures. Combine any sub-figures you want to include into one file. We recommend inkscape for this purpose.

Figures need to have a caption or they will not be rendered.
If you want to include figures without captions you can instead do:

````md
```{image} ../_static/logos/logo_avni_color_withname.png
:alt: AVNI Logo
:width: 80%
:align: center
```
````

## Math

Inline math works just like in latex. Use dollar signs to put stuff like $\eta_r(z)$ in a sentence. That's:

```md
Use dollar signs to put stuff like $\eta_r(z)$ in a sentence.
```

Be aware that not all latex packages are known by Sphinx, so some commands will need to be reformatted (i.e., \num{4e5} needs to be rewritten as 4\times 10^{5}.)

For math blocks:

````md
```{math}
:label: eqn:one:two
F = m a
```
````
becomes
```{math}
:label: eqn:one:two
F = m a
```
````md
Refer to the labeled equation like {math:numref}`eqn:one:two`.
````
Refer to the labeled equation like {math:numref}`eqn:one:two`.
(The label is not necessary if the equation doesn't have one, in which case it would be formatted like):
````md
```{math}
F = ma
```
````

The split environment is built into the math directive; which allows you to use one align operator (`&`).

````md
```{math}
:label: eq:aligned
  -\nabla \cdot \left[2\eta
   \left(\varepsilon(\mathbf u) - \frac{1}{3}(\nabla \cdot \mathbf u)\mathbf 1\right)\right]
   + \nabla p' &=  -\bar \alpha \bar\rho T' \mathbf g \qquad \textrm{in $\Omega$},  \\
  \nabla \cdot (\bar\rho \mathbf u) &= 0  \qquad  \textrm{in $\Omega$}.
```
````

becomes:
```{math}
:label: eq:aligned
  -\nabla \cdot \left[2\eta
   \left(\varepsilon(\mathbf u) - \frac{1}{3}(\nabla \cdot \mathbf u)\mathbf 1\right)\right]
   + \nabla p' &=  -\bar \alpha \bar\rho T' \mathbf g \qquad \textrm{in $\Omega$},  \\
  \nabla \cdot (\bar\rho \mathbf u) &= 0  \qquad \textrm{in $\Omega$}.
```

If you require more than one alignment character you need to start and end an additional `aligned` environment. Be sure to add the same number of align operators (`&`) to each line and use `\\` to denote a new line.

````md
```{math}
:label: eq:aligned
\begin{aligned}
  -\nabla \cdot \left[2\eta
   \left(\varepsilon(\mathbf u) - \frac{1}{3}(\nabla \cdot \mathbf u)\mathbf 1\right)\right]
   + \nabla p' &=  -\bar \alpha \bar\rho T' \mathbf g & \qquad  & \textrm{in $\Omega$},  \\
  \nabla \cdot (\bar\rho \mathbf u) &= 0  & \qquad  & \textrm{in $\Omega$}.
\end{aligned}
```
````

becomes:
```{math}
:label: eq:multi-aligned
\begin{aligned}
  -\nabla \cdot \left[2\eta
   \left(\varepsilon(\mathbf u) - \frac{1}{3}(\nabla \cdot \mathbf u)\mathbf 1\right)\right]
   + \nabla p' &=  -\bar \alpha \bar\rho T' \mathbf g & \qquad  & \textrm{in $\Omega$},  \\
  \nabla \cdot (\bar\rho \mathbf u) &= 0  & \qquad  & \textrm{in $\Omega$}.
\end{aligned}
```

## Links

```md
[Put a link in text](https://en.wikipedia.org/wiki/Gibbs_free_energy) or just post the full link:
<https://en.wikipedia.org/wiki/Gibbs_free_energy>
```

becomes:

[Put a link in text](https://en.wikipedia.org/wiki/Gibbs_free_energy) or just post the full link:
<https://en.wikipedia.org/wiki/Gibbs_free_energy>


## Citations

```md
Traditional citation {cite}`Moulik:2014cr`.
Citation as noun {cite:t}`Moulik:2014cr`.
Use a comma for multiple, like {cite:t}`Moulik:2014cr,MoulikEtAl2021`.
```

becomes

Traditional citation {cite}`Moulik:2014cr`.
Citation as noun {cite:t}`Moulik:2014cr`.
Use a comma for multiple, like {cite:t}`Moulik:2014cr,MoulikEtAl2021`.

If the paper you wish to cite is not already in [references.bib](https://github.com/globalseismology/avni/blob/main/doc/references.bib), you will need to add its bibtex entry. Please format the citation tag as:

- `firstauthor:year` for one author
- `firstauthor:secondauthor:year` for two authors
- `firstauthor:etal:year` for more than two authors

where `firstauthor` and `secondauthor` refer to the *last* names of the authors.

## Footnotes
```md
Here's how you put a footnote[^footnote1] in a sentence.
```

Here's how you put a footnote[^footnote1] in a sentence (see the bottom of this file).



## See here for more

<https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html>
or
<https://jupyterbook.org/en/stable/reference/cheatsheet.html>

## footnote (again)

```md
[^footnote1]: And here's what the footnote says (put this at the very bottom of the document)
```

[^footnote1]: And here's what the footnote says (put this at the very bottom of the document)

```{bibliography}
```