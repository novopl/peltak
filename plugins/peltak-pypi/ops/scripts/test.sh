# peltak:
#   about: Run tests
#   options:
#     - name: ['-k', '--kind']
#       about: 'Kind of tests to run: all/unit/doctest. Defaults to all.'
#       type: str
#       default: all
#     - name: ['-no-sugar']
#       about: Disable pytest-sugar. Might be useful for CI runs.
#       is_flag: true
#     - name: ['--cov-xml']
#       about: Generate junit XML coverage report. Useful for 3rd party integrations.
#       is_flag: true
{% set pkg_name = 'peltak_pypi' %}
{% set cov_html_path = conf.build_dir  + '/coverage' %}

{% if opts.kind in ('all', 'doctest') %}
  {{ "Running doctests" | header }}
  pytest \
    --doctest-modules \
    --doctest-report ndiff \
    {{ ctx.verbose | count_flag('v') }} \
    {{ '-p no:sugar' if opts.no_sugar else '' }} \
    src/{{ pkg_name }} docs/src

  # We do not fail if there are not doctests (would prevent running tests below).
  if [ $# -ne 0 ] && [ $# -ne 5 ]; then
    exit 127
  fi
{% endif %}

set -e

{% if opts.kind != 'doctest' %}
  {{ "Running tests" | header }}
  pytest \
    --cov=src/{{ pkg_name }} \
    --cov-report=term:skip-covered \
    --cov-report=html:{{ cov_html_path }} \
    {{ '--cov-report=xml' if opts.cov_xml else '' }} \
    {{ ctx.verbose | count_flag('v') }} \
    {{ '-p no:sugar' if opts.no_sugar else '' }} \
    tests
{% endif %}


{% if opts.kind != 'doctest' %}
  {% set cov_path = proj_path(cov_html_path, 'index.html') %}
  {{ '\n<32>HTML report: <34>file://{}' | cprint(cov_path) }}
{% endif %}
