minx=-1.175
maxx=1.175
miny=0.0
maxy=1.143
pts=[0 0
     -1 -1
     0 -1
     0 0
     1 -1
     1 1
     0 0
     0 1
     -1 1
     0 0];
pts(:,1)=(pts(:,1)+1)/2*(maxx-minx)+minx;
pts(:,2)=(pts(:,2)+1)/2*(maxy-miny)+miny;
ok=oscmsgout('LASER','/laser/bg/begin',{});
ok=oscmsgout('LASER','/laser/set/color',{0.0,1.0,0.0});
for i=1:size(pts,1)-1
  ok=oscmsgout('LASER','/laser/line',{pts(i,1),pts(i,2),pts(i+1,1),pts(i+1,2)});
end
ok=oscmsgout('LASER','/laser/bg/end',{});
