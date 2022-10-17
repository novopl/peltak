# peltak:
#   about: Run all tests for peltak and all the plugins
peltak test
cd plugins/peltak-changelog && poetry run peltak test
