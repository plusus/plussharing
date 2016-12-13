#!/bin/bash -e

PACKAGE_NAME=plussharing
VERSION_MAJOR=1
VERSION_MINOR=0
VERSION_BUILD=1
VERSION="$VERSION_MAJOR.$VERSION_MINOR-$VERSION_BUILD"
SEP="_"
PACKAGE_NAME_VERSION=$PACKAGE_NAME$SEP$VERSION
ARCHITECTURE=amd64
PACKAGE_DIR=builddeb/$PACKAGE_NAME_VERSION

echo '### COPYING FILES'
rm -rf $PACKAGE_DIR/*
mkdir -p $PACKAGE_DIR
rsync -a package/ builddeb/$PACKAGE_NAME_VERSION/

echo '### CREATING DEBIAN FOLDER'
mkdir -p builddeb/$PACKAGE_NAME_VERSION/DEBIAN
# Copy base files
rsync -a debian/ builddeb/$PACKAGE_NAME_VERSION/DEBIAN/

cd builddeb/$PACKAGE_NAME_VERSION

# Generate control file
CONTROL_FILE="DEBIAN/control"
touch DEBIAN/control
echo "Package: ${PACKAGE_NAME}" > "$CONTROL_FILE"
echo "Version: $VERSION" >> "$CONTROL_FILE"
echo "Section: misc" >> "$CONTROL_FILE"
echo "Priority: optional" >> "$CONTROL_FILE"
echo "Architecture: $ARCHITECTURE" >> "$CONTROL_FILE"
echo "Essential: no" >> "$CONTROL_FILE"
echo "Installed-Size: `du -sc usr | grep total | awk '{ print $1 }'`" >> "$CONTROL_FILE"
echo "Maintainer: Samuel Charland <samuel.charland@usherbrooke.ca>" >> "$CONTROL_FILE"
echo "Homepage: http://plus-us.gel.usherbrooke.ca/plussharing" >> "$CONTROL_FILE"
echo "Depends: python-nautilus (>= 1.1), libc6 (>= 2.19), libssl1.0.0, libffi6 (>= 3.1), python3-pyasn1 (>= 0.1.7), python3-pyasn1-modules (>= 0.0.5), python3-six (>= 1.8.0), python3-pycparser (>= 2.10), python3-pyside (>= 1.2.2), python3-mysql.connector (>= 1.2.3), python3-apt (>= 0.9.3.12), python3-pkg-resources (>= 20.10.1), python3-idna (>= 2.0)" >> "$CONTROL_FILE"
echo "Provides: python3-cffi, python3-cryptography, python3-paramiko, python3-pysftp" >> "$CONTROL_FILE"
echo "Conflicts: python3-cffi, python3-cryptography, python3-paramiko, python3-pysftp" >> "$CONTROL_FILE"
echo "Description: Nautilus extension for file sharing in the PLUS distribution" >> "$CONTROL_FILE"
echo " Allows to share publicly and privately files among users of the PLUS distribution through Nautilus." >> "$CONTROL_FILE"

# Create md5sum
find . -type f ! -regex '.*.hg.*' ! -regex '.*?debian-binary.*' ! -regex '.*?DEBIAN.*' -printf '"%P" ' | xargs md5sum > DEBIAN/md5sums

cd ..

dpkg-deb -bv $PACKAGE_NAME_VERSION $PACKAGE_NAME_VERSION"_"$ARCHITECTURE".deb"
