# Scripts are 'sourced' in order to set envvar 'zp' 
alias zg="source $ZETTELKASTEN_SOURCE/bin/_zg "
alias zm="source $ZETTELKASTEN_SOURCE/bin/_zm "
alias zn="source $ZETTELKASTEN_SOURCE/bin/_zn "

function zl() {
    source $ZETTELKASTEN_SOURCE/bin/_zl list_by_uid "$@"
}

function zs() { # for 'zettelkasten subset' - generally run after 'zl'
    prefix=`echo $zp | cut -d "-" -f 1`
    source $ZETTELKASTEN_SOURCE/bin/_zl list_by_uid $prefix
}

function zt() { # for 'zettelkasten tasks'
    source $ZETTELKASTEN_SOURCE/bin/_zl list_by_priority "$@"
}
