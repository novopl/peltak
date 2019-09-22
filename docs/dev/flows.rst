#####
Flows
#####

When `peltak`_ command is executed, it will run `peltak.main:root_cli()` as the
entry point.


Execution order
===============

.. uml::

    participant "peltak.main" as main
    participant "root_cli()" as root_cli
    participant "conf.load()" as load
    participant "conf.load_yaml_config()" as load_yaml_config
    participant "util.load_yaml()" as load_yaml
    participant "<command_file> from pelconf.yaml " as command

    main -> load: Load project configuration
    load -> load_yaml_config: Load ""pelconf.yaml""
    load_yaml_config -> load_yaml: Parse ""pelconf.yaml""
    load_yaml_config -> command: Import command file. \nThis will run the code in the module root.
    load_yaml_config <-- command
    load_yaml_config -> command: Import next command file.
    load_yaml_config <-- command
    load <-- load_yaml_config
    main <-- load
    main -> root_cli: Parse command line and \nexecute appropriate command.
