Forwarding host port to service in container
############################################

:date: 2015-11-09 17:06
:slug: port_forward_container
:tags: iptables, firewall, container
:author: copyninja
:summary: Brief notes on forwarding specific ports to service running
	  in container.

Problem
-------

I've lxc container running distcc daemon and I would like to forward
the distcc traffic coming to my host system to container.

Solution
--------

Following simple script which uses iptable did the job.

.. code-block:: shell

   #!/bin/sh
   set -e


  usage() {
      cat <<EOF
      $(basename $0) [options] <in-interface> <out-interface> <port> <destination>

      --clear           Clear the previous rules before inserting new
                        ones

      --protocol        Protocol for the rules to use.

      in-interface      Interface on which incoming traffic is expected
      out-interface     Interface to which incoming traffic is to be
                        forwarded.

      port              Port to be forwarded. Can be integer or string
                        from /etc/services.
      destination       IP and port of the destination system to which
                        traffic needs to be forwarded. This should be in
                        form <destination_ip:port>

  (C) 2015 Vasudev Kamath - This program comes with ABSOLUTELY NO
  WARRANTY. This is free software, and you are welcome to redistribute
  it under the GNU GPL Version 3 (or later) License

  EOF
  }

  setup_portforwarding () {
      local protocol="$1"
      iptables -t nat -A PREROUTING -i $IN_INTERFACE -p "$protocol" --dport $PORT \
   	     -j DNAT --to $DESTINATION
      iptables -A FORWARD -p "$protocol" -d ${DESTINATION%%\:*} --dport $PORT -j ACCEPT

      # Returning packet should have gateway IP
      iptables -t nat -A POSTROUTING -s ${DESTINATION%%\:*} -o \
   	     $IN_INTERFACE -j SNAT --to ${IN_IP%%\/*}

  }

  if [ $(id -u) -ne 0 ]; then
      echo "You need to be root to run this script"
      exit 1
  fi

  while true; do
      case "$1" in
   	--clear)
   	    CLEAR_RULES=1
   	    shift
   	    ;;
   	--protocol|--protocol=*?)
   	if [ "$1" = "--protocol" -a -n "$2" ];then
   	    PROTOCOL="$2"
   	    shift 2
   	elif [ "${1#--protocol=}" != "$1" ]; then
   	    PROTOCOL="${1$--protocol=}"
   	    shift 1
   	else
   	    echo "You need to specify protocl (tcp|udp)"
   	    exit 2
   	fi
   	;;

   	*)
   	    break
   	    ;;
      esac
  done

  if [ $# -ne 4 ]; then
      usage $0
      exit 2
  fi

  IN_INTERFACE="$1"
  OUT_INTERFACE="$2"
  PORT="$3"
  DESTINATION="$4"

  # Get the incoming interface IP. This is used for SNAT.
  IN_IP=$(ip addr show $IN_INTERFACE|\
   	       perl -nE '/inet\s(.*)\sbrd/ and print $1')


  if [ -n "$CLEAR_RULES" ]; then
      iptables -t nat -X
      iptables -t nat -F
      iptables -F
  fi

  if [ -n "$PROTOCOL" ]; then
      setup_portforwarding $PROTOCOL
  else
      setup_portforwarding tcp
      setup_portforwarding udp
  fi


Coming to systemd-nspawn I see there is *--port* option which takes
argument in form *proto:hostport:destport* where proto can be either
*tcp* or *udp*, *hostport* and *destport* are number from
1-65535. This option assumes private networking enabled in the
container. I've not tried this option yet but that simplifies quite a
lot of thing, its like -p switch used by *docker*.
