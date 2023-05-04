# peltak:
#   about: Run all checks (types, pep8, code style)
#   options:
#     - name: ['--fix']
#       is_flag: true
#       about: Attempt to fix some of the failed checks (like isort).
#   files:
#     paths:
#       - src/peltak
#       - test/unit
#     include: '*.py'
#     use_gitignore: true
#   use:
#     - cprint
#     - header

# The weird {{ files | wrap_paths }} notation means the files will be collected
# by the script command and passed onto the 3rd party tool. This allows use
# to use the same command implementation for 'peltak check' and
# 'peltak run check-commit'.
{% if not files %}
  cprint "<90>No relevant staged files - skipping lint..."
  exit 0
{% endif %}

header 'mypy'
time mypy --config-file=ops/tools/mypy.ini {{ files | wrap_paths }}
mypy_ret=$?

header 'pycodestyle'
time pycodestyle  --config=ops/tools/pycodestyle.ini {{ files | wrap_paths }};
pycodestyle_ret=$?

header 'flake8'
time flake8 --config=ops/tools/flake8.ini {{ files | wrap_paths }}
flake8_ret=$?

header 'isort'
isort_log=$(time isort \
  --settings-file=ops/tools/isort.ini \
  {% if not opts.fix %} --check-only --diff \{% endif %} \
  {{ files | wrap_paths }} \
)
isort_ret=$?

echo "$isort_log" {%if not opts.fix %} | colordiff{% endif %}

header 'done'

# Run everything first so we can see all errors on 1 run. Fail if any of the checks
# failed
if [[ $mypy_ret -ne 0 || $pycodestyle_ret -ne 0 || $flake8_ret -ne 0 || $isort_ret -ne 0 ]]; then
  cprint "<91>FAILED"
  exit 1
else
  cprint "<92>SUCCESS"
fi
