./bin/bzrflag --world=maps/four_ls.bzw --default-tanks=4 --friendly-fire --occgrid-width=100 --default-true-positive=.97 --default-true-negative=.9 --red-port=50100 --green-port=50101 --purple-port=50102 --blue-port=50103 $@ &
#./bin/bzrflag --world=maps/rotated_box_world.bzw --red-port=50100 --green-port=50101 --purple-port=50102 --blue-port=50103 $@ &
sleep 2
python bzagents/mapping_agent.py localhost 50100 &