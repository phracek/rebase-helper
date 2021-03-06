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
import shutil

import git
import pytest

from rebasehelper.patch_helper import GitPatchTool
from rebasehelper.specfile import PatchObject


class TestPatchHelper(object):

    USER = 'John Doe'
    EMAIL = 'john.doe@example.com'

    LIPSUM_OLD = 'patch_helper/lipsum_old.txt'
    LIPSUM_NEW = 'patch_helper/lipsum_new.txt'
    PATCH1 = 'patch_helper/1.patch'
    PATCH2 = 'patch_helper/2.patch'
    PATCH3 = 'patch_helper/3.patch'
    PATCH4 = 'patch_helper/4.patch'

    TEST_FILES = [
        LIPSUM_OLD,
        LIPSUM_NEW,
        PATCH1,
        PATCH2,
        PATCH3,
        PATCH4,
    ]

    @pytest.fixture
    def rebased_sources(self, workdir):
        path = os.path.join(workdir, 'rebased_sources')
        os.mkdir(path)
        return path

    @pytest.fixture
    def old_sources(self, workdir):
        path = os.path.join(workdir, 'old_sources')
        os.mkdir(path)
        return path

    @pytest.fixture
    def new_sources(self, workdir):
        path = os.path.join(workdir, 'new_sources')
        os.mkdir(path)
        return path

    @pytest.fixture
    def old_repo(self, old_sources):
        repo = git.Repo.init(old_sources)
        repo.git.config('user.name', self.USER, local=True)
        repo.git.config('user.email', self.EMAIL, local=True)
        shutil.copy(os.path.basename(self.LIPSUM_OLD), os.path.join(old_sources, 'lipsum.txt'))
        repo.git.add(all=True)
        repo.index.commit('Initial commit', skip_hooks=True)
        for n in range(1, 5):
            patch_name = os.path.basename(getattr(self, 'PATCH{0}'.format(n)))
            repo.git.apply(os.path.join(os.getcwd(), patch_name))
            repo.git.add(all=True)
            repo.index.commit(GitPatchTool.insert_patch_name('P{0}'.format(n), patch_name), skip_hooks=True)
        return repo

    @pytest.fixture
    def new_repo(self, new_sources):
        repo = git.Repo.init(new_sources)
        repo.git.config('user.name', self.USER, local=True)
        repo.git.config('user.email', self.EMAIL, local=True)
        shutil.copy(os.path.basename(self.LIPSUM_NEW), os.path.join(new_sources, 'lipsum.txt'))
        repo.git.add(all=True)
        repo.index.commit('Initial commit', skip_hooks=True)
        return repo

    @pytest.mark.parametrize('favor_on_conflict', [
        'upstream',
        'downstream',
        None,
    ], ids=[
        'favoring_upstream',
        'favoring_downstream',
        'no_favors',
    ])
    def test__git_rebase(self, rebased_sources, old_sources, new_sources, old_repo, new_repo, favor_on_conflict):
        GitPatchTool.cont = False
        GitPatchTool.non_interactive = True
        GitPatchTool.kwargs = dict(rebased_sources_dir=rebased_sources)
        GitPatchTool.old_sources = old_sources
        GitPatchTool.new_sources = new_sources
        GitPatchTool.old_repo = old_repo
        GitPatchTool.new_repo = new_repo
        GitPatchTool.favor_on_conflict = favor_on_conflict
        GitPatchTool.patches = [PatchObject(os.path.basename(getattr(self, 'PATCH{0}'.format(n))), n, 1)
                                for n in range(1, 5)]
        patches = GitPatchTool._git_rebase()  # pylint: disable=protected-access
        assert patches['untouched'] == [os.path.basename(self.PATCH1)]
        if favor_on_conflict == 'upstream':
            assert patches['modified'] == [os.path.basename(self.PATCH2)]
            assert patches['deleted'] == [os.path.basename(self.PATCH3), os.path.basename(self.PATCH4)]
            assert 'inapplicable' not in patches
        elif favor_on_conflict == 'downstream':
            assert patches['modified'] == [os.path.basename(self.PATCH2), os.path.basename(self.PATCH3)]
            assert patches['deleted'] == [os.path.basename(self.PATCH4)]
            assert 'inapplicable' not in patches
        else:
            assert patches['modified'] == [os.path.basename(self.PATCH2)]
            assert patches['deleted'] == [os.path.basename(self.PATCH4)]
            assert patches['inapplicable'] == [os.path.basename(self.PATCH3)]
        with open(os.path.join(rebased_sources, os.path.basename(self.PATCH2))) as f:
            content = f.read()
            assert 'From: {0} <{1}>\n'.format(self.USER, self.EMAIL) in content
            assert 'Subject: [PATCH] P2\n' in content
            assert GitPatchTool.decorate_patch_name(os.path.basename(self.PATCH2)) not in content
