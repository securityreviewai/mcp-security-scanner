# CLI for github Job

I want you to build a CLI using Python and any CLI framework within Python that allows the user to do the following operations:
1. Set up a GitHub token or a personal access token on GitHub
2. Allow the user to start a job where the CLI performs a whole bunch of activities after downloading the repository from GitHub  The user needs to provide the GitHub repository as one of the arguments in the CLI and then it needs to kick off a job. You do not have to worry about the job at the moment. I will write custom code for that but I want all of this being developed as part of the specification. Finally, as part of the kicking-off-the-job part of it, you can call that a scan operation, it needs to produce multiple types of reports. It could be a Markdown report, a JSON report

Use only `uv` as the package manager for this. Only use `uv add` and no `pip` related operations to install packages. 

The CLI needs to be used as a script so configure it to be run as an independent script