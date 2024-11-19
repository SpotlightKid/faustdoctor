#          Copyright Jean Pierre Cimalando 2022.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE or copy at
#          http://www.boost.org/LICENSE_1_0.txt)
#
# SPDX-License-Identifier: BSL-1.0

import enum
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Tuple, TypedDict

from .utility import safe_element_text, safe_element_attribute, is_decint_string, mangle, parse_cfloat


class WidgetType(enum.StrEnum):
    Button = "button"
    CheckBox = "checkbox"
    VSlider = "vslider"
    HSlider = "hslider"
    NEntry = "nentry"
    VBarGraph = "vbargraph"
    HBarGraph = "hbargraph"

class WidgetStyle(enum.StrEnum):
    Knob = "knob"
    Led = "led"
    Menu = "menu"
    Numerical = "numerical"
    Radio = "radio"
    Slider = "slider"

class WidgetActive(enum.IntEnum):
    Active = 0
    Passive = 1

class WidgetScale(enum.StrEnum):
    Linear = "linear"
    Log = "log"
    Exp = "exp"

@dataclass(init=False)
class Widget:
    type: WidgetType
    id: int
    label: str
    varname: str
    group: int
    order: int
    symbol: str
    init: float
    min: float
    max: float
    step: float
    # for radio buttons and menus
    entries: List[Tuple[str, float]]

    # Meta data
    metadata: Dict[str, str]
    # Standard metadata keys
    hidden: bool
    scale: WidgetScale
    screencolor: str
    style: WidgetStyle
    tooltip: str
    unit: str

@dataclass(init=False)
class Metadata:
    name: str
    author: str
    copyright: str
    license: str
    version: str
    faustversion: str
    classname: str
    filename: str
    groups: List[Tuple[str, List[int]]]
    groupmap: Dict[int, int]
    metadata: Dict[str, str]
    inputs: int
    outputs : int

    active: List[Widget]
    passive: List[Widget]

    classcode: str
    source: str
    structs: Dict[str, str]

    @property
    def num_ui_elements(self):
        return len(self.active) + len(self.passive)


def extract_metadata(doc: ET.ElementTree) -> Metadata:
    root: ET.Element = doc.getroot()

    md = Metadata()
    md.name = safe_element_text(root.find('name'))
    md.author = safe_element_text(root.find("author"))
    md.copyright = safe_element_text(root.find("copyright"))
    md.license = safe_element_text(root.find("license"))
    md.version = safe_element_text(root.find("version"))
    md.classname = safe_element_text(root.find("classname"))
    md.filename = ""
    md.inputs = int(safe_element_text(root.find("inputs"), '0'))
    md.outputs = int(safe_element_text(root.find("outputs"), '0'))
    md.classcode = ""
    md.source = ""
    md.structs = {}
    md.metadata = {}
    md.groups, md.groupmap = parse_groups(root)

    meta: ET.Element
    for meta in root.findall('meta'):
        # TODO: parse keys like "filters.lib/fir:author" and build metadata tree
        key: str = safe_element_attribute(meta, "key")
        value: str = safe_element_text(meta)
        md.metadata[key] = value

    md.active = []
    for elt in root.findall('./ui/activewidgets/widget'):
        md.active.append(extract_widget(elt, True, md))

    md.passive = []
    for elt in root.findall('./ui/passivewidgets/widget'):
        md.passive.append(extract_widget(elt, False, md))

    return md

