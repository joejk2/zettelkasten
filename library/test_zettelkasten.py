import pytest
from zettelkasten import *

# FILENAMES = [
#     dict(filename="1~2022-05-31~foo-bar.md", id="1"),
#     dict(filename="1,1~2022-05-31~foo-bar.md", id="1"),
#     dict(filename="1,1,1~2022-05-31~foo-bar.md", id="1"),
# ]


def test_dash_separated():
    assert dash_separated("foo BAR") == "foo-BAR"
    assert dash_separated("foo", "BAR") == "foo-BAR"


def test_to_string():
    assert to_string(1, "a") == "1a"


def test_select_uid():
    assert select_uid(f"/") == "/"
    assert select_uid(f"1{DELIM}aaa") == "1"
    assert select_uid(f"1a{DELIM}aaa{DELIM}bb") == "1a"
    assert select_uid("1a") == "1a"


def test_select_tags():
    assert select_tags("TAG1-TAG2-foo-bar") == "TAG1 TAG2"


def test_select_description():
    assert select_description("TAG1-TAG2-foo-bar") == "foo bar"


def test_uid_components():
    assert uid_components("1") == [1]
    assert uid_components("12") == [12]
    assert uid_components("1a") == [1, "a"]
    assert uid_components("1a2") == [1, "a", 2]
    assert uid_components("1za2") == [1, "za", 2]


def test_uid_tail():
    assert uid_tail(["1"], 1) == None
    assert uid_tail([], 4) == None
    assert uid_tail(["1"], 0) == 1
    assert uid_tail(["1", "1a", "1a1", "1b1b"], 0) == 1
    assert uid_tail(["1", "1a", "1a1", "1b1b"], 1) == "b"
    assert uid_tail(["1", "1a", "1a2", "1b1b"], 2) == 2
    assert uid_tail(["1", "1a", "1a2", "1b1b"], 3) == "b"
    assert uid_tail(["1", "1a", "1a2", "1b1b"], 4) == None


def test_increment_tail():
    assert increment_tail(1) == 2
    assert increment_tail("a") == "b"
    assert increment_tail("z") == "za"
    assert increment_tail("za") == "zb"
    assert increment_tail("zz") == "zza"


def test_add_level():
    assert add_level(["/"]) == 1
    assert add_level([10]) == "a"
    assert add_level([10, "b"]) == 1


def test_generate_uid():
    assert generate_uid("1", ["1"]) == "1a"
    assert generate_uid("1", ["1", "1a"]) == "1b"
    assert generate_uid("1", ["1", "1a", "1c"]) == "1d"
    assert generate_uid("1", ["1", "1a1", "1c1a1"]) == "1d"
    assert generate_uid("1a", ["1", "1a1", "1c1a1"]) == "1a2"


def test_rename_file():
    assert rename_file("1a1-FOO-bar.md", "2") == "2a-FOO-bar.md"
    assert rename_file("1a1-FOO-bar.md", "2", "foo-bar") == "2a-foo-bar.md"
    with pytest.raises(ValueError):
        rename_file("1-FOO-bar.md", "/")
    with pytest.raises(ValueError):
        rename_file("1a1-FOO-bar.md", "1a")


DATED_FILES = [
    ("06-20", "1-foo.md"),
    ("06-20", "2-foobar.md"),
    ("06-21", "1a-bar.md"),
]


def test_list_sorted():
    assert list_sorted(DATED_FILES, sort_by_last_modified=False) == [
        DATED_FILES[0],
        DATED_FILES[2],
        DATED_FILES[1],
    ]
    assert list_sorted(DATED_FILES, sort_by_last_modified=True) == [
        DATED_FILES[0],
        DATED_FILES[1],
        DATED_FILES[2],
    ]


def test_list_decomposed():
    l = list_decomposed(DATED_FILES)
    assert len(l) == 3


def test_list_arranged():
    pass


"""
TODO - 
    tidy and test rename_file
    tidy and test list functionality 
    check in 
    
    tidy scripts 
    check in 
    
    README
    check in 
"""
