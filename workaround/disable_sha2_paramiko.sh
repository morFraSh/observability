#! /bin/bash
MODE=$1
PATH_PKG_PYTHON=$(python -m pip show paramiko | sed -r -n "s/[Ll]ocation\: (.*)/\1/p")/paramiko/transport.py
CHECK_DISABLE=$(grep -c "disabled_algorithms=None" $PATH_PKG_PYTHON)

if [[ $MODE =~ "isable" ]]; then
   if [ $CHECK_DISABLE -eq 1 ]; then
      sed -i "s/disabled_algorithms=None/disabled_algorithms={'pubkeys': \['rsa-sha2-256', 'rsa-sha2-512'\]}/g" $PATH_PKG_PYTHON
   fi
   echo 'Disable SHA2 in paramiko (py venv)'
else 
   if [[ $MODE =~ "nable" ]]; then
      sed -i "s/disabled_algorithms={'pubkeys': \['rsa-sha2-256', 'rsa-sha2-512'\]}/disabled_algorithms=None/g" $PATH_PKG_PYTHON
      echo 'Enable SHA2 in paramiko (py venv)'
   fi
fi
