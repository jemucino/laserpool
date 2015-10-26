r
doplot=true;
physicshost='192.168.0.206';
physicsport=5006;
while true
  while true
    % Skip any old input
    x=oscmsgin('VIS',0.0,true);
    %fprintf('Flushing %d\n', length(x));
    for j=1:length(x)
      oscmsgin('VIS',0.0);
    end
    
    x=oscmsgin('VIS',1);
    if isempty(x)
      fprintf('No messages from server!\n');
      pause(2);
    elseif strcmp(x.path,'/vis/range')
      break;
    else
      %fprintf('.');
    end
  end
  %fprintf('\n');
  [xt,yt]=transformdata(x);

  if doplot
    figure(1);clf;
    plot(xt,yt,'.')
    hold on
    L=2235.2/2; %half length
    W=1121/2; %half width
    tableborderx=[L,L,-L,-L,L];
    tablebordery=[W,-W,-W,W,W];

    
    plot(tableborderx, tablebordery,'g')
    axis(2*[-L,L,-W,W]);
  end

  % Only keeps hits on the table
  sel=abs(xt)<=L+50 & abs(yt)<=W+50;
  hits=[xt(sel);yt(sel)]';

  if doplot
  end

  % Compute positions of balls
  balls=findballs(hits);
  %displayballs(balls);
  sendballs(balls);
  if doplot & ~isempty(balls)
    hold on;
    plot(balls(:,1),balls(:,2),'ok');
    pause(0.1);
  end

end
