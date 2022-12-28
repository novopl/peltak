# peltak:
#   root_cli: true
#   about: Generate sphinx documentation
#   options:
#     - name: ['--recreate']
#       about: Delete build and out directories before running.
#       is_flag: true
#     - name: ['--run-doctests']
#       about: Also run all doctests.
#       is_flag: true
#   use:
#     - cprint
#     - header
{% if opts.recreate %}
  header 'Cleaning after previous builds'

  header '<91>Deleting <94>docs/html'
  rm -rf docs/html

  header '<91>Deleting <94>.build/docs'
  rm -rf .build/docs
{% endif %}

header 'Generating documentation'
sphinx-build \
    -b html \
    -d {{ conf.build_dir }}/docs \
    docs/src \
    docs/html

{% if opts.run_doctests %}
  header 'Running doctests'
  sphinx-build \
      -b doctest \
      -d {{ conf.build_dir }}/docs \
      docs/src \
      docs/doctest
{% endif %}

{% set docs_path = proj_path('docs/html/index.html') %}
cprint '<32>Documentation: <34>{{docs_path }}'
