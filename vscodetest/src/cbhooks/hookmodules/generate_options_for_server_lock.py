"""
Returns a list of string choices for the Server Lock parameter, which indicate
the type of action that the lock protects against.
"""


def get_options_list(field, **kwargs):
    return [
        ("deletion", "deletion"),
    ]
