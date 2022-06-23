%% Matlabfil for plotting av data fra Pythonprosjekt
clear all
close all

%% Navn: datafil (offline eller online)
filename = 'P0X_BeskrivendeTekst_Y.txt';
d = SortData(filename);

%% Legg inn verdiene dine (punktum norasjon med "d")
figure(1)
set(0,'defaultTextInterpreter','latex');
set(0,'defaultAxesFontSize',14)
set(gcf,'Position',[100 200 800 700])

subplot(3,4,1);
plot(d.Tid,d.W_,'b','LineWidth',1)
title('keyboard press W')
xlabel('Tid [sek]')
ylabel('State')
grid on
hold on

subplot(3,4,2);
plot(d.Tid,d.A_,'r','LineWidth',1)
title('keyboard press A')
xlabel('Tid [sek]')
ylabel('State')
grid on
hold on

subplot(3,4,3);
plot(d.Tid,d.S_,'g','LineWidth',1)
title('keyboard press S')
xlabel('Tid [sek]')
ylabel('State')
grid on
hold on

subplot(3,4,4);
plot(d.Tid,d.W_,'m','LineWidth',1)
title('keyboard press D')
xlabel('Tid [sek]')
ylabel('State')
grid on
hold on

% Motorpådrag
subplot(3,4,5);
plot(d.Tid,d.PowerA,'b','LineWidth',1)
title('PowerA')
xlabel('Tid [sek]')
ylabel('% pådrag')
grid on
hold on

subplot(3,4,6);
plot(d.Tid,d.PowerB,'r','LineWidth',1)
title('PowerB')
xlabel('Tid [sek]')
ylabel('% pådrag')
grid on
hold on

subplot(3,4,7);
plot(d.Tid,d.PowerC,'g','LineWidth',1)
title('PowerC')
xlabel('Tid [sek]')
ylabel('% pådrag')
grid on
hold on

subplot(3,4,8);
plot(d.Tid,d.PowerD,'m','LineWidth',1)
title('PowerD')
xlabel('Tid [sek]')
ylabel('% pådrag')
grid on
hold on



subplot(3,4,11);
plot(d.Tid,d.Ts,'r','LineWidth',1)
title('Ts')
xlabel('Tid [sek]')
ylabel('tidsskritt')
grid on
hold on


