#!/bin/bash

COLOR_RED='\033[0;31m';
COLOR_GREEN='\033[0;32m';
COLOR_YELLOW='\033[0;33m';
COLOR_BLUE='\033[1;96m';
COLOR_WHITE='\033[1;97m';
COLOR_WHITE_UNDERLINED='\033[4;37m';
COLOR_RESET='\033[0m';

ERROR="false";

SERVERIP=192.168.1.235;
SERVERPORT=8000;

# Use -gt 1 to consume two arguments per pass in the loop (e.g. each
# argument has a corresponding value to go with it).
# Use -gt 0 to consume one or more arguments per pass in the loop (e.g.
# some arguments don't have a corresponding value to go with it such
# as in the --default example).
# note: if this is set to -gt 0 the /etc/hosts part is not recognized ( may be a bug )
while [[ $# -gt 0 ]]
  do
    key="$1"

    case $key in

        --ip)
          if [ "$2" = "" ]; then
            ERROR="true";
          else
            SERVERIP="$2"
            shift # past argument
          fi
        ;;
        --port)
          if [ "$2" = "" ]; then
            ERROR="true";
          else
            SERVERPORT="$2"
            shift # past argument
          fi
        ;;

        -h|--help)
          ERROR="true";
        ;;

       
        *)
                # unknown option
        ;;
    esac
  shift # past argument or value
done

clear;


if [ "$ERROR" = "true" ]; then
    echo -e ""
    echo -e "${COLOR_BLUE}Starts VLC server in this computer, listening to video sent by Raspberry Pi camera${COLOR_RESET}"
    echo -e ""
    echo -e "Usage: ./start_computer.sh [options]"
    echo -e "Example: ${COLOR_WHITE}./start_computer.sh --ip 192.168.1.235 --port 8000  ${COLOR_RESET}"
    echo -e ""
    echo -e "Options: ${COLOR_WHITE_UNDERLINED}[options]${COLOR_RESET}"
    echo -e "        ${COLOR_WHITE}--ip [IP]${COLOR_RESET} - Public mplayer server IP (default $SERVERIP) for this computer"
    echo -e "        ${COLOR_WHITE}--port [PORT]${COLOR_RESET} - Public mplayer server PORT (default $SERVERPORT) for this computer. Must be opened in firewall"
    echo -e "        ${COLOR_WHITE}--help${COLOR_RESET} - This help"
    echo -e ""
    echo -e ""
    exit;
fi

# Starting VLC server
printf "${COLOR_BLUE}>> START CONTROL COMPUTER -------------------------------------------------------------------${COLOR_RESET}\n\n";
printf "${COLOR_GREEN}>> Starting video server $SERVERIP:$SERVERPORT ${COLOR_RESET}\n";

nc -l -p $SERVERPORT | mplayer -fps 60 -cache 1024 -

