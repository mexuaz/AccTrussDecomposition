#!/bin/bash

MAINDIR="AccTrussDecomposition"

ALLAPPS=("opt-truss-decomp" "opt-truss-decomp-offload" "opt-offload-large-data" "opt-cpu-large-data" "opt-cpu-large-data" "msp" "h-idx")

BUILDDIR="build-acc"

CMAKEOPT="-DBUILD_SERIAL=ON -DPLAYGROUND=OFF -DLEGACY_PKT_ALL=ON"

cd $HOME

if [[ -d "$MAINDIR" ]]; then
	echo ">>> Syncing repository ..."
	cd "$MAINDIR"
	git reset --hard
	git pull
	cd ..
else
	echo ">>> Cloning repository ..."
	git clone git@github.com:mexuaz/$MAINDIR
fi
echo "<<<"

if [[ -d "$BUILDDIR" ]]; then
    echo ">>> Removing old build directory."
    rm -rf "$BUILDDIR"
    echo "<<<"
fi

echo ">>> Creating new build directory."
mkdir "$BUILDDIR"
cd "$BUILDDIR"
echo "<<<"

echo ">>> Reloading ComputeCanada essential modules ..."
module --force purge
module load nixpkgs gcc/8.3.0 cuda/10.1 cudnn/7.6.5 tbb/2018_U5 cmake/3.16.3 python/3.8.2 boost/1.68.0 openmpi/4.0.1
module list
echo "<<<"

echo ">>> Building all projects ..."

for PRG in ${ALLAPPS[*]}; do
  echo ">> Building $PRG"
  mkdir "$PRG"
  cd "$PRG"
  cmake "$HOME/$MAINDIR/$PRG" "$CMAKEOPT"
  make -j
  echo "<<"
done

echo "<<<"



