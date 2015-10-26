# Draw a pattern
r=0.0
g=0.9
b=1.0
minx=-1.175
maxx=1.175
miny=0.0
maxy=1.143
PATH=${PATH}:../../bin
replayOSC -h 127.0.0.1 7780 <<EOF
/laser/bg/begin
/laser/set/color 0.0 1.0 0.0
/laser/line $minx $miny $minx $maxy
/laser/line $minx $maxy $maxx $maxy
/laser/line $maxx $maxy $maxx $miny
/laser/line $maxx $miny $minx $miny
/laser/bg/end
EOF

