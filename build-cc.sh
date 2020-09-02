#!/bin/bash

MAINDIR="AccTrussDecomposition"

ALLAPPS=( "opt-truss-decomp" )
ALLAPPS+=( "opt-truss-decomp-offload" ) # cuda problems with this project
ALLAPPS+=( "opt-offload-large-data" )
ALLAPPS+=( "opt-cpu-large-data" )
ALLAPPS+=( "opt-cpu-large-data" )
ALLAPPS+=( "msp" )
ALLAPPS+=( "h-idx") # C++ problems with this projects

BUILDDIR="build-acc"

CMAKEOPT="-DBUILD_SERIAL=ON -DPLAYGROUND=OFF -DLEGACY_PKT_ALL=ON"

cd $HOME

if [[ -d "$MAINDIR" ]]; then
	echo ">>> Repository Syncing ..."
	cd "$MAINDIR"
	git reset --hard
	git pull
	cd ..
else
	echo ">>> Repository Cloning ..."
	git clone git@github.com:mexuaz/$MAINDIR
fi
echo "<<< Repository."

if [[ -d "$BUILDDIR" ]]; then
    echo ">>> Removing old build directory."
    rm -rf "$BUILDDIR"
    echo "<<< Old build directory."
fi

echo ">>> Creating new build directory."
mkdir "$BUILDDIR"
cd "$BUILDDIR"
echo "<<< New build directory."

echo ">>> Reloading ComputeCanada essential modules ..."
module --force purge
module load nixpkgs gcc/8.3.0 cuda/10.1 cudnn/7.6.5 tbb/2018_U5 cmake/3.16.3 python/3.8.2 boost/1.68.0 openmpi/4.0.1
module list
echo "<<< Essential Modules."

echo ">>> Building all projects ..."

for PRG in ${ALLAPPS[*]}; do
  echo ">> Building $PRG"
  mkdir "$PRG"
  cd "$PRG"
  cmake "$HOME/$MAINDIR/$PRG" "$CMAKEOPT"
  make -j
  echo "<< Building $PRG"
done

echo "<<< Build All projects."



