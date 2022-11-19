# peltak:
#   about: Create a release commit
#   options:
#     - name: ['-t', '--type']
#       about: "Type of release to make: patch|minor|major. Defaults to 'patch'."
#       type: str
#       default: patch
{{ "-- <32>Creating <95>{}<32> release" | cprint(opts.type) }}

peltak version bump {{ opts.type }}
git add {{ conf.version.files | wrap_paths }}

TAG="peltak-gitflow-v$(peltak version --porcelain)"

echo "Creating release $TAG"
git commit -m "$TAG"

echo "Tagging release $TAG"
git tag -a "$TAG" -m "$TAG"

echo "Pushing released tag $TAG"
git push origin "$TAG"
