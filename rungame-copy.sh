./bin/bzrflag --world=maps/four_ls.bzw  --red-port=50100 --green-port=50101 --purple-port=50102 --blue-port=50103 $@ &
sleep 2
python bzagents/agent1_spencer.py localhost 50100 &
#python bzagents/agent1_spencer.py localhost 50101 &
#python bzagents/agent1_spencer.py localhost 50102 &
#python bzagents/agent1_spencer.py localhost 50103 &

