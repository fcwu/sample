LXC 1.0
=======

https://www.stgraber.org/2013/12/20/lxc-1-0-blog-post-series/


LXC is a userspace interface for the Linux kernel containment features.

Through a powerful API and simple tools, it lets Linux users easily create and manage system or application containers.



Your First Ubuntu Container [1/10]
-----------------------------------

Create a "p1" container using the "ubuntu" template and the same version of Ubuntu and architecture as the host. Pass "-- --help" to list all available options.::

    # sudo lxc-create -t ubuntu -n p1

Start the container (in the background)::

    # sudo lxc-start -n p1 -d

Enter the container in one of those ways:

1. Attach to the container's console (ctrl-a + q to detach)::

    # sudo lxc-console -n p1

2. Spawn bash directly in the container (bypassing the console login), requires a >= 3.8 kernel::

    # sudo lxc-attach -n p1

Difference between ``lxc-console`` and ``lxc-attach``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``lxc-attach`` run a process and switch namespace into the container. ``lxc-consle`` run a console via tty for the specified container.  
`nsenter <https://github.com/jpetazzo/nsenter>`_ can do the same function like ``lxc-attach``.  For example::

    $ sudo nsenter --target 26029 --mount --uts --ipc --net --pid -- /bin/bash

ssh into it
^^^^^^^^^^^^^^

::

    # sudo lxc-info -n p1
    # ssh ubuntu@<ip from lxc-info>

Stop the container in one of those ways
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Stop it from within::

    # sudo poweroff

2. Stop it cleanly from the outside::

    # sudo lxc-stop -n p1

3. Kill it from the outside::

    # sudo lxc-stop -n p1 -k


--------------------------------------------------------------------------------



Your second Container [2/10]
----------------------------

All of distro's templates can usually be found in ``/usr/share/lxc/templates``. They also all typically have extra advanced options which you can get to by passing "--help" after the "lxc-create" call (the "--" is required to split "lxc-create" options from the template's).

Create a Ubuntu container with 12.04(precise) and 32bit architecture::

    $ sudo lxc-create -n u2 -t ubuntu -- -a i386 -r precise

Auto-start
^^^^^^^^^^^^^^^^^^^^^^^^

As you may know, each container has a configuration file typically under
``/var/lib/lxc/<container name>/config`` (man 5 lxc.conf for detail)

* lxc.start.auto = 0 (disabled) or 1 (enabled)
* lxc.start.delay = 0 (delay in second to wait after starting the container)
* lxc.start.order = 0 (priority of the container, higher value means starts earlier)
* lxc.group = group1,group2,group3,... (groups the container is a member of)

