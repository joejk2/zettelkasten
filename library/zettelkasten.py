####################################################################################################
# This module helps create and list zettelkasten files.
#
# Each filename has the following structure:
#
#     12a1-TAG1-TAG2-a-short-description-of-topic-A.md
#     ^    ^
#     UID  TAGS      ^ DESCRIPTION
#
# Tags are prefaced, all-caps.
####################################################################################################


import glob
import itertools
import os
import time
import re
import sys


DELIM = "-"
TAG_LINE_NUMBER = 2


def dash_separated(*args):
    """Example: both ('foo BAR') and ('foo', 'BAR') return 'foo-BAR'"""
    return "-".join(["-".join(arg.split()) for arg in args])


def to_string(*args):
    return "".join([str(a) for a in args])


####################################################################################################
# Inspect filesystem
####################################################################################################
def get_uids(parent_uid: str) -> list:
    return [select_uid(filename) for filename in glob.glob(f"{parent_uid}*")]


####################################################################################################
# Select components from filename.
####################################################################################################
def select_filename_components(filename: str) -> list:
    return (
        select_uid(filename),
        select_text(filename),
    )


def select_uid(filename: str) -> str:
    return filename.split(DELIM)[0]


def select_text(filename: str) -> str:
    """Everything except uid and suffix"""
    return "-".join(filename.split(".md")[0].split(DELIM)[1:])


def select_description(text: str) -> str:
    return text.replace("-", " ")


####################################################################################################
# UID manipulations
####################################################################################################
def uid_components(uid: str) -> list:
    """For example '12a1' to [12, 'a', 1]"""
    return [int(s) if str.isdigit(s) else s for s in re.split(r"(\d+)", uid) if s != ""]


def uid_tail(uids: list, level: int):
    """Get the 'tail' from a list of uids, at given level in the UID hierarchy.

    For example, for uids ['12a', '12b'] the tail is '12' and 'b' at levels 1 and 2 respectively.
    """
    uids = [uid_cs[level] for uid in uids if len(uid_cs := uid_components(uid)) > level]
    return max(uids) if len(uids) else None


def increment_tail(tail: [int, str]):
    """Produces sequences of the form:
    - 1, 2, ... 9, 10, 11, ... etc
    - a, b, ... z, za, zb, ... zza, zzb, ... etc.
    """
    if isinstance(tail, str):
        return tail + "a" if tail[-1] == "z" else tail[:-1] + chr(ord(tail[-1]) + 1)
    else:
        return tail + 1


def add_level(parent_uid_cs: list):
    """Determines the next level in the sequence, for example:
    - the next level from '/' is 1
    - the next level from 1 is 'a'
    - the next level from 'a' is 1
    """
    return 1 if isinstance(parent_uid_cs[-1], str) else "a"


def generate_uid(parent_uid: str, child_uids: list) -> str:
    parent_uid_cs = uid_components(parent_uid)

    head = [] if parent_uid == "/" else parent_uid_cs
    tail = uid_tail(child_uids, len(head))

    new_tail = add_level(parent_uid_cs) if tail is None else increment_tail(tail)
    return to_string(*(head + [new_tail]))


####################################################################################################
# Construct filenames
####################################################################################################
def generate_filename_components(parent: str, *args) -> list:
    """The parent can be either:
    - "/" in which case we generate a filename at the top level
    - a UID of the form "12a1" in which case we generate a child filename
    - a complete filename from which the UID is extracted
    """
    parent_uid = select_uid(parent)
    namespace_uids = get_uids("[0-9]*.md" if parent == "/" else parent_uid)
    return (
        generate_uid(parent_uid, namespace_uids),
        dash_separated(*args),
    )


def join_filename_components(*args):
    return DELIM.join(args) + ".md"


def generate_filename(parent: str, *args):
    return join_filename_components(*generate_filename_components(parent, *args))


####################################################################################################
# List files
####################################################################################################
def filter(prefix):
    return f"{prefix}[-|a-z]*.md"


