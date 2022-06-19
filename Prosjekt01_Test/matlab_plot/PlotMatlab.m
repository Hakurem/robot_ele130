%% Matlabfil for å plotting av data fra Pythonprosjekt
clear all
close all

%% Navn på datafilen fra python
filename = 'Offline_P0X_BeskrivendeTekst_Y.txt';


%% Manipulasjon med struct og fiksing av lister
%Fikser listene importert fra datafilen så vi får NaN på slutten
file = strcat( "../Data/",filename);
opts = detectImportOptions(file);
opts.DataLines = 3;
opts.VariableNamesLine = 1;
T = readtable(file,opts);
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

%% Legg inn verdiene dine (punktum norasjon med "d")
figure(1)
set(0,'defaultTextInterpreter','latex');
set(0,'defaultAxesFontSize',14)
set(gcf,'Position',[100 200 800 700])

subplot(2,2,1);
plot(d.Tid,d.Flow,'b','LineWidth',1)
title('Calculations of flow')
xlabel('Tid [sek]')
ylabel('Flow')
grid on


subplot(2,2,2);
plot(d.Tid,d.Euler,'b','LineWidth',1)
title('Calculations of Euler')
xlabel('Tid [sek]')
ylabel('Volum')
grid on
hold on


subplot(2,2,3);
plot(d.Tid,d.Ts,'b','LineWidth',1)
title('Time-step')
xlabel('Tid [sek]')
ylabel('time-step')
grid on
hold on


