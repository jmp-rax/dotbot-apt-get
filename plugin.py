#!/usr/bin/env python3

import dotbot
import subprocess
import os
from enum import IntEnum

apt_get_update_cmd = "apt-get update"
apt_get_install_cmd_fmt = "apt-get install {} --assume-yes"
get_substituion_name_fmt = "echo {}"

class AptGetOutput(IntEnum):
    UNKNOWN_STATE = -1
    SUCCESSFULLY_INSTALLED = 0
    ALREADY_INSTALLED = 1

class DotbotAptGet(dotbot.Plugin):
    """Dotbot plugin for apt-get, goal is to make this 2 / 3 compliant"""

    _directive = 'apt-get'

    def __init__(self, context):
        super(DotbotAptGet, self).__init__(self)
        self._context = context
        self._debug = False
        self._bail = False

    def can_handle(self, directive):
        """Checks to see if this plugin can handle the directive

        Args:
            directive (str): directive from the yaml configuration file

        Returns:
            bool: False if not root, or false if cannot handle directive else True
        """

        if not os.geteuid() == 0:
            self._log.error("Root privileges are required to install apt packages")
            return False

        return directive == self._directive

    @staticmethod
    def _run(cmd, shell=False):

        if shell is False:
            cmd = cmd.split(' ')

        out = subprocess.Popen(cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=shell)

        output = out.communicate()[0]
        ret = out.returncode

        return ret, output

    def _update(self):
        """
            performs an update on the package manager
        Returns:
            bool: true if it succeeds, false otherwise
        """

        ret, output = self._run(apt_get_update_cmd, shell=True)
        self._log.debug(output)

        if ret != 0:
            self._log.error(output)
            return False

        return True

    def _install(self, package):
        """Installs a give package with apt

        Args:
            package str: package to install

        Returns:
            AptGetOuput: enum describing what happened
        """

        package_name = package
        if "$(" in package_name or '`' in package_name:
            # TODO need a better way to detect if the package needs substitution
            subname_cmd = get_substituion_name_fmt.format(package)
            _, tmp_name = self._run(subname_cmd, shell=True)
            package_name = tmp_name.decode().strip()

        cmd = apt_get_install_cmd_fmt.format(package_name)
        self._log.debug(cmd)

        _, output = self._run(cmd)
        self._log.debug(output)

        if "Setting up {}".format(package_name).encode() in output:
            return AptGetOutput.SUCCESSFULLY_INSTALLED

        if b"is already the newest version" in output:
            return AptGetOutput.ALREADY_INSTALLED


        return AptGetOutput.UNKNOWN_STATE

    def handle_workflow(self, workflow):
        """handles each workflow in the following order
            custom - update - packages

        Args:
            workflow (dict): dictionary with keys 'custom', 'update', or
            'packages'

        Returns:
            bool: True if commands succeeded or _bail was set to false
        """

        if 'custom' in workflow:
            for custom_cmd in workflow['custom']:
                if custom_cmd is None:
                    continue

                ret, output = self._run(custom_cmd, shell=True)
                if ret != 0:
                    self._log.error(output.decode())
                    if self._bail:
                        return False
                else:
                    self._log.lowinfo(output.decode())

        if 'update' in workflow:
            if workflow['update'] == True:
                if self._update() is False:
                    self._log.error("apt-get update failed")
                    return False

        if 'packages' in workflow:
            for package in workflow['packages']:
                apt_result = self._install(package)
                if apt_result < AptGetOutput.SUCCESSFULLY_INSTALLED and self._bail == True:
                    self._log.error("Failed to install {}, bailing because option bail was set to True"
                        .format(package))
                    return False
                elif apt_result < AptGetOutput.SUCCESSFULLY_INSTALLED:
                    self._log.error("Failed to install {}, but continuing anyways"
                        .format(package))

        return True

    def handle(self, _, data):
        if 'options' in data:
            if 'bail' in data['options']:
                self._bail = True
        if 'workflows' in data:
            for flows in data['workflows']:
                for key in flows:
                    self.handle_workflow(flows[key])

        return True
