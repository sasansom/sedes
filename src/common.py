import re

# Various programs use this as the default specification of distribution
# variables and condition variables for the purpose of grouping for expectancy
# computation.
DEFAULT_DIST_COND_VARS_SPEC = "sedes/lemma"

# Parse a dist/cond variables specification. The syntax is a comma-separated
# list of dist_vars, optionally followed by a slash and a comma-separated list
# of cond_vars. A backslash escapes the character that follows it.
def parse_dist_cond_vars_spec(spec):
    dist_vars = []
    cond_vars = []

    escaped = False
    current_vars = dist_vars
    var = []
    i = iter(spec)
    while True:
        try:
            c = next(i)
        except StopIteration:
            c = None

        if escaped:
            # Previous character was a backslash, add this one verbatim.
            if c is None:
                raise ValueError("End of string after {!r}".format("\\"))
            var.append(c)
            escaped = False
        elif c == "\\":
            # Read the next character verbatim.
            escaped = True
        elif c == "/" or c == "," or c is None:
            # Slash, comma, or end of string marks the end of a variable.
            if var:
                current_vars.append("".join(var))
            else:
                if c == "," or current_vars:
                    raise ValueError(f"Empty variable name")
            var.clear()

            if c == "/":
                # At the first slash, switch from dist_vars to cond_vars.
                if current_vars is dist_vars:
                    current_vars = cond_vars
                else:
                    raise ValueError(f"More than one {'/'!r}")
            elif c is None:
                # This is also the end of the string, so return.
                break
        else:
            # Not a special character. Add it to the current variable name.
            var.append(c)

    assert not var, var
    return tuple(dist_vars), tuple(cond_vars)

_ESCAPE_RE = re.compile(r"[,/\\]")
def _escape(x):
    return _ESCAPE_RE.sub(lambda m: f"\\{m.group()}", x)

# Serialize dist_vars and cond_vars lists into the comma- and slash-delimited
# form.
def format_dist_cond_vars_spec(dist_vars, cond_vars):
    return ",".join(_escape(x) for x in dist_vars) + \
        "/" + \
        ",".join(_escape(x) for x in cond_vars)
