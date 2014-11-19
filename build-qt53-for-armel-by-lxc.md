# Build Qt5.3 for armel with LXC

## prerequisite

```
sudo apt-get install lxc qemu-user-static
```

## LXC rootfs

Create armel LXC rootfs

```
sudo lxc-create -t ubuntu -n p5 -- -r precise -a armel
sudo lxc-start -dn p5
ssh ubuntu@`sudo lxc-info -i -n p5|grep -o '[0-9.]*'`
password: ubuntu
```

Install necessary libraries

```
sudo apt-get update
# 12.04 only
sudo apt-get install bash build-essential git-core subversion git-svn apache2 php5 python libx11-dev libfontconfig1-dev ruby flex gperf bison libxslt1-dev libsqlite3-dev libxext-dev libssl-dev libxrender-dev libicu-dev libxv-dev libxrandr-dev libgl1-mesa-dev libglu1-mesa-dev libdbus-1-dev bluez libbluetooth-dev gstreamer0.10-plugins-base gstreamer0.10-ffmpeg gstreamer0.10-plugins-good libgstreamer-plugins-base0.10-dev libgl1-mesa-dev libglu1-mesa-dev libdbus-1-dev libxcb-icccm4-dev libxcb-xfixes0-dev libxcb-image0-dev libxcb-keysyms1-dev libxcb-sync0-dev libx11-xcb-dev xvfb libgtk2.0-dev libxcb-randr0-dev libjpeg-dev libpng-dev
sudo apt-get install "^libxcb.*" libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev
sudo apt-get install flex bison gperf libicu-dev libxslt-dev ruby libssl-dev libxcursor-dev libxcomposite-dev libxdamage-dev libxrandr-dev libfontconfig1-dev libasound2-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev
```

get qt code and build

```
git clone git://gitorious.org/qt/qt5.git qt53-src
cd qt53-src
git checkout -b v5.3.2 v5.3.2
perl init-repository
#perl init-repository -f
./configure -developer-build -opensource -nomake examples -nomake tests
make -j4
# http://qt-project.org/forums/viewthread/22427/P15
#    virtual ListWidgetEditor::~ListWidgetEditor();
#    virtual TreeWidgetEditorDialog::~TreeWidgetEditorDialog();
#    virtual TableWidgetEditorDialog::~TableWidgetEditorDialog();
```

## tarball

On host, 

```
sudo tar xvf qt53-all.tar
sudo mv var/lib/lxc/p5 /var/lib/lxc/
cat <<EOF | sudo tee /var/lib/lxc/p5/fstab
/home/$USER/ mnt none bind 0 0        
EOF
sudo lxc-start -dn p5
ssh ubuntu@`sudo lxc-info -i -n p5|grep -o '[0-9.]*'`
cd /mnt/<folder_to_appchooser>
../qt53-src/qtbase/bin/qmake -spec ../qt53-src/qtbase/mkspecs/linux-g++ -unix -o Makefile appchooser.pro
make
```

On target,

```
mkdir -p /home/linaro/qt53
cp qt53-src/qtbase/lib /home/linaro/qt53/
cp -a qt53-src/qtbase/plugins/platforms /home/linaro/qt53/
cp appchooser /home/linaro/qt53/
cat <<EOF | sudo tee /etc/ld.so.conf.d/qt.conf
/home/linaro/qt53/lib
EOF
sudo ldconfig
DISPLAY=:0 /home/linaro/appchooser
```

### NOTE

On target, there are necessary libraries to install before running qt application,

```
sudo apt-get install libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
                     libxcb-render-util0 libxcb-render0 libxcb-shape0 libxcb-shm0 \
                     libxcb-sync0 libxcb-util0 libxcb-xfixes0 libxcb1
```

For more information, http://qt-project.org/doc/qt-5/linux-requirements.html
