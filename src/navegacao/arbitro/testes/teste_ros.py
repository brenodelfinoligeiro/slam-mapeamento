import pytest
pytest.importorskip('rclpy')

def teste_importa_no_ros_e_interfaces_instaladas():
    from arbitro.no import NoArbitro
    from std_srvs.srv import SetBool,Trigger
    assert callable(NoArbitro) and SetBool.Request(data=True).data is True
    assert hasattr(Trigger.Response(),'success')
