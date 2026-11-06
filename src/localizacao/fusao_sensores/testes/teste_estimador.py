from pathlib import Path
import yaml

def teste_funde_medicoes_e_nao_referencia():
    p=yaml.safe_load((Path(__file__).resolve().parents[1]/'configuracao/estimador.yaml').read_text())['estimador_local']['ros__parameters']
    assert p['odom0']=='/odometria/rodas' and p['imu0']=='/imu/data_raw'
    assert len(p['odom0_config'])==len(p['imu0_config'])==15
    assert [i for i,v in enumerate(p['odom0_config']) if v]==[6,7]
    assert [i for i,v in enumerate(p['imu0_config']) if v]==[11]
    assert p['base_link_frame']=='base_footprint' and p['world_frame']=='odom'
    assert p['publish_tf'] and p['two_d_mode'] and p['use_sim_time']
    assert 'simulacao/referencia' not in str(p)
