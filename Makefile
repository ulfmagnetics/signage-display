# Makefile for signage-display

TARGET_DIR = /Volumes/CIRCUITPY
LIBRARY_DIR = `python3 -c "import signage_air_quality as _; print(_.__path__[0])"`

install : ensure
	cp -r ${LIBRARY_DIR} ${TARGET_DIR}/lib
	cp code.py ${TARGET_DIR}

ensure :
	if ! [[ -d ${TARGET_DIR} ]]; then echo "${TARGET_DIR} must be mounted" && exit 1; fi
