FOLLOW THESE STEPS

1. Copy folder (or use hg clone) to /some/folder/evap on your system
2. Append these two lines to your .bashrc:

export PATH="${PATH}:/some/folder/evap"
export PYTHONPATH="${PYTHONPATH}:/some/folder/evap"

3. Source your .bashrc
4. Test via $ evaporate --help

