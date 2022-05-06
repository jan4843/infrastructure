#!/bin/sh -e

export GIT_DIR="$HOME/.local/src/dotfiles.git"
export GIT_WORK_TREE="$HOME"

if [ -d "$GIT_DIR" ]; then
    echo "dotfiles already installed"
    exit
fi

git clone --bare "$1" "$GIT_DIR"
git config status.showUntrackedFiles no
git checkout --force
git submodule update --init --recursive
