# Scripts are 'sourced' in order to set envvar 'zp' 
alias zg="source $ZETTELKASTEN_SOURCE/bin/_zg "
alias zm="source $ZETTELKASTEN_SOURCE/bin/_zm "

function zl() {
    source $ZETTELKASTEN_SOURCE/bin/_zl list_by_uid "$@"
}

function zt() { # for 'zettelkasten tasks'
    source $ZETTELKASTEN_SOURCE/bin/_zl list_by_header "$@"
}

########################################
# zn = 'zettelkasten new' 
#
# create a new filename  
#
# example usage: zn / foo bar
# example usage: zn 1-foo-bar.md TAG foo bar
########################################
function zn() {
    # setup 
    SCRIPT_DIR=`dirname "$0"`

    # determine filename and export result
    FILENAME=`python ${SCRIPT_DIR}/../library/zettelkasten.py generate_filename "$@" | tr -d '\n'`
    export zp=$FILENAME

    # write header 
    DATE=`date +%F`
    echo ">> ${DATE}" >> ${FILENAME}
    echo ">> :" >> ${FILENAME}
    echo "\n" >> ${FILENAME}

    nvim -c 'startinsert' + ${FILENAME}
}
