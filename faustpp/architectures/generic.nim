{.compile: "{{class_name}}.c".}

type
    {{class_name}}* = object
    SampleBuffer* = UncheckedArray[cfloat]


proc new{{class_name}}*(): ptr {{class_name}} {.importc.}
proc delete{{class_name}}*(dsp: ptr {{class_name}}) {.importc.}
proc init{{class_name}}*(dsp: ptr {{class_name}}, sample_rate: cint) {.importc.}
proc instanceClear{{class_name}}*(dsp: ptr {{class_name}}) {.importc.}
proc compute{{class_name}}*(dsp: ptr {{class_name}}, count: cint, inputs, outputs: ptr ptr SampleBuffer) {.importc.}

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

proc get_parameter*(dsp: ptr {{class_name}}, index: cuint): cfloat {.importc}
proc set_parameter*(dsp: ptr {{class_name}}, index: cuint, value: cfloat) {.importc}

{% for w in active + passive %}
proc get_{{w.meta.symbol}}*(dsp: ptr {{class_name}}): cfloat {.importc}
{% endfor %}
{% for w in active %}
proc set_{{w.meta.symbol}}*(dsp: ptr {{class_name}}, value: cfloat) {.importc}
{% endfor %}
