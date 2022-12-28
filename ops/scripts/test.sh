# peltak:
#   root_cli: true
#   about: Run tests
#   options:
#     - name: ['-k', '--kind']
#       about: |
#         What kind of tests should be ran (all/unit/e2e/doctest). If not given,
#         then alltests will run.
#       type: str
#       default: all
#     - name: ['-no-sugar']
#       about: Disable pytest-sugar. Might be useful for CI runs.
#       is_flag: true
#     - name: ['--cov-xml']
#       about: Generate junit XML coverage report. Useful for 3rd party integrations.
#       is_flag: true
#     - name: ['--cov']
#       about: |
#         What type of coverage should we define. Allowed values are:
#         all/core/scripts/extra. Defaults to 'all'.
#       type: str
#       default: all
#   use:
#     - cprint
#     - header
set -e

{%
set test_paths = {
  'all': ['test'],
  'unit': ['test/unit'],
  'e2e': ['test/e2e'],
  'doctest': ['src/peltak'],
}.get(opts.kind, ['.'])
%}

{# --cov        source dir                  out dir #}
{%
set cov_config = {
  'all':      ('src/peltak',                '.build/coverage'),
  'core':     ('src/peltak/core',           '.build/coverage/core'),
  'extra':    ('src/peltak/extra',          '.build/coverage/extra'),
  'scripts':  ('src/peltak/extra/scripts',  '.build/coverage/extra/scripts'),
}.get(opts.cov, ('', ''))
%}

{% if not cov_config[0] and not cov_config[1] %}
  cprint "<31>Invalid <35>--cov <31>option value: <33>{{ opts.cov }}"
  exit 1
{%  endif %}

{% set cov_path = cov_config[0] %}
{% set cov_html_path = cov_config[1] %}


{% if opts.kind != 'doctest' %}
  header "Running tests"
  pytest \
      -c ops/tools/pytest.ini \
      --cov={{ cov_path }} \
      --cov-report=term \
      --cov-report=html:{{ cov_html_path }} \
      {{ ctx.verbose | count_flag('v') }} \
      {{ '\n-p no:sugar' if opts.no_sugar else '' }} \
      {{ test_paths | wrap_paths }}
{% endif %}


{% if opts.kind in ('all', 'doctest') %}
  header "Running doctests"
  pytest \
      -c ops/tools/pytest.ini \
      --doctest-modules \
      --doctest-report ndiff \
      {{ ctx.verbose | count_flag('v') }} \
      {{ '\n-p no:sugar' if opts.no_sugar else '' }} \
      src/peltak
{% endif %}

cprint "<32>HTML report: <34>file://{{ proj_path(cov_html_path, 'index.html') }}"
