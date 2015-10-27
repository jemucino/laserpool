% Main loop for process data for pool++
% Overall system:
%   - LIDAR scans sent by Pulsefield program 'frontend' via OSC to this program
%   - this program receives scans, identifies balls, and send list to physics engine
%   - vision module uses camera input to identify cue position, if any, and sends to physics engine
%   - physics engine receives ball and cue locations, computes trajectory
% 	- send circles for balls, lines for trajectory to laser module
%   - laser module (from Pulsefield) receives OSC commands and draws using laser, built-in calibration
%	- note that laser module has y-origin along a long edge of table, x is in center
% Table dimensions were 2235.2 by 1121 mm.

doplot=true;
while true
  while true
    % Skip any old input
    x=oscmsgin('VIS',0.0,true);
    %fprintf('Flushing %d\n', length(x));
    for j=1:length(x)
      oscmsgin('VIS',0.0);	% oscmsgin() from Pulsefield
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
  [xt,yt]=transformdata(x);   % Transform from LIDAR position to pool table coords (in mm)
                              % Pool table has the origin in the center with x along long axis

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

  % Only keeps hits on the table (or nearby in case calibration is a little off)
  sel=abs(xt)<=L+50 & abs(yt)<=W+50;
  hits=[xt(sel);yt(sel)]';

  if doplot
  end

  % Compute positions of balls
  balls=findballs(hits);	% Process LIDAR scan to identify balls
  %displayballs(balls);		% Display balls (normally done by physics engine)
  sendballs(balls);		% Send balls to physics engine for processing
  if doplot & ~isempty(balls)
    hold on;
    plot(balls(:,1),balls(:,2),'ok');
    pause(0.1);
  end

end
