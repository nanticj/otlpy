if [ $# -eq 0 ]; then
    export PACKAGE=otlpy
else
    export PACKAGE=$1
fi

isort $PACKAGE
black $PACKAGE
mypy $PACKAGE
pylint $PACKAGE
