# -*- coding: utf-8 -*-
#
# This tool helps you to rebase package to the latest version
# Copyright (C) 2013-2014 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Authors: Petr Hracek <phracek@redhat.com>
#          Tomas Hozza <thozza@redhat.com>

import os

import git
import six

from rebasehelper.logger import logger
from rebasehelper.helpers.process_helper import ProcessHelper


class GitHelper(object):

    """Class which operates with git repositories"""

    # provide fallback values if system is not configured
    GIT_USER_NAME = 'rebase-helper'
    GIT_USER_EMAIL = 'rebase-helper@localhost.local'

    @classmethod
    def get_user(cls):
        try:
            return git.cmd.Git().config('user.name', get=True, stdout_as_string=six.PY3)
        except git.GitCommandError:
            logger.warning("Failed to get configured git user name, using '%s'", cls.GIT_USER_NAME)
            return cls.GIT_USER_NAME

    @classmethod
    def get_email(cls):
        try:
            return git.cmd.Git().config('user.email', get=True, stdout_as_string=six.PY3)
        except git.GitCommandError:
            logger.warning("Failed to get configured git user email, using '%s'", cls.GIT_USER_EMAIL)
            return cls.GIT_USER_EMAIL

    @classmethod
    def run_mergetool(cls, repo):
        # we can't use GitPython here, as it doesn't allow
        # for the command to attach to stdout directly
        cwd = os.getcwd()
        try:
            os.chdir(repo.working_tree_dir)
            ProcessHelper.run_subprocess(['git', 'mergetool'])
        finally:
            os.chdir(cwd)

    @classmethod
    def git_remote_add(cls, name, remote_url):
        repo = git.Repo(os.getcwd())
        git.remote.Remote.add(repo, name, remote_url)

    @classmethod
    def git_fetch_all(cls, remote_name):
        repo = git.Repo(os.getcwd())
        for remote in repo.remotes:
            if remote.name != remote_name:
                continue
            remote.fetch()
            for ref in remote.refs:
                remote.fetch(ref.name.split('/')[1])

    @classmethod
    def git_checkout(cls, new_branch, ref=None):
        repo = git.Repo(os.getcwd())
        if ref:
            # Create a new branch
            repo.git.checkout('-b', new_branch, ref)
        else:
            # Recreate a branch
            repo.git.checkout('-B', new_branch)

    @classmethod
    def git_push(cls, origin, branch):
        repo = git.Repo(os.getcwd())
        repo.git.push(origin, branch)

    @classmethod
    def git_branch(cls, name='rebase-helper'):
        repo = git.Repo(os.getcwd())
        repo.git.branch(name)

    @classmethod
    def git_am(cls, path):
        repo = git.Repo(os.getcwd())
        repo.git.am(path)

    @classmethod
    def git_rev_parse(cls, branch):
        repo = git.Repo(os.getcwd())
        try:
            return repo.rev_parse(branch)
        except Exception:
            return False
