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


########################################
# zg = 'zettelkasten grep' 
#
# search file contents 
#
# example usage: zg
########################################
function zg() {
    [[ -n $1 ]] && cd $1 # go to provided folder or noop
    RG_DEFAULT_COMMAND="rg -i -l --hidden --no-ignore-vcs"

    selected=$(
    FZF_DEFAULT_COMMAND="rg --files" fzf \
    -m \
    -e \
    --ansi \
    --disabled \
    --bind "ctrl-a:select-all" \
    --bind "f12:execute-silent:(subl -b {})" \
    --bind "change:reload:$RG_DEFAULT_COMMAND {q} || true" \
    --preview "rg -i --pretty --context 2 {q} {}" | cut -d":" -f1,2
    )

    # export result
    export zp=$selected 
}


########################################
# zm = 'zettelkasten move' 
#
# move a file and update all references to it 
#
# example usage: zm 1a-foo.md  2-bar.md 
########################################
function zm() {
    # configuration
    suffix=".md"

    # preliminary checks
    if [ $# -ne 2 ]; then
    echo "Usage: OLD_FILENAME NEW_FILENAME"
    return 0
    fi

    if [[ ! "${1}" == *"$suffix" || ! "${2}" == *"$suffix" ]]; then
    echo "Usage: expect to operate on $suffix files" 
    return 0
    fi
    
    # setup
    OLD_FILENAME=${1}
    NEW_FILENAME=${2}

    # final checks
    if [[ ! -f ${OLD_FILENAME} ]]
    then
        echo "${OLD_FILENAME}: No such file"
        return 0
    fi

    # change references and move file
    grep -rl "${OLD_FILENAME}" ${PWD} | xargs sed -i ".bak" "s/${OLD_FILENAME}/${NEW_FILENAME}/g"
    mv ${OLD_FILENAME} ${NEW_FILENAME}

    # archive backups 
    BACKUP_DIR="/tmp/backup_${PWD##*/}-`date +"%F-%T"`"
    mkdir ${BACKUP_DIR}
    (mv *bak ${BACKUP_DIR}) 2>/dev/null

    # print and export new filename
    echo ${NEW_FILENAME}  
    export zp=$NEW_FILENAME
}
