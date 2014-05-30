./bin/bzrflag --world=maps/simple.bzw --default-tanks=1 --default-posnoise=5 --red-port=50100 --green-port=50101 --purple-port=50102 --blue-port=50103 $@ &
sleep 2
python bzagents/stand_still_pigeon.py localhost 50100 &
python bzagents/straight_line_pigeon.py localhost 50101 &
python bzagents/non_conforming_pigeon.py localhost 50102 &
python bzagents/shooter_agent.py localhost 50103 &

