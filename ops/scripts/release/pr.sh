# peltak:
#   about: Create PR for the current release branch
gh pr create \
  --repo novopl/peltak \
  --title "Release: v$(peltak version --porcelain)" \
  --body "$(peltak changelog)"
