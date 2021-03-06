# Welcome to rebase-helper

[![Travis CI build status](https://travis-ci.org/rebase-helper/rebase-helper.svg?branch=master)](https://travis-ci.org/rebase-helper/rebase-helper) [![Documentation build status](https://readthedocs.org/projects/rebase-helper/badge/?version=latest)](https://readthedocs.org/projects/rebase-helper) [![GitLab CI build status](https://gitlab.com/rebase-helper/rebase-helper/badges/master/build.svg)](https://gitlab.com/rebase-helper/rebase-helper/commits/master) [![PyPI version](https://img.shields.io/pypi/v/rebasehelper.svg)](https://pypi.org/project/rebasehelper) [![Project status](https://img.shields.io/pypi/status/rebasehelper.svg)](https://pypi.org/project/rebasehelper) [![Code Quality](https://api.codacy.com/project/badge/Grade/af059c941cd94f7aa557c3ae7ce75bb8)](https://www.codacy.com/app/rebase-helper/rebase-helper)

There are several steps that need to be done when rebasing a package. The goal of **rebase-helper** is to automate most of these steps.

## How to get it running?

**rebase-helper** is packaged in Fedora, so you can just install it with **dnf**.

If you wish to use the latest codebase, consult [installation instructions](https://rebase-helper.readthedocs.io/en/latest/user_guide/installation.html).

## How to use it?

After installation, execute **rebase-helper** from a directory containing SPEC file, sources and patches (usually cloned dist-git repository).

Without any arguments or configuration **rebase-helper** will attempt to determine the latest upstream version automatically.
If that fails, or if you wish to rebase to some different version, you can specify it explicitly as an argument:

`$ rebase-helper 3.1.10`

or you can pass source tarball filename instead:

`$ rebase-helper foo-4.2.tar.gz`

For complete CLI reference see [usage](https://rebase-helper.readthedocs.io/en/latest/user_guide/usage.html).

Alternatively, you can run **rebase-helper** in a container:

`$ docker run -it -e PACKAGE=foo rebasehelper/rebase-helper:latest`

See [docker reference](https://rebase-helper.readthedocs.io/en/latest/user_guide/rebasing_in_container.html) for more information.

## What do I get from it?

**rebase-helper** always creates *rebase-helper-results* directory containing the following items:

| Path                  | Description                                                       |
|:--------------------- |:----------------------------------------------------------------- |
| *report.txt*          | summary report with all important information                     |
| *changes.patch*       | diff against original files, directly applicable to dist-git repo |
| *logs/*               | log files of various verbosity levels                             |
| *rebased-sources/*    | git repository with all modified files                            |
| *checkers/*           | reports from individual checkers that were run                    |
| *old-build/*          | logs and results of old (original) version build                  |
| *new-build/*          | logs and results of new (rebased) version build                   |

## How does it work?

The following steps describe a rebase process:

- **Preparation**

    - *rebase-helper-workspace* and *rebase-helper-results* directories are created
    - original SPEC file is copied to *rebase-helper-results/rebased-sources* directory and its Version tag is modified


- **Getting sources**

    - old and new source tarballs are downloaded and extracted to *rebase-helper-workspace* directory
    - old sources are downloaded from lookaside cache if possible


- **Downstream patches**

    - new git repository is initialized and the old sources are extracted and commited
    - each downstream patch is applied and changes introduced by it are commited
    - new sources are extracted and added as a remote repository
    - `git-rebase` is used to rebase the commits on top of new sources
    - original patches are modified/deleted accordingly
    - resulting files are stored in *rebase-helper-results/rebased-sources*
    - diff against original files is saved to *rebase-helper-results/changes.patch*


- **Build**

    - old and new source RPMs are created and built with selected build tool
    - old SRPM and RPMs can also be downloaded from Koji to speed up the rebase


- **Comparison**

    - multiple checker tools are run against both sets of packages and their output is stored in *rebase-helper-results/checkers* directory


- **Cleanup**

    - *rebase-helper-workspace* directory is removed

## Video presentation

At DevConf.cz 2016, Tomáš Hozza, Petr Hráček presented on rebase-helper.

[![rebase-helper presentation at DevConf.cz 2016](https://img.youtube.com/vi/Y-5Qiwaujd8/0.jpg)](https://www.youtube.com/watch?v=Y-5Qiwaujd8)
