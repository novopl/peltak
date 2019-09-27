#########
Dev Notes
#########


**peltak** is a command line tool to automate a lot of project related tasks.
The tool should only wrap up existing project tools and not try to replace them.
Also when implementing new commands lean towards just calling external tools
rather than interfacing through the API. This way the commands implementation
should resemble shell scripts in their structure and also serve as a reference
on how to call the respective 3rd party tool without the use of **peltak**.
Docker commands are a good example here as docker has a great python support
but reading through the command implementation you know exactly what to do to
do it manually and you probably don't even have to know python.

**WARNING: Beta:** The project is mainly lacking good documentation and
tutorials. The commands themselves are documented quite well, but there is
no generic documentation or guides on how to extend and customize peltak.

Right now only ``peltak.core`` is unit tested. The commands themselves are
tested manually in multiple projects that use peltak for day to day management
and CI runs. Before 1.0, the commands implementation should also be unit tested.
Only the CLI interface shouldn't (e2e tests for that if any).
