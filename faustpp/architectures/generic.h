#ifndef  __{{class_name}}_H__
#define  __{{class_name}}_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif

#ifndef FAUSTCLASS
#define FAUSTCLASS {{class_name}}
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

#include <stdbool.h>
#include <stdint.h>
#include "faust/gui/CInterface.h"

{% for _, struct in structs.items() %}
{{struct}}
{% endfor %}

{{class_name}}* new{{class_name}}();
void delete{{class_name}}({{class_name}}* dsp);
void metadata{{class_name}}(MetaGlue* m);
int getSampleRate{{class_name}}({{class_name}}* RESTRICT dsp);
int getNumInputs{{class_name}}({{class_name}}* RESTRICT dsp);
int getNumOutputs{{class_name}}({{class_name}}* RESTRICT dsp);
void classInit{{class_name}}(int sample_rate);
void instanceResetUserInterface{{class_name}}({{class_name}}* dsp);
void instanceClear{{class_name}}({{class_name}}* dsp);
void instanceConstants{{class_name}}({{class_name}}* dsp, int sample_rate);
void instanceInit{{class_name}}({{class_name}}* dsp, int sample_rate);
void init{{class_name}}({{class_name}}* dsp, int sample_rate);
void buildUserInterface{{class_name}}({{class_name}}* dsp, UIGlue* ui_interface);
void compute{{class_name}}({{class_name}}* dsp, int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs);


int parameter_group(unsigned index) {
    switch (index) {
    {% for w in active + passive %}{% if w.group != -1 %}
    case {{loop.index0}}:
        return {{w.group}};
    {% endif %}{% endfor %}
    default:
        return -1;
    }
}

const char *parameter_label(unsigned index) {
    switch (index) {
    {% for w in active + passive %}
    case {{loop.index0}}:
        return {{cstr(w.label)}};
    {% endfor %}
    default:
        return 0;
    }
}

const char *parameter_short_label(unsigned index) {
    switch (index) {
    {% for w in active + passive %}
    case {{loop.index0}}:
        return {{cstr(w.meta.abbrev|default(w.label)|truncate(16, true))}};
    {% endfor %}
    default:
        return 0;
    }
}

const char *parameter_style(unsigned index) {
    switch (index) {
    {% for w in active + passive %}
    case {{loop.index0}}: {
        return {{cstr(w.meta.style)}};
    }
    {% endfor %}
    default:
        return "";
    }
}

const char *parameter_symbol(unsigned index) {
    switch (index) {
    {% for w in active + passive %}
    case {{loop.index0}}:
        return {{cstr(w.meta.symbol)}};
    {% endfor %}
    default:
        return "";
    }
}

const char *parameter_unit(unsigned index) {
    switch (index) {
    {% for w in active + passive %}
    case {{loop.index0}}:
        return {{cstr(w.unit)}};
    {% endfor %}
    default:
        return 0;
    }
}

{#
const ParameterRange *parameter_range(unsigned index) {
    switch (index) {
    {% for w in active + passive %}
    case {{loop.index0}}: {
        static const ParameterRange range = { {{w.init}}, {{w.min}}, {{w.max}} };
        return &range;
    }
    {% endfor %}
    default:
        return 0;
    }
}
#}

bool parameter_is_trigger(unsigned index) {
    switch (index) {
    {% for w in active + passive %}{% if w.type in ["button"] or
                                            w.meta.trigger is defined %}
    case {{loop.index0}}:
        return true;
    {% endif %}{% endfor %}
    default:
        return false;
    }
}

bool parameter_is_boolean(unsigned index) {
    switch (index) {
    {% for w in active + passive %}{% if w.type in ["button", "checkbox"] or
                                            w.meta.boolean is defined %}
    case {{loop.index0}}:
        return true;
    {% endif %}{% endfor %}
    default:
        return false;
    }
}

bool parameter_is_enum(unsigned index) {
    switch (index) {
    {% for w in active + passive %}{% if w.meta.style in ["menu", "radio"] %}
    case {{loop.index0}}:
        return true;
    {% endif %}{% endfor %}
    default:
        return false;
    }
}

bool parameter_is_integer(unsigned index) {
    switch (index) {
    {% for w in active + passive %}{% if w.type in ["button", "checkbox"] or
                                            w.meta.integer is defined or
                                            w.meta.boolean is defined %}
    case {{loop.index0}}:
        return true;
    {% endif %}{% endfor %}
    default:
        return false;
    }
}

bool parameter_is_logarithmic(unsigned index) {
    switch (index) {
    {% for w in active + passive %}{% if w.scale == "log" %}
    case {{loop.index0}}:
        return true;
    {% endif %}{% endfor %}
    default:
        return false;
    }
}

float get_parameter({{class_name}}* dsp, unsigned index) {
    switch (index) {
    {% for w in active + passive %}
    case {{loop.index0}}:
        return dsp->{{w.varname}};
    {% endfor %}
    default:
        (void)dsp;
        return 0.0;
    }
}

void set_parameter({{class_name}}* dsp, unsigned index, float value) {
    switch (index) {
    {% for w in active %}
    case {{loop.index0}}:
        dsp->{{w.varname}} = value;
        break;
    {% endfor %}
    default:
        (void)dsp;
        (void)value;
        break;
    }
}

{% for w in active + passive %}
float get_{{w.meta.symbol}}({{class_name}}* dsp) {
    return dsp->{{w.varname}};
}
{% endfor %}
{% for w in active %}
void set_{{w.meta.symbol}}({{class_name}}* dsp, float value) {
    dsp->{{w.varname}} = value;
}
{% endfor %}

#endif  /* __{{class_name}}_H__ */
