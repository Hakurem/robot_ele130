%% har laget denne funksjonen til parsing av data fra python til matlab
function [d] = SortData(filename)
    file = strcat( '../Data/',filename);
    opts = detectImportOptions(file);
    opts.VariableNamesLine = 1;
    opts.DataLine = 3;
    T = readtable(file,opts);
    header = importdata(file,',',1);
    header = char(header);
    header = erase(header,'=meas');
    header = erase(header,'=calc');
    header = textscan(header,'%s','Delimiter',',')';
    header = header{:}';
    dif = width(header) - width(T.Properties.VariableNames);
    if dif > 0
        start = width(header)-(dif-1);
        slutt = width(header);
        toDelete = [];
        ctr = 1;
        for i = start:slutt
            toDelete(ctr) = i;
            ctr=ctr+1;
        end
        header(:,toDelete)=[];
    end
    T.Properties.VariableNames = header;
    [rows, cols] = size(T);
    toDelete = [];
    c = 1;
    for i = 1:cols
        for j = 1:rows
            if iscell(T(j,i).Variables)
                toDelete(c) = i;
                c=c+1;
                break
            elseif isnumeric(T(j,i).Variables)
                break
            end
        end
    end
    T(:,toDelete) = [];
    labels = T.Properties.VariableNames;
    Data = T.Variables;
    for i = 1:length(labels)
       c = Data(:,i);
       slutt = NaN(sum(isnan(c)),1);
       verdier = c(~isnan(c));
       fixed = [verdier;slutt];
       key = char(labels(i));
       d(1).(key) = fixed;
    end
end