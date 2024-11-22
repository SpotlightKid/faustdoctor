{% block HeaderDescription -%}
//------------------------------------------------------------------------------
// This file was generated using the Faust compiler (https://faust.grame.fr),
// and the Faust post-processor (https://github.com/SpotlightKid/faustdoctor).
//
// Source: {{filename}}
// Name: {{name}}
// Author: {{author}}
// Copyright: {{copyright}}
// License: {{license}}
// Version: {{version}}
// FAUST version: {{faustversion}}
// FAUST compilation options: {{meta.compile_options}}
//------------------------------------------------------------------------------
{% endblock %}
#ifndef  __{{classname}}_H__
#define  __{{classname}}_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif

#ifndef FAUSTCLASS
#define FAUSTCLASS {{classname}}
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

{{classname}}* new{{classname}}();
void delete{{classname}}({{classname}}* dsp);
void metadata{{classname}}(MetaGlue* m);
int getSampleRate{{classname}}({{classname}}* RESTRICT dsp);
int getNumInputs{{classname}}({{classname}}* RESTRICT dsp);
int getNumOutputs{{classname}}({{classname}}* RESTRICT dsp);
void classInit{{classname}}(int sample_rate);
void instanceResetUserInterface{{classname}}({{classname}}* dsp);
void instanceClear{{classname}}({{classname}}* dsp);
void instanceConstants{{classname}}({{classname}}* dsp, int sample_rate);
void instanceInit{{classname}}({{classname}}* dsp, int sample_rate);
void init{{classname}}({{classname}}* dsp, int sample_rate);
void buildUserInterface{{classname}}({{classname}}* dsp, UIGlue* ui_interface);
void compute{{classname}}({{classname}}* dsp, int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs);

typedef struct {
    FAUSTFLOAT init;
    FAUSTFLOAT min;
    FAUSTFLOAT max;
} ParameterRange;

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
{%- endfor %}
    default:
        return 0;
    }
}

const ParameterRange *parameter_range(unsigned index) {
    switch (index) {
{% for w in active + passive %}
    case {{loop.index0}}: {
        static const ParameterRange range = { {{w.init}}, {{w.min}}, {{w.max}} };
        return &range;
    }
{%- endfor %}
    default:
        return 0;
    }
}

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

FAUSTFLOAT get_parameter({{classname}}* dsp, unsigned index) {
    switch (index) {
{% for w in active + passive %}
    case {{loop.index0}}:
        return dsp->{{w.varname}};
{%- endfor %}
    default:
        (void)dsp;
        return 0.0;
    }
}

void set_parameter({{classname}}* dsp, unsigned index, FAUSTFLOAT value) {
    switch (index) {
{% for w in active %}
    case {{loop.index0}}:
        dsp->{{w.varname}} = value;
        break;
{%- endfor %}
    default:
        (void)dsp;
        (void)value;
        break;
    }
}

{% for w in active + passive %}
FAUSTFLOAT get_{{w.meta.symbol}}({{classname}}* dsp) {
    return dsp->{{w.varname}};
}
{% endfor %}
{% for w in active %}
void set_{{w.meta.symbol}}({{classname}}* dsp, FAUSTFLOAT value) {
    dsp->{{w.varname}} = value;
}
{% endfor %}

#endif  /* __{{classname}}_H__ */
