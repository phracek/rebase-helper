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

import six

from rebasehelper.plugins import Plugin, PluginLoader
from rebasehelper.logger import logger
from rebasehelper.results_store import results_store


class BaseBuildLogHook(Plugin):
    """Base class for a build log hook."""

    # build log hook categories, see PACKAGE_CATEGORIES in constants for a complete list
    CATEGORIES = None

    @classmethod
    def format(cls, data):
        """Formats build log hook output to a readable text form."""
        raise NotImplementedError()

    @classmethod
    def run(cls, spec_file, rebase_spec_file, results_dir, **kwargs):
        """Runs the build log hook.

        Args:
            spec_file (rebasehelper.specfile.SpecFile): Original SpecFile object.
            rebase_spec_file (rebasehelper.specfile.SpecFile): Rebased SpecFile object.
            kwargs (dict): Keyword arguments from instance of Application.

        Returns:
            tuple: The first element is a dict containing changes, the second is a bool whether
            the build process should be restarted.

        """
        raise NotImplementedError()

    @classmethod
    def merge_two_results(cls, old, new):
        raise NotImplementedError()


class BuildLogHookRunner(object):
    def __init__(self):
        self.build_log_hooks = PluginLoader.load('rebasehelper.build_log_hooks')

    def get_all_tools(self):
        return list(self.build_log_hooks)

    def get_supported_tools(self):
        return [k for k, v in six.iteritems(self.build_log_hooks) if v]

    def run(self, spec_file, rebase_spec_file, non_interactive, force_build_log_hooks, **kwargs):
        """Runs all non-blacklisted build log hooks.

        Args:
            spec_file (rebasehelper.specfile.SpecFile): Original SpecFile object.
            rebase_spec_file (rebasehelper.specfile.SpecFile): Rebased SpecFile object.
            kwargs (dict): Keyword arguments from instance of Application.

        Returns:
            bool: Whether build log hooks made some changes to the SPEC file.

        """
        changes_made = False
        if not non_interactive or force_build_log_hooks:
            blacklist = kwargs.get('build_log_hook_blacklist', [])
            for name, build_log_hook in six.iteritems(self.build_log_hooks):
                if not build_log_hook or name in blacklist:
                    continue
                categories = build_log_hook.CATEGORIES
                if not categories or spec_file.category in categories:
                    logger.info('Running %s build log hook.', name)
                    result, rerun = build_log_hook.run(spec_file, rebase_spec_file, **kwargs)
                    result = build_log_hook.merge_two_results(results_store.get_build_log_hooks().get(name, {}), result)
                    results_store.set_build_log_hooks_result(name, result)
                    if rerun:
                        changes_made = True
        return changes_made


# Global instance of BuildLogHookRunner. It is enough to load it once per application run.
build_log_hook_runner = BuildLogHookRunner()
