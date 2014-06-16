#./bin/bzrflag --world=maps/rotated_box_world.bzw \
#./bin/bzrflag --world=maps/final1.bzw \
#./bin/bzrflag --world=maps/final2.bzw \
#./bin/bzrflag --world=maps/test.bzw \
./bin/bzrflag --world=maps/four_ls.bzw \
--friendly-fire \
--time-limit=240 \
--respawn-time=240 \
--max-shots=3 \
--default-tanks=10 \
--default-posnoise=3 \
--default-true-positive=.97 \
--default-true-negative=.9 \
--occgrid-width=100 \
--no-report-obstacles \
--red-port=50100 \
--green-port=50101 \
--purple-port=50102 \
--blue-port=50103 $@ &
# --green-tanks=0 \
# --purple-tanks=0 \
# --blue-tanks=1 \

#General:

#--friendly-fire         You will be safe from friendly fire
#--time-limit=240        Life is short!
#--respawn-time=240      Sorry, you will not be coming back in this life
#--max-shots=3           Three shots at a time
#--default-tanks=10      Have fun!

#Less noise than the Kalman lab:

#--default-posnoise=3

#These are just like in the grid lab:

#--default-true-positive=.97
#--default-true-negative=.9
#--occgrid-width=100
#--no-report-obstacles

sleep 2
python bzagents/final_agent.py localhost 50100 & # red
python bzagents/final_agent.py localhost 50101 & # green
python bzagents/final_agent.py localhost 50102 & # purple
python bzagents/final_agent.py localhost 50103 & # blue

