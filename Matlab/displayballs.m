function displayballs(balls)
  ok=oscmsgout('LASER','/laser/bg/begin',{});
  ok=oscmsgout('LASER','/laser/set/color',{0.0,1.0,0.0});
  for i=1:size(balls,1)
    %fprintf('circle(%.3f,%.3f,%.3f)\n',balls(i,1)/1000,balls(i,2)/1000,.052);
    ok=oscmsgout('LASER','/laser/circle',{balls(i,1)/1000,balls(i,2)/1000+1.14/2,.052});
  end
  ok=oscmsgout('LASER','/laser/bg/end',{});
end
