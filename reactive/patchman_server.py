#!/usr/bin/env python

from charmhelpers.contrib.ansible import apply_playbook
from charmhelpers.core.hookenv import status_set
from charms.reactive.decorators import hook
from charms.reactive.decorators import when
from charms.reactive.decorators import when_not
from charms.reactive.flags import clear_flag
from charms.reactive.flags import register_trigger
from charms.reactive.flags import set_flag
from charms.reactive.relations import endpoint_from_name

register_trigger(when='config.changed',
                 clear_flag='patchman.server.configured')


@when_not('patchman.server.configured')
def configure_patchman():
    status_set('maintenance', 'configuring patchman server')
    apply_playbook(playbook='ansible/playbook.yaml')
    status_set('active', 'ready')
    set_flag('patchman.server.configured')


@when('patchman.available')
@when('patchman.server.configured')
def configure_patchman_interface():
    interface = endpoint_from_name('patchman')
    interface.configure(port=80)


# Hooks
@hook('stop')
def cleanup():
    apply_playbook(playbook='ansible/playbook.yaml', tags=['uninstall'])


@hook('upgrade-charm')
def upgrade_charm():
    clear_flag('patchman.server.configured')
