from pathlib import Path
import sys,importlib
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def teclado():return importlib.import_module('teleoperacao.modelo').EstadoTeclado(prazo=.4)

def teste_teclas_parada_e_saida():
    t=teclado();t.receber('w',10.)
    assert t.velocidade(10.1)[0]>0
    t.receber('s',10.2);assert t.velocidade(10.2)[0]<0
    t.receber('a',10.3);assert t.velocidade(10.3)[1]>0
    t.receber('d',10.4);assert t.velocidade(10.4)[1]<0
    t.receber(' ',10.5);assert t.velocidade(10.5)==(0.,0.)
    t.receber('q',10.6);assert t.sair and t.velocidade(10.6)==(0.,0.)

def teste_solta_tecla_e_entrada_desconhecida_param():
    t=teclado();t.receber('w',1.);assert t.velocidade(1.5)==(0.,0.)
    t.receber('w',2.);t.receber('?',2.1);assert t.velocidade(2.1)==(0.,0.)
