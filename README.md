# ros2doc
i can haz docs?

# installation
sudo apt install python3-sphinx python3-jinja2 python3-breathe

# running it

## to generate docs for all packages
. ~/ros2/install/setup.bash
./ros2doc.py ../src --all

## to generate docs just for a few specific packages:
. ~/ros2/install/setup.bash
./ros2doc.py ../src rmw rcl

# serving locally
sudo apt-get install lighttpd
sudo ln -s `pwd`/docbuild/latest/html /var/www/html/latest
