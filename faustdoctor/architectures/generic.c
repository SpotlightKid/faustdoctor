{% block ImplementationDescription %}
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

{% block ImplementationPrologue %}
{% endblock %}
{% block ImplementationIncludeHeader %}
#include "{{classname}}.h"
{% endblock %}
{% block ImplementationIncludeExtra %}
{% endblock %}

//------------------------------------------------------------------------------
// Begin the Faust code section

{% block ImplementationFaustCode %}
#if defined(__GNUC__)
#   pragma GCC diagnostic push
#   pragma GCC diagnostic ignored "-Wunused-parameter"
#endif

{{ classcode  | replace('\t', '    ') }}

#if defined(__GNUC__)
#   pragma GCC diagnostic pop
#endif
{% endblock %}

//------------------------------------------------------------------------------
// End the Faust code section

{% block ImplementationEpilogue %}
{% endblock %}
