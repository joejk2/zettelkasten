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
import os
import re
import time
import sys

DELIM = "-"


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


def select_tags_description(text: str) -> str:
    tags, description = [], []
    reading_tags = True
    for word in text.split("-"):
        if not str.isupper(word):
            reading_tags = False
        if reading_tags:
            tags.append(word)
        else:
            description.append(word)
    return " ".join(tags), " ".join(description)


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
def list_dated():
    return [
        (time.strftime("%m-%d", time.localtime(os.path.getmtime(f))), f)
        for f in glob.glob("*.md")
    ]


def list_sorted(dated_files, sort_by_last_modified):
    def rank(last_updated, filename):
        uid = uid_components(select_uid(filename))
        return (last_updated, uid) if sort_by_last_modified else uid

    return [
        (date, filename)
        for date, filename in sorted(dated_files, key=lambda x: rank(x[0], x[1]))
    ]


def list_decomposed(dated_files):
    return [
        dict(
            date=date,
            uid=select_uid(filename),
            tags=tags,
            description=description,
        )
        for date, filename in dated_files
        for tags, description in [select_tags_description(select_text(filename))]
    ]


def max_uid_chars(filename_components):
    return max(
        [len(uid_components(c["uid"])) + len(c["uid"]) for c in filename_components]
    )


def max_tag_chars(filename_components):
    return max([len(c["tags"]) for c in filename_components])


def list_arranged(
    filename_components, break_on_uid=False, break_on_date=False, reverse=None
):
    print_components = []
    _max_uid_chars = max_uid_chars(filename_components)
    _max_tag_chars = max_tag_chars(filename_components)
    last_date = None
    last_uid_zeroth = None

    for c in filename_components:
        uid_cs = uid_components(c["uid"])

        if (break_on_date and last_date and c["date"] != last_date) or (
            break_on_uid and last_uid_zeroth and uid_cs[0] != last_uid_zeroth
        ):
            print_components.append("")

        print_components.append(
            [
                c["date"] if c["date"] != last_date else "\u00A0" + " " * 4,
                # preface with spaces for every level to the UID:
                "  " * len(uid_cs),
                c["uid"],
                # pad up to _max_uid_chars + 2:
                " " * (_max_uid_chars - len(uid_cs) - len(c["uid"]) + 2),
                c["tags"],
                # pad up to _max_tag_chars + 1:
                " " * ((_max_tag_chars - len(c["tags"])) + 1),
                "  " * (len(uid_cs) - 1) + c["description"],
            ],
        )
        last_date = c["date"]
        last_uid_zeroth = uid_cs[0]

    return "\n".join(
        ["".join(c) for c in print_components[:: -1 if reverse is None else 1]]
    )


def list_by_uid(reverse=None):
    return list_arranged(
        list_decomposed(list_sorted(list_dated(), sort_by_last_modified=False)),
        break_on_uid=True,
        reverse=reverse,
    )


def list_by_last_modified(reverse=None):
    return list_arranged(
        list_decomposed(list_sorted(list_dated(), sort_by_last_modified=True)),
        break_on_date=True,
        reverse=reverse,
    )


####################################################################################################
# For example:
#   python zettelkasten.py list_by_uid
#   python zettelkasten.py generate_filename / foo bar
####################################################################################################
if __name__ == "__main__":
    print(locals()[sys.argv[1]](*sys.argv[2:]))
