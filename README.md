SUMMARY
====================
A minimal set of tools to manage a plain-text Zettelkasten [^1] from the command line.


SETUP
====================
Dependencies:
- Python 3.8+
- nvim
- [fzf](https://github.com/junegunn/fzf)

Set the following in your shell:

    export ZETTELKASTEN_SOURCE=/path/to/zettelkasten
    source $ZETTELKASTEN_SOURCE/bin/aliases.sh
    export PATH=${PATH}:$ZETTELKASTEN_SOURCE/bin


EXAMPLES
====================

### New Zettelkasten files (`zn`)

    zn / foo               # creates `1-foo.md`
    zn / bar               # creates `2-bar.md`
    zn 1 another thought   # creates `1a-another-thought.md`

### List Zettelkasten (`zl`)

    zl

Opens `fzf` with the following structure:

    07-20 1     foo
           1a   another thought

          2     bar

Hit `enter` to select a file and then:
- print the filename with `zp`
- copy the filename with `zc`
- open the file with `zv`

### Move Zettelkasten files (`zm`)

Moving entails both:
1. renaming the file
2. rewriting all references to it

For example:

    echo "a link to file 2-bar.md" >> 1a-another-thought.md

Move the file:

    zm 2-bar.md 1a1-bar.md

New hierarchy:

    07-20 1       foo
           1a     another thought
            1a1   bar

The reference in _1a-another-thought.md_ is updated:

    a link to file 1a1-bar.md


STRUCTURE
====================

### Filename

Filenames have the following structure:

    12a1-TAG1-TAG2-a-short-description-of-topic-A.md
    ^    ^
    UID  TAGS      ^ DESCRIPTION

Tags preface the description and are all-caps.

### UID

Per usual practice, the UID consists of alternating numbers and characters.

### Lists

Given the following files:

    # Created on 07-20:
    zn / foo
    zn / bar

    # Created on 07-21:
    zn 1 another thought
    zn / SHAPES 2d
    zn 3-SHAPES-2d.md triangle
    zn 3a equilateral
    zn 3a scalene
    zn 3 quadrilateral

The list (`zl`) will be shown as:

    07-20 1             foo
    07-21  1a           another thought

    07-20 2             bar

    07-21 3      SHAPES 2d
           3a           triangle
            3a1         equilateral
            3a2         scalene
           3b           quadrilateral

The list can be ordered by last updated time with `ctrl-l`:

    07-20 1             foo
          2             bar

    07-21  1a           another thought
          3      SHAPES 2d
           3a           triangle
            3a1         equilateral
            3a2         scalene
           3b           quadrilateral

Switch back to order-by-name with `ctrl-n`.

ALL COMMANDS
====================
- `zn`: **new** file
- `zl`: **list** files
- `zm`: **move** file and update references
- `zg`: **grep** files
- `zp`: **print** the previous file created/chosen
- `zc`: **copy** --''--
- `zv`: open in **vim** the previous file created/chosen

REFERENCES
====================
[^1]: https://writingcooperative.com/zettelkasten-how-one-german-scholar-was-so-freakishly-productive-997e4e0ca125
