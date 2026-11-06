"""Validação estrutural de TwistStamped sem importar ROS."""
import math

def extrair_comando(mensagem):
    if mensagem.header.frame_id not in ('','base_footprint'):raise ValueError('Comando deve estar no corpo do robô')
    marca=mensagem.header.stamp
    if marca.sec<0 or not 0<=marca.nanosec<1000000000:raise ValueError('Carimbo inválido')
    l,a=mensagem.twist.linear,mensagem.twist.angular
    if not all(math.isfinite(v) for v in (l.x,l.y,l.z,a.x,a.y,a.z)):raise ValueError('Comando não finito')
    if any(abs(v)>1e-12 for v in (l.y,l.z,a.x,a.y)):raise ValueError('Comando não planar')
    return l.x,a.z,marca.sec+marca.nanosec*1e-9
