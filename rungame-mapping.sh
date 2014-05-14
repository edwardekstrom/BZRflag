./bin/bzrflag --world=maps/four_ls.bzw --default-true-positive=.97 --default-true-negative=.9 --occgrid-width=100 --no-report-obstacles --red-port=50100 --green-port=50101 --purple-port=50102 --blue-port=50103 $@ &
#./bin/bzrflag --world=maps/rotated_box_world.bzw --default-true-positive=.97 --default-true-negative=.9 --occgrid-width=100 --no-report-obstacles --red-port=50100 --green-port=50101 --purple-port=50102 --blue-port=50103 $@ &
sleep 3
#python bzagents/agent0.py localhost 50100 &
#python bzagents/agent0.py localhost 50101 &
#python bzagents/agent0.py localhost 50102 &
python bzagents/mapping_agent.py localhost 50103 &

