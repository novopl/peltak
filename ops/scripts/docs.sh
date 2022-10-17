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
{% if opts.recreate %}
  {{ 'Cleaning after previous builds' | header }}

  {{ '<91>Deleting <94>docs/html' | cprint }}
  rm -rf docs/html

  {{ '<91>Deleting <94>.build/docs' | cprint }}
  rm -rf .build/docs
{% endif %}

{{ 'Generating documentation' | header }}
sphinx-build \
    -b html \
    -d {{ conf.build_dir }}/docs \
    docs/src \
    docs/html

{% if opts.run_doctests %}
  {{ 'Running doctests' | header }}
  sphinx-build \
      -b doctest \
      -d {{ conf.build_dir }}/docs \
      docs/src \
      docs/doctest
{% endif %}

{% set docs_path = proj_path('docs/html/index.html') %}
{{ '<32>Documentation: <34>{}' | cprint(docs_path) }}