def extract_widget(node: ET.Element, is_active: bool, md: Metadata) -> Widget:
    w = Widget()
    w.type = widget_type_from_name(safe_element_attribute(node, "type"))

    w.id = int(safe_element_attribute(node, "id", "0"))
    w.label = safe_element_text(node.find("label"))
    w.symbol = mangle(w.label.lower())
    w.varname = safe_element_text(node.find("varname"))
    w.group = md.groupmap.get(w.id, -1)
    w.order = -1
    w.entries = []

    w.init = 0
    w.min = 0
    w.max = 0
    w.step = 0

    w.metadata = {}
    w.hidden = False
    w.scale = WidgetScale.Linear
    w.screencolor = ""
    w.style = WidgetStyle.Knob
    w.tooltip = ""
    w.unit = ""

    if is_active and w.type in (WidgetType.HSlider, WidgetType.VSlider, WidgetType.NEntry):
        w.init = parse_cfloat(safe_element_text(node.find("init"), "0"))
        w.min = parse_cfloat(safe_element_text(node.find("min"), "0"))
        w.max = parse_cfloat(safe_element_text(node.find("max"), "0"))
        w.step = parse_cfloat(safe_element_text(node.find("step"), "0"))
    elif is_active and w.type in (WidgetType.Button, WidgetType.CheckBox):
        w.init = 0
        w.min = 0
        w.max = 1
        w.step = 1
    elif not is_active and w.type in (WidgetType.VBarGraph, WidgetType.HBarGraph):
        w.min = parse_cfloat(safe_element_text(node.find("min"), "0"))
        w.max = parse_cfloat(safe_element_text(node.find("max"), "0"))
    else:
        raise ValueError("Unsupported widget type")

    meta: ET.Element
    for meta in node.findall('./meta'):
        key: str = safe_element_attribute(meta, "key")
        value: str = safe_element_text(meta).strip()

        if is_decint_string(key) and not value:
            w.order = int(key)

        w.metadata[key] = value

        if key == "hidden":
            w.hidden = value.lower() in ("1", "y", "yes", "t", "true")
        elif key == "scale":
            w.scale = widget_scale_from_name(value.lower())
        elif key == "screencolor":
            w.screencolor = value
        elif key == "style" and value:
            style = parse_widget_style(value)
            w.style = widget_style_from_name(style[0].lower())
            w.entries = style[1]
        elif key == "symbol":
            w.symbol = mangle(value)
        elif key == "tooltip":
            w.tooltip = value
        elif key == "unit":
            w.unit = value

    return w


def parse_groups(root: ET.Element):
    groupmap = {}
    groups = []
    layout_el = root.find('./ui/layout')

    if layout_el:
        gid = 0
        for group in layout_el.findall('.//group'):
            name: str = safe_element_text(group.find("label"))
            widget_ids: List[int] = [int(safe_element_attribute(ref, "id"))
                                     for ref in group.findall("widgetref")]
            if widget_ids and name != "0x00":
                groups.append((name, widget_ids))
                for wid in widget_ids:
                    groupmap[wid] = gid
                gid += 1

    return groups, groupmap


def parse_widget_style(value: str) -> Tuple[str, List[Tuple[str, float]]]:
    """Parse value of [style:...] widget meta data

    The value can be either a simple widget style like `knob`, `led` or
    `numerical`, or a style name and list of entries within curly braces,
    e.g. for menus or radio buttons. Examples:

    * `menu{’label1’:v1;’label2’:v2...}` or
    * `radio{’label1’:v1;’label2’:v2...}`

    Returns a tuple with the style name as the first entry and a list
    of entries (`(label: str, value: float)` tuple) as the second one.

    """
    value = value.strip()
    brace_pos: int = value.find("{")

    if brace_pos < 0:
        return value, []

    style = value[:brace_pos].strip()
    entries = [entry.strip().split(":") for entry in value[brace_pos+1:-1].split(";") if entry.strip()]
    entries = [(label.strip().strip("'"), parse_cfloat(value.strip())) for label, value in entries]
    return style, entries


def widget_type_from_name(name: str) -> WidgetType:
    try:
        return WidgetType(name)
    except ValueError:
            raise ValueError("Invalid widget type name '{name}'")


def widget_scale_from_name(name: str) -> WidgetScale:
    try:
        return WidgetScale(name)
    except ValueError:
        raise ValueError(f"Invalid widget scale name '{name}'")


def widget_style_from_name(name: str) -> WidgetStyle:
    try:
        return WidgetStyle(name)
    except ValueError:
        raise ValueError(f"Invalid widget style name '{name}'")
