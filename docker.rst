`Docker <http://www.docker.com>`_
---------------------------------
*Develop, Ship and Run Any Application, Anywhere*

Docker is a platform for developers and sysadmins to develop, ship, and run applications. Docker lets you quickly assemble applications from components and eliminates the friction that can come when shipping code. Docker lets you get your code tested and deployed into production as fast as possible.


**Show the Docker version information**
::

    $sudo docker version
    Client version: 1.1.2
    Client API version: 1.13
    Go version (client): go1.2.1
    Git commit (client): d84a070
    Server version: 1.1.2
    Server API version: 1.13
    Go version (server): go1.2.1
    Git commit (server): d84a070


**Display system-wide information**
::

    $sudo docker info
    Containers: 22
    Images: 20
    Storage Driver: devicemapper
     Pool Name: docker-8:1-265714-pool
     Data file: /var/lib/docker/devicemapper/devicemapper/data
     Metadata file: /var/lib/docker/devicemapper/devicemapper/metadata
     Data Space Used: 1032.9 Mb
     Data Space Total: 102400.0 Mb
     Metadata Space Used: 2.6 Mb
     Metadata Space Total: 2048.0 Mb
    Execution Driver: native-0.2
    Kernel Version: 3.13.0-32-generic
    Username: xxxxx
    Registry: [https://index.docker.io/v1/]
    WARNING: No swap limit support

Dockerizing Applications
-----------------------------
Running an application inside a container takes a single command: *docker run*

Get base image
^^^^^^^^^^^^^^^^^^^
::

    $ sudo docker pull ubuntu:14.04

    $ sudo docker images
    REPOSITORY          TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
    ubuntu              14.04               c4ff7513909d        23 hours ago        213 MB
    busybox             ubuntu-14.04        37fca75d01ff        9 weeks ago         5.609 MB
    busybox             buildroot-2014.02   a9eb17255234        9 weeks ago         2.433 MB



Hello world
^^^^^^^^^^^^^
::

    $ sudo docker run ubuntu:14.04 /bin/echo "Hello world"
    Hello world

An Interactive Container
^^^^^^^^^^^^^^^^^^^^^^^^^^
The *-t* flag assigns a pseudo-tty inside our new container and the *-i* flag allows us to make an interactive connection of the container.
::

    $ sudo docker run -t -i ubuntu:14.04 /bin/bash
    root@af8bae53bdd3:/#


You can play around inside this container and when you're done you can use the *exit* command to finish.
::

    root@af8bae53bdd3:/# exit

As with our previous container, once the Bash shell process has finished, the container is stopped.


A Daemonized Hello world
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The *-d* flag tells Docker to run the container and put it in the background, to daemonize it.
::

    $ sudo docker run -d ubuntu:14.04 /bin/sh -c "while true; do echo hello world; sleep 1; done"
    1e5535038e285177d5214659a068137486f96ee5c2e85a4ac52dc83f2ebe4147

The *docker ps* command queries the Docker daemon for information about all the containers it knows about.
::

    $ sudo docker ps
    CONTAINER ID  IMAGE         COMMAND               CREATED        STATUS       PORTS NAMES
    1e5535038e28  ubuntu:14.04  /bin/sh -c 'while tr  2 minutes ago  Up 1 minute        insane_babbage


The *-a* for ps means all. You can see all of your containers.
::

    $ sudo docker ps -a
    CONTAINER ID  IMAGE         COMMAND               CREATED        STATUS                      PORTS NAMES
    1e5535038e28  ubuntu:14.04  /bin/sh -c 'while tr  2 minutes ago  Up 1 minute                 insane_babbage
    1677fc800eb2  ubuntu:14.04  /bin/bash             11 minutes ago Exited (0) 10 minutes ago   cranky_mayer

Container logs
^^^^^^^^^^^^^^
::

    $ sudo docker logs <container_id>

**Tailing logs** *(After version 1.1.0)*

You can now tail the logs of a container. 

For example, you can get the last ten lines of a log by using :
::

$ docker logs --tail 10 <container_id> 

You can also follow the logs of a container without having to read the whole log file with. ::

$ docker logs --tail 0 -f <container_id>



Start/Stop container
^^^^^^^^^^^^^^^^^^^^^^
::

    $ sudo docker start
    $ sudo docker stop

Remove container/image
^^^^^^^^^^^^^^^^^^^^^^^^
Images can be removed either by their short or long ID`s, or their image names.
::

    $ sudo docker rm <container_id>
    $ sudo docker rmi <image_id>


Ports
^^^^^^^^^^^^^^^^^^^^^^^^
**Bind container port**

Use *-p* to publish a container's port to the host.

After *docker run*, it use *docker port* to see the actual mapping.
::

   $ sudo docker run -it -p 8000:80 user/supervisord 

**Bind random port**

Ports are published in random high number ports.
::

    $ sudo docker run -it -p 80 user/supervisord 

**Bind UDP port**

::

    $ sudo docker run -it -p 8000:80/udp colinhuang/supervisord


**Publish all ports**

*-P* maps all exposed ports in the container.
::

    $ sudo docker run -it -P colinhuang/supervisord



Volumes
^^^^^^^^^^^^^^^^^^^^^^^^

**Create a volume**
::

    $ sudo docker run -it -v /tmp ubuntu:14.04 /bin/bash
    root@02d027999022:/# touch /tmp/hello_world.txt

::

    $ docker inspect <container_id> | grep \"Volumes\" -A 2
    "Volumes": {
        "/tmp": "/var/lib/docker/vfs/dir/1810314edc60faab2276e4311dab87b87db96a308893b988c44b73fbe49c156d"
    },

The folder /var/lib/docker is outside the container.

*The volumes persist even if the container is stopped.* 

::

    $ sudo ls -la /var/lib/docker/vfs/dir/1810314edc60faab2276e4311dab87b87db96a308893b988c44b73fbe49c156d
    -rw-r--r--  1 root root    0 Jul  3 12:52 hello_world.txt


**Mount custom directory**
::

    $ sudo docker run -it -v <host_dir_path>:<container_path> ubuntu:14.04 
    //Example
    $ sudo docker run -it -v /home/vagrant/docker/volume:/tmp ubuntu:14.04 ls /tmp

**Mount in read only mode**

Just add *ro* after container mount path.
::

    $ sudo docker run -it -v /home/vagrant/docker/volume:/tmp:ro ubuntu:14.04 /bin/bash
    $ touch /tmp/ro
    $ touch: cannot touch '/tmp/ro': Read-only file system

**Bind mounting your whole filesystem in a container** *(After version 1.1.0)* 

*"/"* is now allowed as source of `--volumes`. 
::

$ docker run -v /:/my_host ubuntu:14.04 ls /my_host. 

However, it is now forbidden to mount to **/**.

**Share volumes betweeen containers**

You can use *--volumes-from* to mount volumes from the specified container(s).
::

    // This is container 1
    $ sudo docker run -it --name test1 -v /opt ubuntu:14.04 /bin/bash
    root@bcdf19d53634:/# touch /opt/c1

    //This is container 2
    $ sudo docker run -it --volumes-from test1 ubuntu:14.04 /bin/bash
    root@7442f73f0468:/# ls /opt
    c1  

Dockerfiles
-----------------------------
Usage
::
 
    $ sudo docker build -t <new_image_name> <path>
    //Example:
    $ sudo docker build -t shykes/myapp .

Whenever possible, Docker will re-use the intermediate images, accelerating *docker build* significantly 

Here is the format of the *Dockerfile*:
::

    # Comment
    INSTRUCTION arguments

Example forms:
::

    FROM <image>:<tag>
    MAINTAINER <name>
    RUN <command>
    EXPOSE <port> 
    VOLUME ["/data"]
    WORKDIR /path/to/workdir
    CMD ["executable","param1","param2"]
    ENTRYPOINT ["executable", "param1", "param2"]

More detail: http://docs.docker.com/reference/builder/


Docker Hub
-----------------------------
Register your account by https://hub.docker.com/
::

    $ sudo docker login
    Username: 
    Password:
    Email:
    Login Succeeded

Your authentication credentials will be stored in the *.dockercfg* authentication file in your home directory.

**Searching and pull for images**

You can search the Docker Hub registry via its search interface or by using the command line interface.
::

    $ sudo docker search centos

Once you've found the image you want, you can download it with *docker pull <imagename>*:

::

    $ sudo docker pull ubuntu:14.04
    Pulling repository ubuntu:14.04
    0b443ba03958: Download complete
    539c0211cd76: Download complete


**Commit your own image**
::

    $ sudo docker commit <container_id> REPOSITORY[:tags]

You can also pause containers during commit. *(After version 1.1.0)*

Because doing a commit on a running container was **not** recommended. 
::

$ docker commit --pause=false <container_id>



**Pushing a repository to Docker Hub**

In order to push a repository to its registry, you need to have named an image or committed your container to a named image. 
::

$ sudo docker push yourname/newimage