def list_dated(prefix="*"):
    return [
        (time.strftime("%m-%d", time.localtime(os.path.getmtime(f))), f)
        for f in glob.glob(filter(prefix))
    ]


def list_header(prefix="*", header_tags=""):
    def sorted_header(f):
        with open(f) as _file:
            for l in itertools.islice(_file, TAG_LINE_NUMBER - 1, TAG_LINE_NUMBER):
                if re.match("^>> ", l) and all(
                    [t in l.split() for t in header_tags.split()]
                ):
                    return " ".join(sorted(l.strip("^>> ").strip("\n").split()))
        return None

    return [
        (ts, f)
        for f in glob.glob(filter(prefix))
        if (ts := sorted_header(f)) is not None
    ]


def list_sorted(tagged_files, sort_by_tag):
    def rank(tag, filename):
        uid = uid_components(select_uid(filename))
        return (tag, uid) if sort_by_tag else uid

    return [
        (tag, filename)
        for tag, filename in sorted(tagged_files, key=lambda x: rank(x[0], x[1]))
    ]


def list_decomposed(tagged_files):
    return [
        dict(
            tag=tag,
            uid=select_uid(filename),
            description=description,
        )
        for tag, filename in tagged_files
        for description in [select_description(select_text(filename))]
    ]


def max_uid_level_max_tag_chars(filename_components):
    max_uid_level = 0
    max_chars_tag = 0
    for c in filename_components:
        max_uid_level = (
            l if (l := len(uid_components(c["uid"]))) > max_uid_level else max_uid_level
        )
        max_chars_tag = l if (l := len(c["tag"])) > max_chars_tag else max_chars_tag
    return max_uid_level, max_chars_tag


def list_arranged(
    filename_components,
    break_on_uid=False,
    break_on_tag=False,
    order=1,
    pad_uid=True,
    print_all_tags=False,
):
    print_components = []
    _max_uid_level, _max_chars_tag = max_uid_level_max_tag_chars(filename_components)
    last_tag = None
    last_uid_zeroth = None

    for c in filename_components:
        uid_cs = uid_components(c["uid"])
        if (break_on_tag and last_tag and c["tag"] != last_tag) or (
            break_on_uid and last_uid_zeroth and uid_cs[0] != last_uid_zeroth
        ):
            print_components.append("")

        uid_padding_len = len(uid_cs) if pad_uid else 1
        uid_prefix = " " * uid_padding_len + "`"
        description_prefix = (
            " "
            * (_max_uid_level - len(uid_prefix) - 2 * len(uid_components(c["uid"])) + 2)
            + " " * uid_padding_len
        )

        print_components.append(
            [
                c["tag"] + "\u00A0" * (_max_chars_tag - len(c["tag"]))
                if c["tag"] != last_tag or print_all_tags
                else "\u00A0" * _max_chars_tag,
                uid_prefix,
                c["uid"],
                description_prefix,
                c["description"],
            ],
        )
        last_tag = c["tag"]
        last_uid_zeroth = uid_cs[0]

    return "\n".join(["".join(c) for c in print_components[:: int(order)]])


def list_by_uid(prefix=None, order=1):
    return list_arranged(
        list_decomposed(list_sorted(list_dated(prefix), sort_by_tag=False)),
        break_on_uid=True,
        order=order,
    )


def list_by_last_modified(prefix=None, order=1):
    return list_arranged(
        list_decomposed(list_sorted(list_dated(prefix), sort_by_tag=True)),
        break_on_tag=True,
        order=order,
    )


def list_by_header(prefix=None, order=1, header_tags=""):
    return list_arranged(
        list_decomposed(
            list_sorted(list_header(prefix, header_tags), sort_by_tag=True)
        ),
        break_on_tag=True,
        order=order,
        pad_uid=False,
        print_all_tags=True,
    )


####################################################################################################
# For example:
#   python zettelkasten.py list_by_uid
#   python zettelkasten.py generate_filename / foo bar
####################################################################################################
if __name__ == "__main__":
    print(locals()[sys.argv[1]](*sys.argv[2:]))
