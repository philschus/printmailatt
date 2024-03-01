#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

python3 $SCRIPTPATH/printmailatt.py default.cfg | tee -a $SCRIPTPATH/output.log
