import re
import xml.etree.ElementTree as ET

from typing import Dict, List, Tuple

from .utility import parse_cstrlit, safe_element_text


REG_STRLIT = r'"(?:\\.|[^"\\])*"'
REG_IDENT = r"[a-zA-Z_][0-9a-zA-Z_]*"

REG_GLOBAL = re.compile(
    r"^\s*m->declare\((" + REG_STRLIT + r"), (" + REG_STRLIT + r")\);")
REG_INCLUDE = re.compile("^\\s*#\\s*include\\s+(.*)$")
REG_PRIVATE = re.compile(r"^(\s*)private(\s*:.*)$");
REG_PROTECTED = re.compile(r"^(\s*)protected(\s*:.*)$")
REG_VIRTUAL = re.compile(r"^(\s*)virtual([ \t].*$|$)")
REG_CONTROL = re.compile(
    r"^\s*ui_interface->declare\(&(" + REG_IDENT + r"), "
    r"(" + REG_STRLIT + r"), (" + REG_STRLIT + r")\);")
REG_TYPEDEF_STRUCT = re.compile(
    r"typedef struct \{.*?\} (?P<name>[_a-z][a-z0-9]*);", re.DOTALL)


def lift_structs(mdsource: str) -> Tuple[str, Dict[str, str]]:
    structs: Dict[str, str] = {}

    def save_structs(match: re.Match) -> str:
        structs[match.group("name")] = match.group(0)
        return ""

    return REG_TYPEDEF_STRUCT.sub(save_structs, mdsource), structs


def add_namespace(mdsource: str) -> str:
    ccode: str = ''
    is_in_class: bool = False

    # add our namespace definitions
    ccode += \
        "#ifndef FAUSTDR_BEGIN_NAMESPACE" "\n" \
        "#   define FAUSTDR_BEGIN_NAMESPACE" "\n" \
        "#endif" "\n" \
        "#ifndef FAUSTDR_END_NAMESPACE" "\n" \
        "#   define FAUSTDR_END_NAMESPACE" "\n" \
        "#endif" "\n" \
        "\n"

    # open the namespace
    ccode += \
        "FAUSTDR_BEGIN_NAMESPACE" "\n" \
        "\n"
    is_in_namespace : bool = True

    for line in mdsource.splitlines():
        if is_in_class:
            if line == "<<<<EndFaustClass>>>>":
                is_in_class = False
            else:
                # make sure not to enclose #include in the namespace
                is_include: bool = REG_INCLUDE.match(line) is not None
                if is_include and is_in_namespace:
                    ccode += "FAUSTDR_END_NAMESPACE" "\n";
                    is_in_namespace = False;
                elif not is_include and not is_in_namespace:
                    ccode += "FAUSTDR_BEGIN_NAMESPACE" "\n"
                    is_in_namespace = True;

                ccode += line;
                ccode += '\n';
        elif line == "<<<<BeginFaustClass>>>>":
            is_in_class = True

    # close the namespace
    if is_in_namespace:
        ccode += \
            "FAUSTDR_END_NAMESPACE" "\n" \
            "\n"

    return ccode


def apply_workarounds(cppsource: str, docmd: ET.ElementTree) -> str:
    line: str
    lines: List[str]

    # fix missing <meta>
    has_meta: bool = docmd.find('meta') is not None
    if not has_meta:
        lines = cppsource.splitlines()

        widget_nodes: Dict[str, ET.Element] = {}

        for elt in docmd.findall('./ui/activewidgets/widget'):
            widget_nodes[safe_element_text(elt.find('varname'))] = elt
        for elt in docmd.findall('./ui/passivewidgets/widget'):
            widget_nodes[safe_element_text(elt.find('varname'))] = elt

        for line in lines:
            mat = REG_GLOBAL.match(line)
            sub: ET.Element

            if mat is not None:
                key = parse_cstrlit(mat.group(1))
                value = parse_cstrlit(mat.group(2))
                sub = ET.SubElement(docmd.getroot(), 'meta', {'key': key})
                sub.text = value
                continue

            mat = REG_CONTROL.match(line)
            if mat is not None:
                varname = mat.group(1)
                key = parse_cstrlit(mat.group(2))
                value = parse_cstrlit(mat.group(3))
                sub = ET.SubElement(widget_nodes[varname], 'meta', {'key': key})
                sub.text = value
                continue

    # fix visibility keywords
    lines = cppsource.splitlines()
    source: List[str] = []

    for line in lines:
        mat = REG_PRIVATE.match(line)
        if mat is not None:
            source.append('%sFAUSTDR_PRIVATE%s\n' % (mat.group(1), mat.group(2)))
            continue

        mat = REG_PROTECTED.match(line)
        if mat is not None:
            source.append('%sFAUSTDR_PROTECTED%s\n' % (mat.group(1), mat.group(2)))
            continue

        mat = REG_VIRTUAL.match(line)
        if mat is not None:
            source.append('%sFAUSTDR_VIRTUAL%s\n' % (mat.group(1), mat.group(2)))
            continue

        source.append(line + "\n")

    return "".join(source)


def remove_preamble_and_epilog(mdsource: str, preamble="END PREAMBLE", epilog="START EPILOG") -> str:
    pos: int = mdsource.find("// " + preamble)
    if pos >= 0:
        mdsource = mdsource[pos+len(preamble)+4:]

    pos = mdsource.find("// " + epilog)
    if pos >= 0:
        mdsource = mdsource[:pos]

    return mdsource
