#!/bin/bash

set -e -o pipefail

# gets the aliases
shopt -s expand_aliases
source /root/.profile 2>&1 > /dev/null

# Disable coredump generation
sysctl -w 'kernel.core_pattern=core'

# Reset
COLOR_RESET='\e[0m'     # Text Reset

# Regular Colors
RED='\e[0;31m'
GREEN='\e[0;32m'
YELLOW='\e[0;33m'

mmcroot=/dev/mmcblk2p2
rootfs_in_use=0

function fast_blink {
	while true; do
		user_led_off
		sleep 0.1
		user_led_on
		sleep 0.1
	done
}

function slow_blink {
	while true; do
		user_led_off
		sleep 1
		user_led_on
		sleep 1
	done
}

# Kill last running jobs
function cleanup {
	jobs=$(jobs -p)
	kill $(echo $jobs)
	wait $(echo $jobs)
}

# Copies the wireguard configuration from an usb stick, if any
function stick_conf {
	if [ ! -e /dev/sda1 ]; then
		echo -e "${YELLOW}No USB stick detected${COLOR_RESET}"
		return
	fi

	echo -e "${GREEN}USB stick detected. Getting wireguard configuration${COLOR_RESET}"

	set -x

	mkdir -p /tmp/usb
	mount /dev/sda1 /tmp/usb

	conf=$(ls /tmp/usb/*.conf | head -n 1 )
	if [ "${conf}" != "" ]; then
		echo -e "${GREEN}Copying ${conf} wireguard configuration from USB Stick${COLOR_RESET}"
		mkdir -p /tmp/mmc
		mount ${mmcroot} /tmp/mmc
		cp ${conf} /tmp/wg0.conf
		sed -i '/^Address[[:blank:]]/a\Table = off' /tmp/wg0.conf
		dos2unix /tmp/wg0.conf
		mv /tmp/wg0.conf /tmp/mmc/etc/wireguard
		sync
		umount /tmp/mmc
		rmdir /tmp/mmc

		umount /tmp/usb
		rmdir /tmp/usb
		echo -e "${GREEN}REMOVE THE USB STICK AND POWER_CYCLE THE BOARD${COLOR_RESET}"
		slow_blink
		# NOT REACHED
	else
		echo -e "${RED} Error, no conf file on stick${COLOR_RESET}"
	fi

	umount /tmp/usb
	rmdir /tmp/usb
}


set -- $(cat /proc/cmdline)
for x in "$@"; do
	case "$x" in
	root=*)
		if [ "${x#root=}" == "${mmcroot}" ]; then
			echo -e "${GREEN}MMC BOOT detected -> Production mode!${COLOR_RESET}"
			rootfs_in_use=1
		fi
		;;
	esac
done

# Condition to flash is that this is a SD boot,
# and that the jumper is not set

flash=$(read_flash_gpio)
if [ "${flash}" -eq 0 ]; then
	echo -e "${YELLOW}Interrupted start through GPIO jumper${COLOR_RESET}"
	exit 0
fi

if [ "${rootfs_in_use}" -eq 0 ]; then

	trap cleanup exit

	echo -e "${GREEN}Flashing the eMMC!${COLOR_RESET}"

	fast_blink &
	/sbin/mmc_flash.sh

	stick_conf

	echo "COMPLETE! Please remove the SD card and reboot"

	user_led_on
	exit 0
fi

set +x

stick_conf

user_led_on
if [ "$?" -eq 0 ]; then
    echo -e "${GREEN}OK!${COLOR_RESET}"
else
    echo -e "${RED}FAIL!${COLOR_RESET}"
fi
