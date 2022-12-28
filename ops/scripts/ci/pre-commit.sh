# about: Tag current commit and create GitHub release
# use:
#   - cprint
set -e

PATH="/opt/local/libexec/gnubin\
:/opt/local/bin\
:/opt/local/Library/Frameworks/Python.framework/Versions/3.6/bin\
:$PATH"

REPO_DIR="/Users/novo/src/projects/utils/peltak"
SERVER_DIR="${REPO_DIR}/server"
CLIENT_DIR="${REPO_DIR}/client"

{% raw %}
function check_py_project() {
    local proj_path=$1
    local plugin_name=$(basename $proj_path)
    local header_str="#  $plugin_name  #"
    local header_len=${#header_str}
    local header_bar=$(head -c $header_len < /dev/zero | tr '\0' '#')

    cprint "<96>$header_bar"
    cprint "<96>#  <95>$plugin_name  <96>#"
    cprint "<96>$header_bar"

    cd "$proj_path"
    . ".venv/bin/activate"
    peltak ci check-commit
}
{% endraw %}

check_py_project "$REPO_DIR"
check_py_project "$REPO_DIR/plugins/peltak-changelog"
check_py_project "$REPO_DIR/plugins/peltak-gitflow"
check_py_project "$REPO_DIR/plugins/peltak-todos"