When your machine starts, an init script will ask ``lxc-autostart`` to start all containers of a given group (by default, all containers which aren't in any) in the right order and waiting the specified time between them.

To illustrate that, edit /var/lib/lxc/p1/config and append those lines to the file:::

    lxc.start.auto = 1
    lxc.group = ubuntu


Freezing
^^^^^^^^^^^^^^^^^^^^^^^^

Frozen containers won't get any time allocated by the scheduler.

::

    $ sudo lxc-freeze -n u1
    $ sudo lxc-ls -f
    NAME              STATE    IPV4       IPV6  AUTOSTART  
    -----------------------------------------------------
    b1                RUNNING  -          -     NO         
    ct-ubuntu-trusty  STOPPED  -          -     NO         
    qnap              STOPPED  -          -     NO         
    u1                FROZEN   10.0.3.49  -     NO         
    u2                STOPPED  -          -     NO  
    $ lxc-unfreeze -n u1

Networking
^^^^^^^^^^^^^^^^^^^^^^^^

In depth, http://containerops.org/2013/11/19/lxc-networking/

In ``/var/lib/lxc/<container id>/config``::

    lxc.network.type = veth
    lxc.network.hwaddr = 00:16:3e:3a:f1:c1
    lxc.network.flags = up
    lxc.network.link = lxcbr0
    lxc.network.name = eth0
    
    lxc.network.type = veth
    lxc.network.link = virbr0
    lxc.network.name = virt0
    
    lxc.network.type = phys
    lxc.network.link = eth2
    lxc.network.name = eth1

Attach
^^^^^^^^^^^^^^^^^^^^^^^^

You may also use it from scripts to run actions in the container, such as:::

    $ sudo lxc-attach -n p1 -- restart ssh

But it's a lot more powerful than that. For example, take:::

    $ sudo lxc-attach -n p1 -e -s 'NETWORK|UTSNAME'

In that case, you'll get a shell that says "root@p1" (thanks to UTSNAME), running "ifconfig -a" from there will list the container's network interfaces. But everything else will be that of the host. Also passing "-e" means that the cgroup, apparmor, ... restrictions won't apply to any processes started from that shell.

Passing devices to a running containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ sudo lxc-device add -n p1 /dev/ttyUSB0 /dev/ttyS0

Which will add (mknod) /dev/ttyS0 in the container with the same type/major/minor as /dev/ttyUSB0 and then add the matching cgroup entry allowing access from the container.


-------------------------------------------------------------------------------


Advanced Container Usage [3/10]
---------------------------------

Exchanging data with a container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Access data that's in the container and on a filesystem which was mounted by the container itself (such as a tmpfs). In those cases, you can use this trick:::

    sudo ls -lh /proc/$(sudo lxc-info -n p1 -p -H)/root/run/

Well, let's say we want to have our host's /var/cache/lxc shared with "p1", we can edit /var/lib/lxc/p1/fstab and append:::

    /var/cache/lxc var/cache/lxc none bind,create=dir

Container nesting
^^^^^^^^^^^^^^^^^^^^^

So to enable nesting for our "p1" container, edit /var/lib/lxc/p1/config and add:::

    lxc.aa_profile = lxc-container-default-with-nesting

Doro: not work on up-to-date Ubuntu 14.04 (2014/08/11). Revise to as following::

    lxc.aa_profile = unconfined

The result looks::

    $ sudo lxc-ls --fancy --nesting
    NAME    STATE    IPV4                 IPV6   AUTOSTART  
    ------------------------------------------------------
    p1      RUNNING  10.0.3.82, 10.0.4.1  -      NO       
     \_ p1  RUNNING  10.0.4.7             -      NO       
    p2      RUNNING  10.0.3.128           -      NO

Raw network access
^^^^^^^^^^^^^^^^^^^^^

::

    lxc.network.type = phys
    lxc.network.hwaddr = 00:16:3e:c6:0e:04
    lxc.network.flags = up
    lxc.network.link = tap0
    lxc.network.name = eth0

Then all I have to do is start OpenVPN on my host which will connect and setup tap0, then start the container which will steal that interface and use it as its own eth0


-------------------------------------------------------------------------------


More Advanced Container Usage [4/10]
------------------------------------------

foreign architectures
^^^^^^^^^^^^^^^^^^^^^^^

::

    sudo lxc-create -t ubuntu -n p3 -- -a armhf

Hooks
^^^^^^^^^^^^^^^^^^^

The currently available hooks are (details in lxc.conf(5)):

* lxc.hook.pre-start (called before any initialization is done)
* lxc.hook.pre-mount (called after creating the mount namespace but before mounting anything)
* lxc.hook.mount (called after the mounts but before pivot_root)
* lxc.hook.autodev (identical to mount but only called if using autodev)
* lxc.hook.start (called in the container right before /sbin/init)
* lxc.hook.post-stop (run after the container has been shutdown)
* lxc.hook.clone (called when cloning a container into a new one)

Additionally each network section may also define two additional hooks:

* lxc.network.script.up (called in the network namespace after the interface was created)
* lxc.network.script.down (called in the network namespace before destroying the interface)

As a simple example, let's add the following to our "p1" container:::

    lxc.hook.pre-start = /var/lib/lxc/p1/pre-start.sh

And create the hook itself at ``/var/lib/lxc/p1/pre-start.sh``:::

    #!/bin/sh
    echo "arguments: $*" > /tmp/test
    echo "environment:" >> /tmp/test
    env | grep LXC >> /tmp/test

Make it executable (chmod 755) and then start the container.

Android containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Android kernel
2. make complex config and hook

See https://www.stgraber.org/2013/12/23/lxc-1-0-some-more-advanced-container-usage/ for detail

LXC on Android
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See https://www.stgraber.org/2013/12/23/lxc-1-0-some-more-advanced-container-usage/ for detail

-------------------------------------------------------------------------------


Container Storage [5/10]
-----------------------------

Storage backingstores
^^^^^^^^^^^^^^^^^^^^^^

It defaults to "none" which simply stores the rootfs under
``/var/lib/lxc/<container>/rootfs`` but you can specify something else to ``lxc-create`` or ``lxc-clone`` with the -B option.

* directory based storage ("none" and "dir)
* btrfs
* lvm
    - This one will use a new logical volume for the container.
    - The LV can be set with --lvname (the default is the container name).
    - The VG can be set with --vgname (the default is "lxc").
    - The filesystem can be set with --fstype (the default is "ext4").
    - The size can be set with --fssize (the default is "1G").
    - You can also use LVM thinpools with --thinpool
* overlayfs
    When used with lxc-create it'll create a container where any change done after its initial creation will be 
    stored in a "delta0" directory next to the container's rootfs.
* zfs
* aufs

Standard paths
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* /var/lib/lxc (default location for containers)
* /var/lib/lxcsnap (default location for snapshots)
* /var/cache/lxc (default location for the template cache)
* $HOME/.local/share/lxc (default location for unprivileged containers)
* $HOME/.local/share/lxcsnap (default location for unprivileged snapshots)
* $HOME/.cache/lxc (default location for unprivileged template cache)

The default path, also called lxcpath can be overridden on the command line with the -P option or once and for all by 
setting "lxcpath = /new/path" in /etc/lxc/lxc.conf (or $HOME/.config/lxc/lxc.conf for unprivileged containers).

The default configuration used for all containers at creation time is taken from
/etc/lxc/default.conf (no unprivileged equivalent yet).
The templates themselves are stored in /usr/share/lxc/templates.

Cloning containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    sudo lxc-clone u2 u3

Using aufs::

    sudo lxc-clone -B aufs -s u2 u3

/var/lxc/lxc/u3 would looks like::

    root@u-desktop:/var/lib/lxc# ls u3
    config  delta0  fstab  lxc_rdepends  rootfs
    root@u-desktop:/var/lib/lxc# cat u3/lxc_rdepends 
    /var/lib/lxc
    u2
    root@u-desktop:/var/lib/lxc# grep rootfs u3/config
    lxc.rootfs = aufs:/var/lib/lxc/u2/rootfs:/var/lib/lxc/u3/delta0

Snapshot
^^^^^^^^^^^^^^^^^^^

Create::

$ sudo lxc-snapshot -n u3 

List::

    $ sudo lxc-snapshot -n u3 -L
    snap0 (/var/lib/lxcsnaps/u3) 2014:08:12 09:51:11
    $ sudo ls /var/lib/lxc/lxcsnaps/u3/snap0/
    config        delta0/       fstab         lxc_rdepends  rootfs/       ts

Restore::

    sudo lxc-snapshot -n p1-lvm -r snap0


-------------------------------------------------------------------------------


Security features [6/10]
-----------------------------

Capabilities
^^^^^^^^^^^^^^

The two relevant configurations options are:

* lxc.cap.drop
* lxc.cap.keep

Both are lists of capability names as listed in `capabilities(7) <http://man7.org/linux/man-pages/man7/capabilities.7.html>`_.

In Ubuntu we use lxc.cap.drop to drop sys_module, mac_admin, mac_override, sys_time which prevent some known problems at container boot time.

Control groups
^^^^^^^^^^^^^^^^^

* Resource bean counting
* Resource quotas
* Access restrictions

For example to set a memory limit on p1 you'd add the following to its configuration (``/var/lib/lxc/p1/config``):::

    lxc.cgroup.memory.limit_in_bytes = 134217728

This will set a memory limit of 128MB (the value is in bytes) and will be the equivalent to writing that same value to ``/sys/fs/cgroup/memory/lxc/p1/memory.limit_in_bytes``

Most LXC templates only set a few devices controller entries by default:::

    # Default cgroup limits
    lxc.cgroup.devices.deny = a
    ## Allow any mknod (but not using the node)
    lxc.cgroup.devices.allow = c *:* m
    lxc.cgroup.devices.allow = b *:* m
    ## /dev/null and zero
    lxc.cgroup.devices.allow = c 1:3 rwm
    lxc.cgroup.devices.allow = c 1:5 rwm
    ## consoles
    lxc.cgroup.devices.allow = c 5:0 rwm
    lxc.cgroup.devices.allow = c 5:1 rwm
    ## /dev/{,u}random
    lxc.cgroup.devices.allow = c 1:8 rwm
    lxc.cgroup.devices.allow = c 1:9 rwm
    ## /dev/pts/*
    lxc.cgroup.devices.allow = c 5:2 rwm
    lxc.cgroup.devices.allow = c 136:* rwm
    ## rtc
    lxc.cgroup.devices.allow = c 254:0 rm
    ## fuse
    lxc.cgroup.devices.allow = c 10:229 rwm
    ## tun
    lxc.cgroup.devices.allow = c 10:200 rwm
    ## full
    lxc.cgroup.devices.allow = c 1:7 rwm
    ## hpet
    lxc.cgroup.devices.allow = c 10:228 rwm
    ## kvm
    lxc.cgroup.devices.allow = c 10:232 rwm


AppArmor
^^^^^^^^^^^^

Checkout lxc.aa_profile in configuration and /etc/apparmor.d/lxc/ for profile


SELinux
^^^^^^^^^^^^^

Not used

Seccomp
^^^^^^^^^^^^^

Seccomp is a fairly recent kernel mechanism which allows for filtering of system calls.

User namespace
^^^^^^^^^^^^^^^^

Introduce next time


-------------------------------------------------------------------------------


Unprivileged containers [7/10]
-----------------------------

Remap UID 0 in container to others UID in host. Enabled in 3.12 kernel. Try this if you would like to run LXC without root right.
This will map standard paths as following,

* /etc/lxc/lxc.conf => ~/.config/lxc/lxc.conf
* /etc/lxc/default.conf => ~/.config/lxc/default.conf
* /var/lib/lxc => ~/.local/share/lxc
* /var/lib/lxcsnaps => ~/.local/share/lxcsnaps
* /var/cache/lxc => ~/.cache/lxc

Doro: Not works following `this document <https://www.stgraber.org/2014/01/17/lxc-1-0-unprivileged-containers/>`_ on Ubuntu 14.04 at 2014/08/10 


Scripting with the API [8/10]
-----------------------------

Writing by C (linking to liblxc) or Python 3

Python script 1::

    import lxc
    import sys

    # Setup the container object
    c = lxc.Container("apicontainer")
    if c.defined:
        print("Container already exists", file=sys.stderr)
        sys.exit(1)

    # Create the container rootfs
    if not c.create("download", lxc.LXC_CREATE_QUIET, {"dist": "ubuntu",
                                                       "release": "trusty",
                                                       "arch": "i386"}):
        print("Failed to create the container rootfs", file=sys.stderr)
        sys.exit(1)

    # Start the container
    if not c.start():
        print("Failed to start the container", file=sys.stderr)
        sys.exit(1)

    # Query some information
    print("Container state: %s" % c.state)
    print("Container PID: %s" % c.init_pid)

    # Stop the container
    if not c.shutdown(30):
        print("Failed to cleanly shutdown the container, forcing.")
        if not c.stop():
            print("Failed to kill the container", file=sys.stderr)
            sys.exit(1)

    # Destroy the container
    if not c.destroy():
        print("Failed to destroy the container.", file=sys.stderr)
        sys.exit(1)

python script 2::

    import lxc
    import sys

    for container in lxc.list_containers(as_object=True):
        # Start the container (if not started)
        started=False
        if not container.running:
            if not container.start():
                continue
            started=True

        if not container.state == "RUNNING":
            continue

        # Wait for connectivity
        if not container.get_ips(timeout=30):
            continue

        # Run the updates
        container.attach_wait(lxc.attach_run_command,
                              ["apt-get", "update"])
        container.attach_wait(lxc.attach_run_command,
                              ["apt-get", "dist-upgrade", "-y"])

        # Shutdown the container
        if started:
            if not container.shutdown(30):
                container.stop()

python script 3::

    import lxc

    c = lxc.Container("p1")
    if not c.running:
        c.start()

    def print_hostname():
        with open("/etc/hostname", "r") as fd:
            print("Hostname: %s" % fd.read().strip())

    # First run on the host
    print_hostname()

    # Then on the container
    c.attach_wait(print_hostname)

    if not c.shutdown(30):
        c.stop()

python script 4::

    import lxc
    import os
    import sys

    if not os.geteuid() == 0:
        print("The use of overlayfs requires privileged containers.")
        sys.exit(1)

    # Create a base container (if missing) using an Ubuntu 14.04 image
    base = lxc.Container("base")
    if not base.defined:
        base.create("download", lxc.LXC_CREATE_QUIET, {"dist": "ubuntu",
                                                       "release": "precise",
                                                       "arch": "i386"})

        # Customize it a bit
        base.start()
        base.get_ips(timeout=30)
        base.attach_wait(lxc.attach_run_command, ["apt-get", "update"])
        base.attach_wait(lxc.attach_run_command, ["apt-get", "dist-upgrade", "-y"])

        if not base.shutdown(30):
            base.stop()

    # Clone it as web (if not already existing)
    web = lxc.Container("web")
    if not web.defined:
        # Clone base using an overlayfs overlay
        web = base.clone("web", bdevtype="overlayfs",
                         flags=lxc.LXC_CLONE_SNAPSHOT)

        # Install apache
        web.start()
        web.get_ips(timeout=30)
        web.attach_wait(lxc.attach_run_command, ["apt-get", "update"])
        web.attach_wait(lxc.attach_run_command, ["apt-get", "install",
                                                 "apache2", "-y"])

        if not web.shutdown(30):
            web.stop()

    # Create a website container based on the web container
    mysite = web.clone("mysite", bdevtype="overlayfs",
                       flags=lxc.LXC_CLONE_SNAPSHOT)
    mysite.start()
    ips = mysite.get_ips(family="inet", timeout=30)
    if ips:
        print("Website running at: http://%s" % ips[0])
    else:
        if not mysite.shutdown(30):
            mysite.stop()


GUI in containers [9/10]
-----------------------------

Run Chrome, google talk and skype in LXC container that shares host's /dev/dri, /dev/snd, /tmp/.X11-unix, /dev/video0 to container.
Bind PulseAudio on host to container's /home/ubuntu/.pulse_socket

See https://www.stgraber.org/2014/02/09/lxc-1-0-gui-in-containers/


Troubleshooting and debugging [10/10]
--------------------------------------

logging
^^^^^^^^

Most LXC commands take two options:

* -o, -logfile=FILE: Location of the logfile (defaults to stder)
* -l, -logpriority=LEVEL: Log priority (defaults to ERROR)

The valid log priorities are:

* FATAL
* ALERT
* CRIT
* ERROR
* WARN
* NOTICE
* INFO
* DEBUG
* TRACE

allow mount loop device
^^^^^^^^^^^^^^^^^^^^^^^

::

    lxc.aa_profile = unconfined
    lxc.cgroup.devices.allow = b 7:* rwm
    lxc.cgroup.devices.allow = c 10:237 rwm


Build on Ubuntu 14.04 (not to build .deb)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

get source::

    $ apt-get source lxc

configure::

    ./configure --build=x86_64-linux-gnu --prefix=/usr --includedir=${prefix}/include --mandir=${prefix}/share/man --infodir=${prefix}/share/info --sysconfdir=/etc --localstatedir=/var --libdir=${prefix}/lib/x86_64-linux-gnu --libexecdir=${prefix}/lib/x86_64-linux-gnu --disable-maintainer-mode --disable-dependency-tracking --libdir=${prefix}/lib/x86_64-linux-gnu --libexecdir=${prefix}/lib/x86_64-linux-gnu --with-rootfs-path=${prefix}/lib/x86_64-linux-gnu/lxc --enable-python CFLAGS="-g -O2 -fstack-protector --param=ssp-buffer-size=4 -Wformat -Werror=format-security" CPPFLAGS="-D_FORTIFY_SOURCE=2" CXXFLAGS="-g -O2 -fstack-protector --param=ssp-buffer-size=4 -Wformat -Werror=format-security" FFLAGS="-g -O2 -fstack-protector --param=ssp-buffer-size=4" GCJFLAGS="-g -O2 -fstack-protector --param=ssp-buffer-size=4" LDFLAGS="-Wl,-Bsymbolic-functions -Wl,-z,relro" --enable-doc --disable-rpath --enable-apparmor --enable-selinux --disable-lua --enable-tests --disable-cgmanager --with-distro=ubuntu

Run::

    sudo LD_PRELOAD=src/lxc/liblxc.so src/lxc/lxc-start -n u-precise -l TRACE -o a.log --share-net 1
