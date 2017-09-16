#!/bin/bash

COLOR_RED='\033[0;31m';
COLOR_GREEN='\033[0;32m';
COLOR_YELLOW='\033[0;33m';
COLOR_BLUE='\033[1;96m';
COLOR_WHITE='\033[1;97m';
COLOR_WHITE_UNDERLINED='\033[4;37m';
COLOR_RESET='\033[0m';

ERROR="false";

REMOTE_SERVER_IP=192.168.1.235;
REMOTE_SERVER_PORT=8000;

IMAGE_WIDTH=320;
IMAGE_HEIGHT=240; 


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
            REMOTE_SERVER_IP="$2"
            shift # past argument
          fi
        ;;
        --port)
          if [ "$2" = "" ]; then
            ERROR="true";
          else
            REMOTE_SERVER_PORT="$2"
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
    echo -e "${COLOR_BLUE}Starts Raspberry Pi clients (VLC client, OpenCV, Tensorflow...)${COLOR_RESET}"
    echo -e ""
    echo -e "Usage: ./start_raspberry.sh [options]"
    echo -e "Example: ${COLOR_WHITE}./start_raspberry.sh --ip 192.168.1.235 --port 8000  ${COLOR_RESET}"
    echo -e ""
    echo -e "Options: ${COLOR_WHITE_UNDERLINED}[options]${COLOR_RESET}"
    echo -e "        ${COLOR_WHITE}--ip [IP]${COLOR_RESET} - Public remote server IP (default $REMOTE_SERVER_IP)"
    echo -e "        ${COLOR_WHITE}--port [PORT]${COLOR_RESET} - Public remote server PORT (default $REMOTE_SERVER_PORT)"
    echo -e "        ${COLOR_WHITE}--help${COLOR_RESET} - This help"
    echo -e ""
    echo -e ""
    exit;
fi

# Starting VLC server
printf "${COLOR_BLUE}>> START RASPBERRY PI -------------------------------------------------------------------${COLOR_RESET}\n\n";
printf "${COLOR_GREEN}>> Sending images to $REMOTE_SERVER_IP:$REMOTE_SERVER_PORT ${COLOR_RESET}\n";

raspivid -w $IMAGE_WIDTH -h $IMAGE_HEIGHT -t 0 -o - | nc $REMOTE_SERVER_IP $REMOTE_SERVER_PORT 



