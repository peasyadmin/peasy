#!/bin/bash

Usage ()
{
  echo "\nUsage: sh make.sh [-c] [-m app] [-i app] [-u app] [-d app] [-t] [-h]";
  echo "    -c             - Cleans the project.";
  echo "    -l app         - Prepare application for Linux.";
  echo "    -w app         - Prepare application for Windows.";
  echo "    -i app         - Install (Linux).";
  echo "    -i app         - Uninstall (Linux).";
  echo "    -d app         - Create a debian package (Linux).";
  echo "    -t             - Create a tarball."
  echo "    -h             - Shows this help.\n";
}

Clean ()
{
  sudo rm -r build/
  find ./ -name "*~" -delete 
  find ./ -name "*.pyc" -delete
  find ./ -name "*.o" -delete
  find ./ -name "*.a" -delete
  find ./ -name "*.so" -delete
}

PrepareLinux ()
{
  mkdir -p build/Peasy
  cp -r Sources/Drivers build/Peasy
  cp -r Sources/Libraries build/Peasy
  cp -r Sources/thirdParty/all/beremiz build/Peasy
  cp -r Sources/thirdParty/linux/CanFestival-3 build/Peasy
  cp Sources/EsPeEs.py build/Peasy
  cp Sources/EsPeEs-Client.py build/Peasy
  cp Sources/EsPeEs-Server.py build/Peasy

  if [ "$arch" = "armv6l" ];
  then
    cp -r Sources/thirdParty/linux/Matiec-Raspbian build/Peasy
    mv build/Peasy/Matiec-Raspbian build/Peasy/matiec
  else
    cp -r Sources/thirdParty/linux/Matiec-Ubuntu build/Peasy
    mv build/Peasy/Matiec-Ubuntu build/Peasy/matiec
  fi

  cd build/Peasy

  # Build CanFestival-3
  cd CanFestival-3/
  if [ "$arch" = "armv6l" ];
  then
    ./configure --prefix=/usr --arch=armhf
  else
    ./configure --prefix=/usr
  fi
  make

  # Build matiec
  cd ../
  cd matiec
  autoreconf
  ./configure --prefix=/usr
  make
  cd ../
  python -m compileall .
  cd ../../
}

PrepareWindows ()
{
  echo
}

DebianPackage ()
{
  cp Files/Makefile build/Makefile
  cd build
  if [ "$arch" = "x86_64" ];
  then
    sudo checkinstall --install=no --maintainer "peasy@privatdemail.com" --pkgname "peasy" --pkgversion "0.1" --pkgrelease "1" --pkglicense "GPL" --pkggroup "Development" --requires "build-essential, bison, flex, autoconf, git-core, libtool, python-wxgtk2.8, python-wxtools, python-jsonpickle, python-numpy, checkinstall, pyro, python-pymodbus, python-pip, python-nevow, python-twisted, python-soappy, python-psutil, ncurses-dev, python-dev, python-wxglade, ia32-libs"
  else
    sudo checkinstall --install=no --maintainer "peasy@privatdemail.com" --pkgname "peasy" --pkgversion "0.1" --pkgrelease "1" --pkglicense "GPL" --pkggroup "Development" --requires "build-essential, bison, flex, autoconf, git-core, libtool, python-wxgtk2.8, python-wxtools, python-jsonpickle, python-numpy, checkinstall, pyro, python-pymodbus, python-pip, python-nevow, python-twisted, python-soappy, python-psutil, ncurses-dev, python-dev, python-wxglade"
  fi

  cd ..
}

InstallPeasy ()
{
  cp Sources/Files/linux/Makefile build/Makefile
  cd build
  sudo make install
  cd ..
}

UninstallPeasy ()
{
  cp Files/Makefile build/Makefile
  cd build
  sudo make uninstall
  cd ..
}

Tarball ()
{
  Clean
  cd ..
  tar -czf peasy_0.1_src.tar.gz peasy/
  mv peasy_0.1_src.tar.gz peasy/
  cd peasy/
}

arch=`uname -m`;

if [ $# -ge 3 ];
then
  echo "\nToo many parameters."
  Usage
  exit 1
fi

while true; do
  case "$1" in
    -l|--linux)
      shift;
      if [ -n "$1" ]; then
        case "$1" in
          Peasy)
             PrepareLinux
             exit
             ;;
          *)
             echo "\nDon't know package \"$1\"."
             Usage
             exit
             ;;
        esac
      else
        echo "\nNo package set."
        Usage
        exit
      fi
      ;;
    -w|--windows)
      shift;
      if [ -n "$1" ]; then
        case "$1" in
          Peasy)
             PrepareWindows
             exit
             ;;
          *)
             echo "\nDon't know package \"$1\"."
             Usage
             exit
             ;;
        esac
      else
        echo "\nNo package set."
        Usage
        exit
      fi
      ;;
    -i|--install)
      shift;
      if [ -n "$1" ]; then
        case "$1" in
          Peasy)
             InstallPeasy
             exit
             ;;
          *)
             echo "\nDon't know package \"$1\"."
             Usage
             exit
             ;;
        esac
      else
        echo "\nNo package set."
        Usage
        exit
      fi
      ;;
    -u|--uninstall)
      shift;
      if [ -n "$1" ]; then
        case "$1" in
          Peasy)
             UninstallPeasy
             exit
             ;;
          *)
             echo "\nDon't know package \"$1\"."
             Usage
             exit
             ;;
        esac
      else
        echo "\nNo package set."
        Usage
        exit
      fi
      ;;
    -d|--debian)
      shift;
      if [ -n "$1" ]; then
        case "$1" in
          Peasy)
             DebianPackage
             exit
             ;;
          *)
             echo "\nDon't know package \"$1\"."
             Usage
             exit
             ;;
        esac
      else
        echo "\nNo package set."
        Usage
        exit
      fi
      ;;
    -c|--clean)
      Clean
      exit
      ;;
    -t|--tarball)
      Tarball
      exit
      ;;
    -h|--help)
      Usage
      exit
      ;;
    *)
      echo "\nWrong parameters."
      Usage
      exit
      ;;
  esac
done
