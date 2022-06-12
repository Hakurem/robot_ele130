
%% Matlabfil for å plotting av data fra Pythonprosjekt
clear all
close all
CalcOffline = readtable('CalcOffline.txt');

%% Manipulasjon med struct og fiksing av lister
%Fikser listene importert fra datafilen så vi får NaN på slutten
labels = CalcOffline.Properties.VariableNames;
Data = CalcOffline.Variables;
for i = 1:length(labels)
   c = Data(:,i);
   slutt = NaN(sum(isnan(c)),1);
   verdier = c(~isnan(c));
   fixed = [verdier;slutt];
   key = char(labels(i));
   d(1).(key) = fixed;
end
%% Legg inn verdiene dine
figure(1)
set(0,'defaultTextInterpreter','latex');
set(0,'defaultAxesFontSize',14)
set(gcf,'Position',[100 200 800 700])

subplot(2,2,1);
plot(d.Tid,d.Ts,'b','LineWidth',1)
title('Ts')
xlabel('Tid [sek]')
ylabel('s')
grid on


subplot(2,2,2);
plot(d.Tid,d.s,'b','LineWidth',1)
xlabel('Tid [sek]')
grid on
hold on

subplot(2,2,2);
plot(d.Tid,d.s_IIR,'r','LineWidth',1)
title('Avstand vs Avstand_IIR')
xlabel('Tid [sek]')
ylabel('m')
grid on
legend('s','s\_IIR')


subplot(2,2,3);
plot(d.Tid,d.v,'b','LineWidth',1)
xlabel('Tid [sek]')
grid on
hold on

subplot(2,2,3);
plot(d.Tid,d.v_IIR,'r','LineWidth',1)
title('Fart vs Fart_IIR')
xlabel('Tid [sek]')
ylabel('m/s')
grid on
legend('v','v\_IIR')


subplot(2,2,4);
plot(d.Tid,d.a,'b','LineWidth',1)
xlabel('Tid [sek]')
grid on
hold on

subplot(2,2,4);
plot(d.Tid,d.a_IIR,'r','LineWidth',1)
title('Akselerasjon vs Akselerasjon_IIR')
xlabel('Tid [sek]')
ylabel('m/s^2')
grid on
legend('a','a\_IIR')


