Docker container as Development Environment
###########################################

:date: 2018-04-14 13:15 +0530
:author: copyninja
:slug: docker-dev-environment
:tags: docker, container
:summary: Post describing how Docker can be used to create uniform development
          environment in development teams.

When you have a distributed team working on a project, you need to make sure
that every one uses similar development environment. This is critical if you are
working on embedded systems project. There are multiple possibility for this
scenario.

1. Use a common development server and provide every developer in your team an
   account in it.
2. Provide description to every one how to setup their development environment
   and trust them they will do so.
3. Use Docker to provide the developer with ready made environment and use
   build server (CI) for creating final deployment binaries.

1st approach was most common approach used, but it has some drawbacks. Since its
a shared system you should make sure not every one is able to install or modify
system and hence have a single administrator so that no one accidentally breaks
the development environment. Other problems include forced to use older OS due
to specific requirements of compilers etc.

2nd approach makes you put your trust on your developer to get the correct
development environment. Of course you need to trust your team, but every one is
a human being and humans can make mistake.

Enter Docker
============

*Dockerfile* is best way to document/setup development environment. A developer
can read *Dockerfile* and understand what is being done to setup the environment
and simply execute `docker build` command to generate his/her development
environment, or better you build the image and publish it in either public
registry and if that is not possible put it in a private registry, and ask
developers to pull a image of development environment.

Don't be scared by *private registry*, setting one up is not a humongous task!
Its just couple of docker commands and there is a pretty good `documentation
<https://docs.docker.com/registry/deploying/#run-a-local-registry>`_ available
to set one up.

While setting up a development environment you need to make sure last
instruction in your `Dockerfile` is executing the shell of your choice. This is
because when you start a container this last instruction is what actually is run
by docker, and in our case we need to provide developer with a shell all build
toolchain and libraries.

.. code-block:: Dockerfile

   ...
   CMD ["/bin/bash"]


Now developer just needs to get/build the image, start the container and use it
for their work!. To summarize below command is sufficient for developer to run a
fresh environment.

.. code-block:: shell

   $ docker build -t devenv . # If they are building it

   # If they are pulling it from say private registry
   $ docker pull private-registry-ip/path/to/devenv

   $ docker run -itd --name development devenv
   $ docker attach development

When container is started it will execute the shell and the next attach command
will attach your shell's input/output to container. Now it can be used just like
normal shell to build the application.

Another good thing which can be done is sharing the workspace with container so
your container can just contain the toolchain and library that is needed and all
version control, code editing and likewise can be done in the host machine. One
thing that would be needed to make sure is your UID on host and UID of the user
inside the container is same. This can be easily done by creating a separate
user in the container with UID same as your UID on host system.

Advantages
==========

Some advantages of using docker container include

1. They are easy to setup and saves a lot of time to the team as a whole
   compared to traditional approaches.
2. Easy to throwaway and start fresh: If a developer thinks he did something
   wrong with container he can prune it and create a fresh one based on the
   development environment image. So this gives a lot of freedom to developer to
   experiment.
3. Uniformity: You will be sure that all your team will be using same
   evnironment.

So you might ask what about other container technologies like systemd-nspawn or
lxc etc. Of course they can also be used in the similar fashion, infact before
experimenting with Docker I was a vivid user of *systemd-nspawn* container. You
might have also seen my previous `blog posts
<https://copyninja.info/tags/systemd-nspawn.html>`_ on *systemd-nspawn* too.
Only reason I switched to Docker is its easy to setup unlike systemd-nspawn
which needs so many tweaking and tuning of things besides it does not have a
Dockerfile like approach which makes things more time consuming. So for me
Docker won the war and I shifted to using Docker more.

This entire post was based on my experiment and experience with Docker. If you
feel something can be done in a better way please feel free to write to me.
