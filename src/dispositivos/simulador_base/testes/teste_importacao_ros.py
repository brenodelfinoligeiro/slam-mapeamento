"""Smoke real no Jazzy; fora de ROS só esta verificação é ignorada."""
import importlib
import pytest

def teste_adaptador_importa_no_ros():
    pytest.importorskip('rclpy')
    modulo=importlib.import_module('simulador_base_nos.no_simulador')
    assert callable(modulo.main)
