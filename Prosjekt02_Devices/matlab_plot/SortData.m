function [d] = SortData(file)
    opts = detectImportOptions(file);
    opts.DataLines = 3;
    opts.VariableNamesLine = 1;
    meta_T = readtable(file,opts);
    T = meta_T;
    [rows, cols] = size(meta_T);
    for i = 1:cols
        for j = 1:rows
            if iscell(meta_T(j,i).Variables)
               T(:,i) = [];
               break
            end
        end
    end
    labels = T.Properties.VariableNames;
    Data = T.Variables;
    for i = 1:length(labels)
       c = Data(:,i);
       slutt = NaN(sum(isnan(c)),1);
       verdier = c(~isnan(c));
       fixed = [verdier;slutt];
       key = erase(char(labels(i)),"_meas"); 
       key = erase(key,"_calc");
       d(1).(key) = fixed;
    end
end