{% block NimPrologue %}
{% if fdrversioninfo is undefined or fdrversioninfo < (0, 2, 0) %}
{{fail("This template is not compatible with faustdoctor version < 0.2.0.")}}
{% endif %}
{% endblock %}
{.compile: "{{classname}}.c".}

type
    {{classname}}* = object

    ParameterRange* = object
        init*, min*, max*: cfloat

    SampleBuffer* = UncheckedArray[cfloat]


proc new{{classname}}*(): ptr {{classname}} {.importc.}
proc delete{{classname}}*(dsp: ptr {{classname}}) {.importc.}
proc init{{classname}}*(dsp: ptr {{classname}}, sample_rate: cint) {.importc.}
proc instanceClear{{classname}}*(dsp: ptr {{classname}}) {.importc.}
proc compute{{classname}}*(dsp: ptr {{classname}}, count: cint, inputs, outputs: ptr ptr SampleBuffer) {.importc.}

proc parameter_range*(index: cuint): ptr ParameterRange {.importc.}
proc parameter_group*(index: cuint): cint {.importc}
proc parameter_is_boolean*(index: cuint): bool {.importc}
proc parameter_is_enum*(index: cuint): bool {.importc}
proc parameter_is_integer*(index: cuint): bool {.importc}
proc parameter_is_logarithmic*(index: cuint): bool {.importc}
proc parameter_is_trigger*(index: cuint): bool {.importc}
proc parameter_label*(index: cuint): cstring {.importc}
proc parameter_short_label*(index: cuint): cstring {.importc}
proc parameter_style*(index: cuint): cstring {.importc}
proc parameter_symbol*(index: cuint): cstring {.importc}
proc parameter_unit*(index: cuint): cstring {.importc}

proc get_parameter*(dsp: ptr {{classname}}, index: cuint): cfloat {.importc}
proc set_parameter*(dsp: ptr {{classname}}, index: cuint, value: cfloat) {.importc}

{% for w in active + passive %}
proc get_{{w.symbol}}*(dsp: ptr {{classname}}): cfloat {.importc}
{% endfor %}
{% for w in active %}
proc set_{{w.symbol}}*(dsp: ptr {{classname}}, value: cfloat) {.importc}
{% endfor %}
