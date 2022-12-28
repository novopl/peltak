# peltak:
#   about: Run all tests for peltak and all the plugins
#   use:
#     - cprint
#     - header
peltak test
cd plugins/peltak-changelog && poetry run peltak test
