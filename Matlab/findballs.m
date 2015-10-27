function balls=findballs(hits)
  balldiam=52;
  thresh=balldiam*0.8;
  thresh2=balldiam*1.1;
  balllist={};
  for i=1:size(hits,1)
    if isempty(balllist) || mag(hits(i,:)-balllist{end}(end,:)) > thresh || mag(hits(i,:)-balllist{end}(1,:)) > thresh2
      balllist{end+1}=[];
    end
    balllist{end}(end+1,:)=hits(i,:);
  end
  fprintf('Have %d balls\n', length(balllist));
  balls=[];
  for i=1:length(balllist)
    balls(i,:)=mean(balllist{i},1);
  end
end


function m=mag(x)
  m=sqrt(sum(x.^2));
end
