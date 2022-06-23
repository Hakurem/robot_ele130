function [] = SaveMyFigure(fig_handle,name)

% SaveMyFigure, lagrer .fig og .pdf av gjeldende figur
% Klikk p? den figuren du vil lagre, og bruk funksjonen slik: 
% 
%   SaveMyFigure(gcf,'figurename')
% 
% hvor 'figurename' er et beskrivende filnavn for figuren.


% Ved lagring til vektorgrafikk pdf
% m? figurst?rrelsen settes. Dette trengs ikke for bitmap
fig_handle.PaperPositionMode = 'auto';
figure_pos = fig_handle.PaperPosition;
fig_handle.PaperSize = [figure_pos(3) figure_pos(4)];

% lagre 2 varianter, en .fig slik at du kan endre p? figuren 
% senere, og en .pdf for rapport
figurename_1 = [name,'.fig'];
figurename_2 = [name,'.pdf'];

if ~exist(figurename_1)
    savefig(figurename_1)
    print('-dpdf','-painters','-bestfit',figurename_2)
else
    TekstStreng = ['Filen ''',figurename_1,...
        ''' finnes fra f?r. Overskrive?'];
    svar=questdlg(TekstStreng,'Advarsel','Ja','Nei','Nei');
    switch svar
        case 'Ja'
        savefig(figurename_1)
        print('-dpdf','-painters','-bestfit',figurename_2)
        case 'Nei'
            return
    end
end

end

