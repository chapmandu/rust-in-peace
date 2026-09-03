"""Downstream theme targets.

Each module renders one editor/terminal config from the shared palettes
and the semantic role table in scripts/roles.py, and exposes
`generate(flavor) -> str` (Zed, whose format is a theme family, takes
the whole flavor list). Token tables and templating stay in each module;
role meanings (modified, info, builtin, variable.builtin) do not.
New targets register in scripts/build_ports.py.
"""
