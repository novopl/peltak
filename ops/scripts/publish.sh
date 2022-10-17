# peltak:
#   about: Publish to PyPI repo
#   options:
#     - name: ['-r', '--repo']
#       about: Target PyPI repository.
#       type: str
#     - name: ['-n', '--dry-run']
#       about: Target PyPI repository.
#       is_flag: true
#     - name: ['-u', '--username']
#       about: PyPI repo username
#       type: str
#     - name: ['-p', '--password']
#       about: PyPI repo password
#       type: str
poetry publish \
  --build \
  {{ ('-r ' + opts.repo) if opts.repo else '' }} \
  {{ '--dry-run' if opts.dry_run else '' }} \
  {{ '-u {}'.format(opts.username) if opts.username else '' }} \
  {{ '-p {}'.format(opts.password) if opts.password else '' }}
