#          Copyright Jean Pierre Cimalando 2022.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE or copy at
#          http://www.boost.org/LICENSE_1_0.txt)
#
# SPDX-License-Identifier: BSL-1.0

import os
from typing import Any, Optional, TextIO, List, Dict, Tuple

from jinja2 import Environment, FileSystemLoader

from .metadata import Metadata, WidgetActive, Widget, WidgetType, WidgetScale
from .utility import cstrlit, mangle


class RenderFailure(Exception):
    pass


def render_metadata(out: TextIO, md: Metadata, tmplfile: str, defines: Dict[str, str]):
    tmpldir: str = os.path.dirname(tmplfile)
    env = Environment(loader=FileSystemLoader(tmpldir))
    template = env.get_template(os.path.basename(tmplfile))

    context: Dict[str, Any] = make_global_environment(md, defines)

    out.write(template.render(context))


def make_global_environment(md: Metadata, defines: Dict[str, str]) -> Dict[str, Any]:
    context: Dict[str, Any] = {}

    context["classcode"] = md.classcode
    context["source"] = md.source
    context["structs"] = md.structs.copy()

    context["name"] = md.name
    context["author"] = md.author
    context["copyright"] = md.copyright
    context["license"] = md.license
    context["version"] = md.version
    context["faustversion"] = md.faustversion
    context["classname"] = md.classname
    context["filename"] = md.filename
    context["inputs"] = int(md.inputs)
    context["outputs"] = int(md.outputs)
    context["meta"] = md.metadata.copy()
    context["groups"] = md.groups[:]

    wtype: int
    for wtype in (WidgetActive.Active, WidgetActive.Passive):
        widget_list: List[Widget] = []
        widget_list_obj: List[Dict[str, Any]] = []

        if wtype == WidgetActive.Active:
            widget_list = md.active
        elif wtype == WidgetActive.Passive:
            widget_list = md.passive

        i: int
        for i in range(len(widget_list)):
            widget: Widget = widget_list[i]

            widget_obj: Dict[str, Any] = {}

            widget_obj["type"] = widget.type.value
            widget_obj["id"] = widget.id
            widget_obj["label"] = widget.label
            widget_obj["symbol"] = widget.symbol
            widget_obj["varname"] = widget.varname
            widget_obj["group"] = widget.group
            widget_obj["order"] = widget.order
            widget_obj["init"] = widget.init
            widget_obj["min"] = widget.min
            widget_obj["max"] = widget.max
            widget_obj["step"] = widget.step
            widget_obj["hidden"] = widget.hidden
            widget_obj["scale"] = widget.scale.value
            widget_obj["screencolor"] = widget.screencolor
            widget_obj["style"] = widget.style.value
            widget_obj["tooltip"] = widget.tooltip
            widget_obj["unit"] = widget.unit
            widget_obj["entries"] = widget.entries
            widget_obj["meta"] = widget.metadata.copy()

            widget_list_obj.append(widget_obj)

        if wtype == WidgetActive.Active:
            context["active"] = widget_list_obj
        elif wtype == WidgetActive.Passive:
            context["passive"] = widget_list_obj

    context["cstr"] = cstrlit
    context["cid"] = mangle

    def fail(msg: str):
        if len(msg) == 0:
            msg = "failure without a message";
        raise RenderFailure(msg);
    context["fail"] = fail

    key: str
    val: str
    for key, val in defines.items():
        context[key] = parse_value_string(val)

    return context;

def parse_value_string(value: str) -> Any:
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
