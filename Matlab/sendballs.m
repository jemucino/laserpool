% Send ball information to physics module
% Depends on 'oscmsgout' from Pulsefield
function sendballs(balls);
  ok=oscmsgout('PHYSICS','/begin_balls',{});
  for i=1:size(balls,1)
    ok=oscmsgout('PHYSICS','/ball',{balls(i,1)/1000,balls(i,2)/1000});
  end
  ok=oscmsgout('PHYSICS','/end_balls',{});
  pause(2);
  fprintf('Sent ball messages\n');
end
