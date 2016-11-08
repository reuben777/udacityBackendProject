# udacityBackendProject
Getting started

Start up Vagrant:
using - cd /Documents/{where the project vagrant file is}
vagrant up
vagrant ssh
cd /vagrant 
cd tournament

# initialize DB
// do this before testing!
psql \c tournament
\i tournament.sql

then exit 
\q

now you can run:
python tournament_test.py 
